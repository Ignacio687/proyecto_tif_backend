- **Point 1 - Fix consistant error on skill calls made by the second call, it should whait for the response if the response is a question, then call the skill when the user agrees to do it.**
    """
        [2026-02-17T08:10:04.128506-0300] INFO - Sending user prompt to Gemini: el numero es 2645018867
        [2026-02-17T08:10:06.750019-0300] DEBUG - Parsed JSON response: {'server_reply': 'Entendido, Ignacio. He actualizado el número de tu papá. ¿Quieres que lo llame ahora o prefieres que lo guarde con algún nombre específico?', 'app_params': [{'question': True}], 'interaction_params': {'relevant_for_context': True, 'context_priority': 85, 'relevant_info': 'El número de teléfono actualizado del papá de Ignacio es 2645018867'}, 'context_updates': [{'entry_number': 2, 'new_priority': 0}]}
        [2026-02-17T08:10:07.746333-0300] DEBUG - Second call returned skills: [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'data': '{"contact_phone": "2645018867"}'}}]
        [2026-02-17T08:10:07.746463-0300] INFO - GEMINI SERVICE RETURNING: {'server_reply': 'Entendido, Ignacio. He actualizado el número de tu papá. ¿Quieres que lo llame ahora o prefieres que lo guarde con algún nombre específico?', 'app_params': [{'question': True}], 'interaction_params': {'relevant_for_context': True, 'context_priority': 85, 'relevant_info': 'El número de teléfono actualizado del papá de Ignacio es 2645018867'}, 'context_updates': [{'entry_number': 2, 'new_priority': 0}], 'skills': [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'data': '{"contact_phone": "2645018867"}'}}]}
        [2026-02-17T08:10:07.747980-0300] DEBUG - Saved conversation for user 6993e5800a7b9993a45b65ac
        [2026-02-17T08:10:07.750800-0300] DEBUG - Updated key context priority for user 6993e5800a7b9993a45b65ac, context 699449a6d52d39b5496f4f78
        [2026-02-17T08:10:07.750935-0300] DEBUG - Updated key context priority for user 6993e5800a7b9993a45b65ac, entry 2 (ID: 699449a6d52d39b5496f4f78) to priority 0
        [2026-02-17T08:10:07.753288-0300] DEBUG - Saved new key context for user 6993e5800a7b9993a45b65ac: El número de teléfono actualizado del papá de Igna...
        [2026-02-17T08:10:07.753393-0300] DEBUG - Saved current interaction key context for user 6993e5800a7b9993a45b65ac: El número de teléfono actualizado del papá de Igna...
        [2026-02-17T08:10:07.755437-0300] DEBUG - Cleaned up 1 zero-priority contexts for user 6993e5800a7b9993a45b65ac
        [2026-02-17T08:10:07.755568-0300] INFO - Response sent for user 6993e5800a7b9993a45b65ac: Entendido, Ignacio. He actualizado el número de tu papá. ¿Quieres que lo llame ahora o prefieres que...
        INFO:     127.0.0.1:47506 - "POST /api/v1/assistant HTTP/1.1" 200 OK

        ---

        INFO:     127.0.0.1:57718 - "POST /api/v1/assistant HTTP/1.1" 200 OK
        [2026-02-18T11:09:52.631792-0300] DEBUG - Retrieved 8 conversations for context (4359 chars)
        [2026-02-18T11:09:52.634277-0300] DEBUG - Retrieved 3 key contexts for user 6995b7353065cc806b0c57bb (349 chars)
        [2026-02-18T11:09:52.637277-0300] DEBUG - Total optimized context length: 5135 characters (~1283 tokens)
        [2026-02-18T11:09:52.637589-0300] DEBUG - Context stats: {'key_context_entries': 3, 'key_context_chars': 343, 'conversation_entries': 8, 'conversation_chars': 4215, 'total_dynamic_chars': 4558, 'within_limits': {'key_context': True, 'conversations': True, 'total': True}}
        [2026-02-18T11:09:52.637710-0300] DEBUG - Variable context for Gemini call: time_and_location=%s | key_context_data(%d)=%s | context_conversations(%d)=%s | context_data_text=%s
        [2026-02-18T11:09:52.639005-0300] INFO - Sending user prompt to Gemini: podrias llamar a mi hermana Luna
        [2026-02-18T11:09:58.184827-0300] DEBUG - Parsed JSON response: {'server_reply': 'Claro, Ignacio. Enseguida llamo a tu hermana Luna.', 'app_params': [{'question': False}], 'interaction_params': {'relevant_for_context': True, 'context_priority': 70, 'relevant_info': 'La hermana del usuario se llama Luna'}, 'context_updates': []}
        [2026-02-18T11:09:59.407894-0300] DEBUG - Second call returned skills: [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'contact_name': 'Luna'}}]
        [2026-02-18T11:09:59.408017-0300] INFO - GEMINI SERVICE RETURNING: {'server_reply': 'Claro, Ignacio. Enseguida llamo a tu hermana Luna.', 'app_params': [{'question': False}], 'interaction_params': {'relevant_for_context': True, 'context_priority': 70, 'relevant_info': 'La hermana del usuario se llama Luna'}, 'context_updates': [], 'skills': [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'contact_name': 'Luna'}}]}
        [2026-02-18T11:09:59.411019-0300] DEBUG - Saved conversation for user 6995b7353065cc806b0c57bb
        [2026-02-18T11:09:59.414227-0300] DEBUG - Saved new key context for user 6995b7353065cc806b0c57bb: La hermana del usuario se llama Luna...
        [2026-02-18T11:09:59.414561-0300] DEBUG - Saved current interaction key context for user 6995b7353065cc806b0c57bb: La hermana del usuario se llama Luna...
        [2026-02-18T11:09:59.415778-0300] DEBUG - No zero-priority contexts to clean up for user 6995b7353065cc806b0c57bb
        [2026-02-18T11:09:59.416027-0300] INFO - Response sent for user 6995b7353065cc806b0c57bb: Claro, Ignacio. Enseguida llamo a tu hermana Luna....
        INFO:     127.0.0.1:35902 - "POST /api/v1/assistant HTTP/1.1" 200 OK
        INFO:     127.0.0.1:47242 - "POST /api/v1/auth/verify-token HTTP/1.1" 200 OK
        INFO:     127.0.0.1:47242 - "GET /api/v1/conversations?page=1&page_size=10 HTTP/1.1" 200 OK
        [2026-02-18T11:10:20.871415-0300] DEBUG - Retrieved 9 conversations for context (4459 chars)
        [2026-02-18T11:10:20.873278-0300] DEBUG - Retrieved 4 key contexts for user 6995b7353065cc806b0c57bb (387 chars)
        [2026-02-18T11:10:20.875581-0300] DEBUG - Total optimized context length: 5341 characters (~1335 tokens)
        [2026-02-18T11:10:20.875845-0300] DEBUG - Context stats: {'key_context_entries': 4, 'key_context_chars': 379, 'conversation_entries': 9, 'conversation_chars': 4297, 'total_dynamic_chars': 4676, 'within_limits': {'key_context': True, 'conversations': True, 'total': True}}
        [2026-02-18T11:10:20.875995-0300] DEBUG - Variable context for Gemini call: time_and_location=%s | key_context_data(%d)=%s | context_conversations(%d)=%s | context_data_text=%s
        [2026-02-18T11:10:20.877120-0300] INFO - Sending user prompt to Gemini: ahora a pedro
        [2026-02-18T11:10:22.790028-0300] DEBUG - Parsed JSON response: {'server_reply': 'Entendido, Ignacio. ¿Querés que llame a Pedro o preferís que le envíe un mensaje?', 'app_params': [{'question': True}], 'interaction_params': {'relevant_for_context': False, 'context_priority': 0, 'relevant_info': ''}}
        [2026-02-18T11:10:24.365764-0300] DEBUG - Second call returned skills: [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'contact_name': 'Luna'}}]
        [2026-02-18T11:10:24.365915-0300] INFO - GEMINI SERVICE RETURNING: {'server_reply': 'Entendido, Ignacio. ¿Querés que llame a Pedro o preferís que le envíe un mensaje?', 'app_params': [{'question': True}], 'interaction_params': {'relevant_for_context': False, 'context_priority': 0, 'relevant_info': ''}, 'skills': [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'contact_name': 'Luna'}}]}
        [2026-02-18T11:10:24.368757-0300] DEBUG - Saved conversation for user 6995b7353065cc806b0c57bb
        [2026-02-18T11:10:24.370121-0300] DEBUG - No zero-priority contexts to clean up for user 6995b7353065cc806b0c57bb
        [2026-02-18T11:10:24.370300-0300] INFO - Response sent for user 6995b7353065cc806b0c57bb: Entendido, Ignacio. ¿Querés que llame a Pedro o preferís que le envíe un mensaje?...
        INFO:     127.0.0.1:42434 - "POST /api/v1/assistant HTTP/1.1" 200 OK
        [2026-02-18T11:10:40.124608-0300] DEBUG - Retrieved 10 conversations for context (4571 chars)
        [2026-02-18T11:10:40.126633-0300] DEBUG - Retrieved 4 key contexts for user 6995b7353065cc806b0c57bb (387 chars)
        [2026-02-18T11:10:40.128842-0300] DEBUG - Total optimized context length: 5481 characters (~1370 tokens)
        [2026-02-18T11:10:40.128985-0300] DEBUG - Context stats: {'key_context_entries': 4, 'key_context_chars': 379, 'conversation_entries': 10, 'conversation_chars': 4391, 'total_dynamic_chars': 4770, 'within_limits': {'key_context': True, 'conversations': True, 'total': True}}
        [2026-02-18T11:10:40.129092-0300] DEBUG - Variable context for Gemini call: time_and_location=%s | key_context_data(%d)=%s | context_conversations(%d)=%s | context_data_text=%s
        [2026-02-18T11:10:40.129885-0300] INFO - Sending user prompt to Gemini: llama
        [2026-02-18T11:10:42.662023-0300] DEBUG - Parsed JSON response: {'server_reply': 'Entendido, Ignacio. ¿Querés que llame a Pedro?', 'app_params': [{'question': True}], 'interaction_params': {'relevant_for_context': False, 'context_priority': 0, 'relevant_info': ''}}
        [2026-02-18T11:10:43.498765-0300] DEBUG - Second call returned skills: [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'contact_name': 'Pedro'}}]
        [2026-02-18T11:10:43.498924-0300] INFO - GEMINI SERVICE RETURNING: {'server_reply': 'Entendido, Ignacio. ¿Querés que llame a Pedro?', 'app_params': [{'question': True}], 'interaction_params': {'relevant_for_context': False, 'context_priority': 0, 'relevant_info': ''}, 'skills': [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'contact_name': 'Pedro'}}]}
        [2026-02-18T11:10:43.500713-0300] DEBUG - Saved conversation for user 6995b7353065cc806b0c57bb
        [2026-02-18T11:10:43.501945-0300] DEBUG - No zero-priority contexts to clean up for user 6995b7353065cc806b0c57bb
        [2026-02-18T11:10:43.502122-0300] INFO - Response sent for user 6995b7353065cc806b0c57bb: Entendido, Ignacio. ¿Querés que llame a Pedro?...
    """

- **Point 2 – Long-term memory: conversation summarization + semantic retrieval (background job)**

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

- **Point 3 – Use new gemini 2.5 flash preview tts for online voice generation, send voice to the app**
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

- **Point 4 – Erradicate this behaviors:**

    "server_reply": "Excelente, Ignacio. ¿Te gustaría que busque más información sobre algún tema en particular de las noticias o necesitás ayuda con otra cosa?" That follow up question should not be asked, the action was already done.0

---

- **Point 5 – Retry logic for 503 in Gemini client** *(to consider)*

  Consider adding retry logic for **503 (Service Unavailable)** responses from the Gemini API (e.g. deadline expired, model overloaded) so transient failures are retried and the client is more resilient.

---

- **Point 6 – Play YouTube video skill: user asks to play a video, Gemini finds the URL, app opens it**

  **Goal:** The user can ask the assistant to play a YouTube video (e.g. "poné el último video de MrBeast", "quiero ver recetas de milanesas"). The server uses Gemini with Google Search grounding to find the real video URL, returns it as a skill action, and the Android app opens it via an `ACTION_VIEW` intent in the YouTube app.

  **Behavior:**
  1. **Server side (backend):**
     - Add a `PlayYouTubeVideoSkill` to the skill schema (name, action: `play_youtube_video`, params: `video_url`, optionally `video_title`).
     - In the Gemini prompt/instructions, tell the model that when the user asks to play/watch a video, it should use Google Search grounding to find the actual YouTube URL and return it via the skill.
     - The second call (skill extraction) should output the skill with the resolved URL.
  2. **Android side (app):**
     - Implement `PlayYouTubeVideoSkill` that receives `video_url` from the server response.
     - Fire an `ACTION_VIEW` intent with the URL — Android will open it in the YouTube app if installed, or in the browser otherwise.
  3. **Considerations:**
     - Gemini must have **Google Search tool enabled** for this to work reliably (otherwise URLs may be hallucinated).
     - Fallback: if no URL is found, the server should reply saying it couldn't find the video instead of returning a skill with a bad URL.
     - The skill params schema should include `video_url` (required) and `video_title` (optional, for the assistant to say "I'm playing X").
