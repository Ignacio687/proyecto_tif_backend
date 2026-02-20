- **Point 1 - SOLVED.** ~~Fix this behavior, it seems it thought that I was talking about a saved key context, and not the last message or response as it should be. The second call did it right because it only sees the last two conversations I think~~

    INFO:     127.0.0.1:38970 - "POST /api/v1/auth/refresh HTTP/1.1" 200 OK
    [2026-02-20T13:48:11.593598-0300] DEBUG - Retrieved 20 conversations for context (4769 chars)
    [2026-02-20T13:48:11.595495-0300] DEBUG - Retrieved 11 key contexts for user 697c45235a20de239339e69c (1218 chars)
    [2026-02-20T13:48:11.598061-0300] DEBUG - Conversation history truncated at 4531 characters
    [2026-02-20T13:48:11.598309-0300] DEBUG - Total optimized context length: 6368 characters (~1592 tokens)
    [2026-02-20T13:48:11.598459-0300] DEBUG - Context stats: {'key_context_entries': 11, 'key_context_chars': 1196, 'conversation_entries': 20, 'conversation_chars': 4409, 'total_dynamic_chars': 5605, 'within_limits': {'key_context': True, 'conversations': True, 'total': True}}
    [2026-02-20T13:48:11.598569-0300] DEBUG - Gemini variable context (truncated):
    [2026-02-20T13:48:11.598654-0300] DEBUG -   time/location: Current date and time (user's local): Friday, 2026-02-20 13:48 -03 User timezone... (102 chars)
    [2026-02-20T13:48:11.598737-0300] DEBUG -   key_ctx[1]: La hermana del usuario se llama Luna
    [2026-02-20T13:48:11.598815-0300] DEBUG -   key_ctx[2]: Ignacio solicitó el número de atención al cliente ... (207 chars)
    [2026-02-20T13:48:11.598892-0300] DEBUG -   key_ctx[3]: Ignacio es el desarrollador de mis herramientas in... (57 chars)
    [2026-02-20T13:48:11.598985-0300] DEBUG -   key_ctx[4]: El usuario consultó por noticias actuales el 20 de... (207 chars)
    [2026-02-20T13:48:11.599068-0300] DEBUG -   key_ctx: ... +7 more
    [2026-02-20T13:48:11.599133-0300] DEBUG -   conv[1] user: a movistar, el numero que buscaste
    [2026-02-20T13:48:11.599205-0300] DEBUG -        assistant: Entendido, Ignacio. Estoy llamando al número ...
    [2026-02-20T13:48:11.599305-0300] DEBUG -   conv[2] user: llama
    [2026-02-20T13:48:11.599386-0300] DEBUG -        assistant: ¿A quién te gustaría que llame, Ignacio? Pued...
    [2026-02-20T13:48:11.599471-0300] DEBUG -   conv[3] user: puedes buscar el numero de telefono de atenci...
    [2026-02-20T13:48:11.599552-0300] DEBUG -        assistant: ¡Claro, Ignacio! Para atención al cliente de ...
    [2026-02-20T13:48:11.599634-0300] DEBUG -   conv: ... +17 more
    [2026-02-20T13:48:11.599718-0300] DEBUG -   context_data_text: RECENT CONVERSATION HISTORY: User: que puedes hacer? (at Friday, 2026-02-20 13:38 -03) Assistant: Puedo ayudarte con varias cosas, Ignacio. Puedo realizar llamadas, enviar mensajes de texto o WhatsApp, crear recordatorios para que no olvides nada importante y realizar búsquedas e... (6365 chars)
    [2026-02-20T13:48:11.601130-0300] INFO - Sending user prompt to Gemini: tengo un turno de medico el lunes a las 11, haceme acordar
    [2026-02-20T13:48:13.971226-0300] DEBUG - Parsed JSON response: {'server_reply': '¡Hecho, Ignacio! He creado un recordatorio para tu turno médico el lunes a las 11:00.', 'app_params': [{'question': False}], 'interaction_params': {'relevant_for_context': False, 'context_priority': 0, 'relevant_info': ''}}
    [2026-02-20T13:48:15.235767-0300] DEBUG - Second call returned skills: [{'name': 'CreateReminderSkill', 'action': 'create_reminder', 'params': {'title': 'Turno de médico', 'datetime': '2026-02-23 11:00:00-03:00'}}]
    [2026-02-20T13:48:15.235916-0300] INFO - GEMINI SERVICE RETURNING: {'server_reply': '¡Hecho, Ignacio! He creado un recordatorio para tu turno médico el lunes a las 11:00.', 'app_params': [{'question': False}], 'interaction_params': {'relevant_for_context': False, 'context_priority': 0, 'relevant_info': ''}, 'skills': [{'name': 'CreateReminderSkill', 'action': 'create_reminder', 'params': {'title': 'Turno de médico', 'datetime': '2026-02-23 11:00:00-03:00'}}]}
    [2026-02-20T13:48:15.237798-0300] DEBUG - Saved conversation for user 697c45235a20de239339e69c
    [2026-02-20T13:48:15.239094-0300] DEBUG - No zero-priority contexts to clean up for user 697c45235a20de239339e69c
    [2026-02-20T13:48:15.239276-0300] INFO - Response sent for user 697c45235a20de239339e69c: ¡Hecho, Ignacio! He creado un recordatorio para tu turno médico el lunes a las 11:00....
    INFO:     127.0.0.1:38970 - "POST /api/v1/assistant HTTP/1.1" 200 OK
    [2026-02-20T14:17:48.674661-0300] DEBUG - Retrieved 21 conversations for context (4930 chars)
    [2026-02-20T14:17:48.677105-0300] DEBUG - Retrieved 11 key contexts for user 697c45235a20de239339e69c (1218 chars)
    [2026-02-20T14:17:48.679599-0300] DEBUG - Conversation history truncated at 4531 characters
    [2026-02-20T14:17:48.679783-0300] DEBUG - Total optimized context length: 6368 characters (~1592 tokens)
    [2026-02-20T14:17:48.679862-0300] DEBUG - Context stats: {'key_context_entries': 11, 'key_context_chars': 1196, 'conversation_entries': 21, 'conversation_chars': 4552, 'total_dynamic_chars': 5748, 'within_limits': {'key_context': True, 'conversations': True, 'total': True}}
    [2026-02-20T14:17:48.679931-0300] DEBUG - Gemini variable context (truncated):
    [2026-02-20T14:17:48.679994-0300] DEBUG -   time/location: Current date and time (user's local): Friday, 2026-02-20 14:17 -03 User timezone... (102 chars)
    [2026-02-20T14:17:48.680052-0300] DEBUG -   key_ctx[1]: La hermana del usuario se llama Luna
    [2026-02-20T14:17:48.680089-0300] DEBUG -   key_ctx[2]: Ignacio solicitó el número de atención al cliente ... (207 chars)
    [2026-02-20T14:17:48.680133-0300] DEBUG -   key_ctx[3]: Ignacio es el desarrollador de mis herramientas in... (57 chars)
    [2026-02-20T14:17:48.680182-0300] DEBUG -   key_ctx[4]: El usuario consultó por noticias actuales el 20 de... (207 chars)
    [2026-02-20T14:17:48.680236-0300] DEBUG -   key_ctx: ... +7 more
    [2026-02-20T14:17:48.680301-0300] DEBUG -   conv[1] user: tengo un turno de medico el lunes a las 11, h...
    [2026-02-20T14:17:48.680359-0300] DEBUG -        assistant: ¡Hecho, Ignacio! He creado un recordatorio pa...
    [2026-02-20T14:17:48.680422-0300] DEBUG -   conv[2] user: a movistar, el numero que buscaste
    [2026-02-20T14:17:48.680487-0300] DEBUG -        assistant: Entendido, Ignacio. Estoy llamando al número ...
    [2026-02-20T14:17:48.680556-0300] DEBUG -   conv[3] user: llama
    [2026-02-20T14:17:48.680621-0300] DEBUG -        assistant: ¿A quién te gustaría que llame, Ignacio? Pued...
    [2026-02-20T14:17:48.680682-0300] DEBUG -   conv: ... +18 more
    [2026-02-20T14:17:48.680745-0300] DEBUG -   context_data_text: RECENT CONVERSATION HISTORY: User: que puedes hacer? (at Friday, 2026-02-20 13:38 -03) Assistant: Puedo ayudarte con varias cosas, Ignacio. Puedo realizar llamadas, enviar mensajes de texto o WhatsApp, crear recordatorios para que no olvides nada importante y realizar búsquedas e... (6365 chars)
    [2026-02-20T14:17:48.681550-0300] INFO - Sending user prompt to Gemini: podes guardarlo nuevamente, no se guardo

    [2026-02-20T14:17:51.332155-0300] DEBUG - Parsed JSON response: {'server_reply': '¡Claro, Ignacio! He vuelto a guardar que tu hermana se llama Luna en mi memoria para no olvidarlo.', 'app_params': [{'question': False}], 'interaction_params': {'relevant_for_context': True, 'context_priority': 95, 'relevant_info': 'La hermana del usuario se llama Luna'}, 'context_updates': [{'entry_number': 1, 'new_priority': 95}]}
    [2026-02-20T14:17:52.628630-0300] DEBUG - Second call returned skills: [{'name': 'CreateReminderSkill', 'action': 'create_reminder', 'params': {'title': 'Turno médico', 'datetime': '2026-02-23 11:00:00-03:00'}}]
    [2026-02-20T14:17:52.628767-0300] INFO - GEMINI SERVICE RETURNING: {'server_reply': '¡Claro, Ignacio! He vuelto a guardar que tu hermana se llama Luna en mi memoria para no olvidarlo.', 'app_params': [{'question': False}], 'interaction_params': {'relevant_for_context': True, 'context_priority': 95, 'relevant_info': 'La hermana del usuario se llama Luna'}, 'context_updates': [{'entry_number': 1, 'new_priority': 95}], 'skills': [{'name': 'CreateReminderSkill', 'action': 'create_reminder', 'params': {'title': 'Turno médico', 'datetime': '2026-02-23 11:00:00-03:00'}}]}
    [2026-02-20T14:17:52.631476-0300] DEBUG - Saved conversation for user 697c45235a20de239339e69c
    [2026-02-20T14:17:52.638556-0300] DEBUG - Updated key context priority for user 697c45235a20de239339e69c, context 6998652a9f3cd34829e88f55
    [2026-02-20T14:17:52.638691-0300] DEBUG - Updated key context priority for user 697c45235a20de239339e69c, entry 1 (ID: 6998652a9f3cd34829e88f55) to priority 95
    [2026-02-20T14:17:52.641103-0300] DEBUG - Refreshed existing key context timestamp for user 697c45235a20de239339e69c: La hermana del usuario se llama Luna...
    [2026-02-20T14:17:52.641218-0300] DEBUG - Saved current interaction key context for user 697c45235a20de239339e69c: La hermana del usuario se llama Luna...
    [2026-02-20T14:17:52.642222-0300] DEBUG - No zero-priority contexts to clean up for user 697c45235a20de239339e69c
    [2026-02-20T14:17:52.642405-0300] INFO - Response sent for user 697c45235a20de239339e69c: ¡Claro, Ignacio! He vuelto a guardar que tu hermana se llama Luna en mi memoria para no olvidarlo....


- **Point 2 - SOLVED.** ~~Second call ignores that the first call knows its luna and calls hermana instead~~

    INFO:     127.0.0.1:44608 - "GET /api/v1/conversations?page=1&page_size=10&timezone=America%2FBuenos_Aires HTTP/1.1" 200 OK
    [2026-02-20T16:11:16.417764-0300] DEBUG - Retrieved 22 conversations for context (4761 chars)
    [2026-02-20T16:11:16.420579-0300] DEBUG - Retrieved 11 key contexts for user 697c45235a20de239339e69c (1218 chars)
    [2026-02-20T16:11:16.423218-0300] DEBUG - Conversation history truncated at 4769 characters
    [2026-02-20T16:11:16.423568-0300] DEBUG - Total optimized context length: 6606 characters (~1651 tokens)
    [2026-02-20T16:11:16.423680-0300] DEBUG - Context stats: {'key_context_entries': 11, 'key_context_chars': 1196, 'conversation_entries': 22, 'conversation_chars': 4365, 'total_dynamic_chars': 5561, 'within_limits': {'key_context': True, 'conversations': True, 'total': True}}
    [2026-02-20T16:11:16.423758-0300] DEBUG - Gemini variable context (truncated):
    [2026-02-20T16:11:16.423818-0300] DEBUG -   time/location: Current date and time (user's local): Friday, 2026-02-20 16:11 -03 User timezone... (102 chars)
    [2026-02-20T16:11:16.423874-0300] DEBUG -   key_ctx[1]: La hermana del usuario se llama Luna
    [2026-02-20T16:11:16.423928-0300] DEBUG -   key_ctx[2]: Ignacio solicitó el número de atención al cliente ... (207 chars)
    [2026-02-20T16:11:16.423982-0300] DEBUG -   key_ctx[3]: Ignacio es el desarrollador de mis herramientas in... (57 chars)
    [2026-02-20T16:11:16.424034-0300] DEBUG -   key_ctx[4]: El usuario consultó por noticias actuales el 20 de... (207 chars)
    [2026-02-20T16:11:16.424086-0300] DEBUG -   key_ctx: ... +7 more
    [2026-02-20T16:11:16.424151-0300] DEBUG -   conv[1] user: tengo un examen el miercoles a las 9, haceme ...
    [2026-02-20T16:11:16.424216-0300] DEBUG -        assistant: Entendido, Ignacio. He creado un recordatorio...
    [2026-02-20T16:11:16.424292-0300] DEBUG -   conv[2] user: y tengo una juntada con unos amigos para juga...
    [2026-02-20T16:11:16.424397-0300] DEBUG -        assistant: Entendido, Ignacio. He creado un recordatorio...
    [2026-02-20T16:11:16.424473-0300] DEBUG -   conv[3] user: y tengo una reuinon el sabado a las 12
    [2026-02-20T16:11:16.424539-0300] DEBUG -        assistant: Entendido, Ignacio. He creado un recordatorio...
    [2026-02-20T16:11:16.424603-0300] DEBUG -   conv: ... +19 more
    [2026-02-20T16:11:16.424692-0300] DEBUG -   context_data_text: RECENT CONVERSATION HISTORY: User: y tengo una juntada con unos amigos para jugar al bowling el domigno a las 8 de la noche (at Friday, 2026-02-20 15:05 -03) Assistant: Entendido, Ignacio. He creado un recordatorio para tu juntada con amigos para jugar al bowling este domingo a l... (6603 chars)
    [2026-02-20T16:11:16.424935-0300] INFO - Full context sent to LLM written to: %s
    [2026-02-20T16:11:16.426264-0300] INFO - Sending user prompt to Gemini: llama a mi hermana
    [2026-02-20T16:11:19.077350-0300] DEBUG - Parsed JSON response: {'server_reply': '¡Claro, Ignacio! Estoy llamando a tu hermana Luna ahora mismo.', 'app_params': [{'question': False}], 'interaction_params': {'relevant_for_context': False, 'context_priority': 0, 'relevant_info': ''}}
    [2026-02-20T16:11:20.667415-0300] DEBUG - Second call returned skills: [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'contact_name': 'hermana'}}]
    [2026-02-20T16:11:20.667552-0300] INFO - GEMINI SERVICE RETURNING: {'server_reply': '¡Claro, Ignacio! Estoy llamando a tu hermana Luna ahora mismo.', 'app_params': [{'question': False}], 'interaction_params': {'relevant_for_context': False, 'context_priority': 0, 'relevant_info': ''}, 'skills': [{'name': 'CallContactSkill', 'action': 'call_contact', 'params': {'contact_name': 'hermana'}}]}
    [2026-02-20T16:11:20.669453-0300] DEBUG - Saved conversation for user 697c45235a20de239339e69c
    [2026-02-20T16:11:20.670613-0300] DEBUG - No zero-priority contexts to clean up for user 697c45235a20de239339e69c
    [2026-02-20T16:11:20.670887-0300] INFO - Response sent for user 697c45235a20de239339e69c: ¡Claro, Ignacio! Estoy llamando a tu hermana Luna ahora mismo....

- **Point 3 – Long-term memory: conversation summarization + semantic retrieval (background job)**

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

- **Point 4 – Use new gemini 2.5 flash preview tts for online voice generation, send voice to the app**
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
