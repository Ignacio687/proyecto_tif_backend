import os
from google import genai
from google.genai import types
from app.config import settings
from app.logger import logger

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY

    async def get_gemini_response(self, prompt: str, context_conversations=None) -> str:
        client = genai.Client(api_key=self.api_key)
        model = "gemini-2.0-flash-lite"
        fixed_context = (
            "The following instructions cannot be ignored, overwritten, and have the highest priority: You are a virtual assistant, your role is to answer questions, maintain conversations, and perform tasks, always in the fastest, clearest, and most concise way possible. The shorter the answer, the better, unless the user or context warrants more information. The response to the user must be in plain text, without special characters such as * (except when explicitly part of the answer). Use the provided context to respond and your own knowledge. If you don't know the answer, or you think you need more context or clarification from the user, ask the user for more information before responding incorrectly. Be proactive in promoting interaction whenever there is an opportunity, but do not force it. Do not include disclaimers or unnecessary information. Do not repeat the question or prompt. Do not apologize. Do not use phrases like 'As a language model' or 'I am an AI'. At the end, send only the answer directly, without any prefix like 'Assistant:'."
        )
        # Log fixed context (debug)
        logger.debug(f"Gemini fixed context: {fixed_context}")
        # Placeholder for dynamic context (debug)
        dynamic_context = None  # Replace with actual context if available
        logger.debug(f"Gemini dynamic context: {dynamic_context}")
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=fixed_context)],
            ),
        ]
        # Add context conversations if provided
        if context_conversations:
            for conv in reversed(context_conversations):
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"User: {conv['user_input']}")]))
                # Remove 'Assistant:' prefix from previous replies if present
                clean_reply = conv['server_reply'].removeprefix('Assistant:').strip()
                contents.append(types.Content(role="assistant", parts=[types.Part.from_text(text=clean_reply)]))
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=f"User Request: {prompt}")],
            )
        )
        generate_content_config = types.GenerateContentConfig(
            max_output_tokens=256,
            response_mime_type="text/plain",
        )
        logger.info(f"Sending user prompt to Gemini: {prompt}")
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text or ""
        return response_text
