"""
Gemini AI service implementation
"""
import json
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
from app.config import settings
from app.logger import logger
from app.services.interfaces import GeminiServiceInterface


class GeminiService(GeminiServiceInterface):
    """Service for interacting with Gemini AI"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash-lite"



    async def get_gemini_response(self, prompt: str, key_context_data: Optional[List[Dict[str, Any]]] = None, 
                                last_conversations: Optional[List[Dict[str, Any]]] = None, 
                                context_conversations: Optional[List[Dict[str, Any]]] = None, 
                                max_items: int = 10) -> Dict[str, Any]:
        """
        Sends the prompt and key context data to Gemini and gets the response.
        """
        try:
            # Use provided parameters or defaults
            if last_conversations is None:
                last_conversations = []
            if key_context_data is None:
                key_context_data = []

            # Build fixed context
            fixed_context = self._build_fixed_context(max_items)
            
            contents = [
                types.Content(role="user", parts=[types.Part.from_text(text=fixed_context)]),
            ]

            # Add key context data if available
            if key_context_data:
                summary_text = "Key context from previous important interactions:\n" + "\n".join(
                    f"[{c.get('timestamp', '')} | priority: {c.get('context_priority', '')}] {c['relevant_info']}" 
                    for c in key_context_data
                )
                logger.debug(f"[GeminiService] Key context string sent to Gemini: {summary_text}")
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"[CONTEXT SUMMARY]\n{summary_text}")]))

            # Add conversational context if available
            if context_conversations:
                for conv in reversed(context_conversations):
                    user_input = conv.get('user_input', '')
                    server_reply = conv.get('server_reply', '')
                    timestamp = conv.get('timestamp', None)
                    
                    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"User: {user_input} (at {timestamp})")]))
                    
                    clean_reply = server_reply
                    if clean_reply.lower().startswith('assistant:'):
                        clean_reply = clean_reply[len('assistant:'):].strip()
                    contents.append(types.Content(role="assistant", parts=[types.Part.from_text(text=clean_reply)]))

            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"User Request: {prompt}")]))

            logger.debug(f"Prompt to Gemini: {prompt}")
            logger.debug(f"Key context sent to Gemini: {key_context_data}")

            # Generate response
            response_schema = self._build_response_schema()
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            )

            logger.info(f"Sending user prompt to Gemini: {prompt}")
            response_text = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text or ""

            logger.debug(f"Raw Gemini response text: {response_text}")
            gemini_response = json.loads(response_text)
            logger.debug(f"Parsed Gemini response: {gemini_response}")
            
            return gemini_response
            
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            raise

    def _build_fixed_context(self, max_items: int) -> str:
        """Build the fixed context prompt for Gemini"""
        return (
            "You are a virtual assistant. Your responses must be structured as a JSON object with the following fields, matching exactly the provided schema and field names. Do not invent or omit fields.\n"
            "- Be a bit more personal and friendly. If you know the user's name, use it naturally in your responses.\n"
            "- When setting the context_priority for an interaction, start with low numbers for new facts.\n"
            f"- The key context (long-term memory) can hold up to {max_items} entries. Do not repeat information: each entry must be unique and not duplicate the 'relevant_info' of any other entry. If you see that an important entry is about to be replaced by a less important one, INCREASE the priority of the important entry so it is not lost. If you want to explicitly remove or replace an entry, set its priority to 0.\n"
            "- Each entry in the key context is numbered. In your structured response, you can reference the entry number(s) you want to update or remove in a dedicated field (for example, 'context_updates').\n"
            "- IMPORTANT: Do not simply repeat or re-assert facts already present in the key context (such as the user's name) as the most relevant information for new interactions. Only add or highlight new facts if they are truly relevant to the current user request. Focus your response and context updates on the user's actual intent and new information, not on repeating existing context.\n"
            "- If the user says 'no', 'no thanks', 'that's all', 'nothing else', or any clear negative/ending phrase, you must set 'app_params': [{{'question': false }}] and do NOT ask if they need anything else or offer further help. End the conversation politely and do not prompt for more input.\n"
            "- 'server_reply' (string, required): The direct answer to the user, in plain text, concise, and without any prefix or special characters. If you do not have a skill available to fulfill the user's request, you must answer directly in 'server_reply' and never reference or wait for a skill.\n"
            "    - If you do not have access to real data, respond with plausible examples and never say you are waiting, searching, or consulting anything.\n"
            "    - Do not simulate skill actions or say you are going to search or consult. Always answer as if you already have the information.\n"
            "- 'app_params' (array of objects, optional): Parameters for the app. Currently, only one parameter is used: 'question' (boolean). If 'question' is true, the app will continue listening for further input, making the conversation more fluid. If false, the conversation ends and the app stops listening.\n"
            "    - Use 'question': true only if you need more information from the user to fulfill their request. If you already have enough information, respond directly and set 'question': false.\n"
            "    - Do not repeat questions or offer further help if the user has already confirmed or answered affirmatively.\n"
            "    - If the user responds with 'yes' or confirms, proceed to fulfill the request and provide the information, without asking further questions.\n"
            "- 'skills' (array of objects, optional): Skills that the app can perform. Each skill must match exactly the provided list and structure. Do not invent or modify skills or their parameters. If no skill is available for the user's request, do not use this field.\n"
            "- 'server_skill' (object, optional): A specific skill that the server can fulfill directly. If a server skill is required, only complete this field and leave 'skills' empty. The server will attach the requested information and regenerate the response.\n"
            "- 'interaction_params' (object, required): Parameters for summarizing and prioritizing the interaction.\n"
            "    - 'relevant_for_context' (boolean): Whether this interaction is important for long-term context. Use this for information that should be remembered across sessions, such as the user's name, preferences, or other key facts.\n"
            "    - 'context_priority' (integer, 1-100): Priority of this interaction for context retention.\n"
            "    - 'relevant_info' (string): A concise, factual, and contextually useful summary of the most important information about the user or their preferences, written as a fact about the user (e.g., 'The user likes action movies', 'The user's name is Ana', 'The user prefers vegetarian food'). This field should always be filled with the most relevant new fact or preference learned from the interaction, if any. If no new relevant fact is learned, repeat the last most important one.\n"
            "- 'context_updates' (array of objects, optional): Use this field to reference and update key context entries by their number, for example to increase their priority if an important entry is about to be replaced.\n"
            "You will be provided with the available skills, their parameters, and the exact structure to use. Always fill out the fields exactly as specified. If there is no skill available for the user's request, always answer directly in 'server_reply' and do not reference skills. Do not use phrases like 'As a language model' or 'I am an AI'. Do not include disclaimers, apologies, or repeat the question. Only return the JSON object as specified."
        )

    def _build_response_schema(self) -> types.Schema:
        """Build the response schema for Gemini"""
        return types.Schema(
            type=types.Type.OBJECT,
            properties={
                "server_reply": types.Schema(type=types.Type.STRING),
                "app_params": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "question": types.Schema(type=types.Type.BOOLEAN)
                        }
                    )
                ),
                "skills": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "name": types.Schema(type=types.Type.STRING),
                            "action": types.Schema(type=types.Type.STRING),
                            "params": types.Schema(
                                type=types.Type.OBJECT,
                                properties={
                                    "any": types.Schema(type=types.Type.STRING)
                                }
                            ),
                        },
                    ),
                ),
                "server_skill": types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(type=types.Type.STRING),
                        "action": types.Schema(type=types.Type.STRING),
                        "params": types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "any": types.Schema(type=types.Type.STRING)
                            }
                        ),
                    },
                ),
                "interaction_params": types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "relevant_for_context": types.Schema(type=types.Type.BOOLEAN),
                        "context_priority": types.Schema(type=types.Type.INTEGER),
                        "relevant_info": types.Schema(type=types.Type.STRING),
                    },
                    required=["relevant_for_context", "context_priority", "relevant_info"]
                ),
                "context_updates": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "entry_number": types.Schema(type=types.Type.INTEGER),
                            "new_priority": types.Schema(type=types.Type.INTEGER),
                        }
                    )
                ),
            },
            required=["server_reply", "interaction_params"],
        )
