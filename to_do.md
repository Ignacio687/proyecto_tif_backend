- **Point 1 – Skills via Function Calling (fix unreliable skill invocation)**

  **Problem:** The model is unreliable at calling skills. Integration tests show it often returns `skills: None` for clear call instructions ("Call John", "Ring my brother", etc.) and does not consistently trigger the Google Search tool for search-style prompts. The model is losing focus on the long system context: it has to follow a big JSON schema and a long list of skill descriptions in plain text, so it frequently omits or misuses the skills array.

  **Solution:** Two calls. First call generates the **user-facing reply** and only knows **which skills exist** (no schema detail). Second call, **only when a skill was selected**, generates the **skill schema** (function call + params) with minimal context to save tokens. Google Search stays as today (handled directly by the API).

  1. **First call:** Model generates the **user response** (the reply the user sees). It only knows the **list of available skills** (names / high-level), not the full function declarations or parameter schemas. It produces the natural-language reply; it may or may not indicate that a skill should be called (we do not rely on this).
  2. **Second call (always):** Run **always**, not only when the first call “selected” a skill. This call is **only for generating the skill schema** (exact function name + parameters). Inputs are **minimal**: user request, first call response, and system context—**not** the full first-call context, to save tokens. The second call decides from (user_req, first_reply, system context) whether any skill is needed and with what params; it outputs the structured function call(s) or nothing. Backend executes the skill(s) returned by the second call. **Why always:** If we only ran the second call when the first “selected” a skill, we would still depend on the first call behaving correctly. When it misbehaves (e.g. does not select a skill when the user said “Call John”), we would never run the second call and would not fix the problem. By always running the second call, the second call is the single source of truth for “what skills to run”; the first call can focus on the reply, and we still get correct skill invocation even when the first call omits or mis-signals.
  3. **No skill needed:** When the second call returns no function call, we simply return the first call’s response as-is.

  Reference: https://ai.google.dev/gemini-api/docs/function-calling?hl=es-419&example=meeting .

    """
        # To run this code you need to install the following dependencies:
        # pip install google-genai

        import base64
        import os
        from google import genai
        from google.genai import types


        def generate():
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.5-flash-lite"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="""INSERT_INPUT_HERE"""),
                    ],
                ),
            ]
            tools = [
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name="getWeather",
                            description="gets the weather for a requested city",
                            parameters=genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                properties = {
                                    "city": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                },
                            ),
                        ),
                    ])
            ]
            generate_content_config = types.GenerateContentConfig(
                max_output_tokens=2500,
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                tools=tools,
            )

            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                print(chunk.text if chunk.function_calls is None else chunk.function_calls[0])

        if __name__ == "__main__":
            generate()
    """

- **Point 2 –User location / timezone in requests**

  **Problem:** We register all timestamps as UTC without taking into account the user's location. This causes time-related confusion (e.g. "tomorrow", "in the morning") and limits context (e.g. we can't infer local time for weather).

  **Solution:** Ask the app to send the **current user location** (or timezone) with every request—e.g. timezone identifier (e.g. `America/Argentina/Buenos_Aires`), or lat/long so the backend can derive timezone. Use this to:
  1. **Store and interpret times correctly** (convert to user local time when needed, or store UTC + timezone).
  2. **Provide context to the model** (e.g. for weather search, "user is in Buenos Aires") and for any skill that benefits from location.

- **Point 3 – Current time and date in every request context**

  In the context of **every** request, always include the **current time and date** as seen by the user: either computed from the user's location/timezone (if sent) or UTC if not present. This allows the model to:
  - Compare "now" with timestamps and relative times mentioned in previous conversations (e.g. "we talked about this yesterday", "remind me next Monday").
  - Evaluate and reason about time and day in prior messages (e.g. "last week the user said…") with correct temporal grounding.

- **Point 4 – Setting a Reminder and Send a Message (when implemented in the app)**

  Implement these skills on the backend so they are available to the model once the app supports them:
  1. **Set reminder:** User can ask to be reminded at a specific time or after a delay (e.g. "remind me in 1 hour", "remind me tomorrow at 9"). Backend should schedule or store the reminder; use user timezone/location when provided for correct local time.
  2. **Send a message:** User can ask to send a message to a contact (e.g. "text María", "send a WhatsApp to my brother saying I'll be late"). Backend should expose the skill; actual delivery depends on app integration (push, in-app, or external service).

  Add them to the skill list and function-calling schema when the app is ready to handle the corresponding actions (notifications for reminders, messaging channel for send message).

---

- **Point 5 – Long-term memory: conversation summarization + semantic retrieval (background job)**

  **Goal:** Build a "long-term memory" from relevant conversations. When the user talks about a topic over many turns (e.g. 20 chats about a project), the system maintains a running summary; when the conversation shifts or the topic ends, the summary is finalized, a short headline is generated, and the headline is embedded (vector) and stored. Future user requests are compared (e.g. vector similarity) to these stored headlines so the model can be given the **most relevant past summarized conversations** as context, without sending full chat history.

  **Behavior:**
  1. **Relevance filter:** Only create/update summaries for **relevant** conversations. Ignore and do not summarize:
     - Transactional/skill-only (e.g. "call mom", "set a reminder").
     - Trivial or one-off (e.g. "Hello", "tell me a poem").
     Relevant = sustained, topic-focused dialogue (e.g. project work, planning, learning, personal context that recurs).
  2. **Running summary:** For a given "topic window" (e.g. same session or same detected topic), each new interaction can **add to** a running summary. The summary can be as long as needed. When the conversation **shifts** or is **no longer relevant** to that topic, the running summary is finalized.
     - **Flag to merge into old summary:** The model (or a separate step) must be able to **flag** when a new conversation is about an **existing** topic/summary. In that case, **add to** that old summary instead of creating a new one—so we **do not get fragmented summaries** talking about the same thing.
     - **Time frame in every summary:** Always **reference the time frame** when each conversation happened (e.g. "In late January 2025 the user…", "Conversation from 2025-01-15…"). Summaries must have clear temporal context so the model and the user can tell when things were discussed.
  3. **Headline + vector:** For each finalized summary, generate a **headline summary** (short, grammatical). Convert the headline to a **semantic/grammatical vector** (embedding) and store it (e.g. DB or vector store) with the full summary and metadata (user_id, time range, etc.).
  4. **Retrieval at request time:** When the user sends a new request, compare the request (or its embedding) to the stored headline vectors; fetch the **most relevant** conversation summaries (e.g. top-k by similarity). Use these summaries (plus existing key context) as context for the model so it has "long-term memory" without full history.
  5. **Latency:** All of this (relevance decision, summarization, headline, embedding, storage) and optionally part of the "first call" context preparation (e.g. which summaries to fetch) should be handled by a **third call that runs as a job after the response is sent to the user**. So: user request → first call (reply) + second call (skills) → **response sent** → **background job** runs (summarization, embeddings, storage; and/or precomputing context for next time). No extra latency for the user.

  **Design notes:**
  - Summarization can be done by a separate Gemini call (or dedicated model) in the job: input = conversation slice (and optionally candidate existing summaries for matching), output = updated running summary + "is_final" or "topic_shift" signal + **"merge_into_summary_id"** (or similar) when the new conversation is about an existing topic—so we append to that summary instead of creating a new one.
  - Every summary segment must **include time frame** (e.g. date range or "late Jan 2025"); the model producing the summary should be instructed to always phrase additions with temporal context.
  - Embeddings: use an embedding API (e.g. Gemini embedding or another provider) for the headline; store vectors in MongoDB (vector search) or a dedicated vector DB.
  - "Relevance" can be a small classifier or heuristic (e.g. no skill invoked, multiple turns, model says "relevant_for_context" or similar) so we don’t summarize every chat.

---

- **Point 6 – Use new gemini 2.5 flash preview tts for online voice genration, send voice to the app**
    """
        # To run this code you need to install the following dependencies:
        # pip install google-genai

        import base64
        import mimetypes
        import os
        import re
        import struct
        from google import genai
        from google.genai import types


        def save_binary_file(file_name, data):
            f = open(file_name, "wb")
            f.write(data)
            f.close()
            print(f"File saved to to: {file_name}")


        def generate():
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.5-flash-preview-tts"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="""Read aloud in a warm and friendly tone: 
        Hello! how are you?"""),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                response_modalities=[
                    "audio",
                ],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"
                        )
                    )
                ),
            )

            file_index = 0
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                    file_name = f"ENTER_FILE_NAME_{file_index}"
                    file_index += 1
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)
                    if file_extension is None:
                        file_extension = ".wav"
                        data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
                    save_binary_file(f"{file_name}{file_extension}", data_buffer)
                else:
                    print(chunk.text)

        def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
            """Generates a WAV file header for the given audio data and parameters.

            Args:
                audio_data: The raw audio data as a bytes object.
                mime_type: Mime type of the audio data.

            Returns:
                A bytes object representing the WAV file header.
            """
            parameters = parse_audio_mime_type(mime_type)
            bits_per_sample = parameters["bits_per_sample"]
            sample_rate = parameters["rate"]
            num_channels = 1
            data_size = len(audio_data)
            bytes_per_sample = bits_per_sample // 8
            block_align = num_channels * bytes_per_sample
            byte_rate = sample_rate * block_align
            chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

            # http://soundfile.sapp.org/doc/WaveFormat/

            header = struct.pack(
                "<4sI4s4sIHHIIHH4sI",
                b"RIFF",          # ChunkID
                chunk_size,       # ChunkSize (total file size - 8 bytes)
                b"WAVE",          # Format
                b"fmt ",          # Subchunk1ID
                16,               # Subchunk1Size (16 for PCM)
                1,                # AudioFormat (1 for PCM)
                num_channels,     # NumChannels
                sample_rate,      # SampleRate
                byte_rate,        # ByteRate
                block_align,      # BlockAlign
                bits_per_sample,  # BitsPerSample
                b"data",          # Subchunk2ID
                data_size         # Subchunk2Size (size of audio data)
            )
            return header + audio_data

        def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
            """Parses bits per sample and rate from an audio MIME type string.

            Assumes bits per sample is encoded like "L16" and rate as "rate=xxxxx".

            Args:
                mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

            Returns:
                A dictionary with "bits_per_sample" and "rate" keys. Values will be
                integers if found, otherwise None.
            """
            bits_per_sample = 16
            rate = 24000

            # Extract rate from parameters
            parts = mime_type.split(";")
            for param in parts: # Skip the main type part
                param = param.strip()
                if param.lower().startswith("rate="):
                    try:
                        rate_str = param.split("=", 1)[1]
                        rate = int(rate_str)
                    except (ValueError, IndexError):
                        # Handle cases like "rate=" with no value or non-integer value
                        pass # Keep rate as default
                elif param.startswith("audio/L"):
                    try:
                        bits_per_sample = int(param.split("L", 1)[1])
                    except (ValueError, IndexError):
                        pass # Keep bits_per_sample as default if conversion fails

            return {"bits_per_sample": bits_per_sample, "rate": rate}


        if __name__ == "__main__":
            generate()
    """

---