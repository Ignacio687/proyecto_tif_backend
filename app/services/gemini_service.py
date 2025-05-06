import os
from google import genai
from google.genai import types
from app.config import settings
from app.logger import logger

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY

    async def get_gemini_response(self, prompt: str) -> str:
        client = genai.Client(api_key=self.api_key)
        model = "gemini-2.0-flash-lite"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            max_output_tokens=256,
            response_mime_type="text/plain",
        )
        logger.info(f"Sending prompt to Gemini: {prompt}")
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text or ""
        return response_text
