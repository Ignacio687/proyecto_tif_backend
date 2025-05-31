import os
from google import genai
from google.genai import types
from app.config import settings
from app.logger import logger

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY

    def build_and_update_summarized_context(self, conversations, new_interaction=None, max_items=10):
        """
        Build and update the summarized context from previous conversations and an optional new interaction.
        Only interactions with relevant_for_context=True are included. If new_interaction is provided, it is considered for inclusion.
        Returns a list of dicts with relevant_info, timestamp, and context_priority, ordered by priority (highest first).
        """
        if not conversations:
            return []
        # Filter only relevant interactions
        relevant = [
            c for c in conversations
            if c.get('interaction_params', {}).get('relevant_for_context')
            and 'context_priority' in c.get('interaction_params', {})
            and 'relevant_info' in c.get('interaction_params', {})
        ]
        # Optionally add the new interaction if relevant
        if new_interaction and new_interaction.get('interaction_params', {}).get('relevant_for_context'):
            relevant.append(new_interaction)
        # Sort by context_priority
        relevant.sort(key=lambda c: c['interaction_params']['context_priority'], reverse=True)
        # Build summarized context with all required fields
        summarized = []
        for c in relevant[:max_items]:
            summarized.append({
                'relevant_info': c['interaction_params']['relevant_info'],
                'timestamp': c.get('timestamp'),
                'context_priority': c['interaction_params']['context_priority']
            })
        return summarized

    async def save_summarized_context(self, summarized_context, repository):
        """
        Save the summarized context to the database using the repository interface.
        """
        await repository.save_summarized_context(summarized_context)

    async def load_summarized_context(self, repository):
        """
        Load the summarized context from the database using the repository interface.
        """
        return await repository.get_summarized_context()

    async def get_gemini_response(self, prompt: str, repository=None, context_conversations=None) -> dict:
        """
        Sends the prompt and summarized context to Gemini, gets the response, and updates the summarized context in the database.
        If repository is None, only queries Gemini (legacy/test mode).
        """
        client = genai.Client(api_key=self.api_key)
        model = "gemini-2.0-flash-lite"
        # 1. Load last conversations for context
        last_conversations = []
        if repository is not None:
            last_conversations = await repository.get_last_conversations()
        # 2. Build fixed context
        fixed_context = (
            "You are a virtual assistant. Your responses must be structured as a JSON object with the following fields, matching exactly the provided schema and field names. Do not invent or omit fields.\n"
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
            "You will be provided with the available skills, their parameters, and the exact structure to use. Always fill out the fields exactly as specified. If there is no skill available for the user's request, always answer directly in 'server_reply' and do not reference skills. Do not use phrases like 'As a language model' or 'I am an AI'. Do not include disclaimers, apologies, or repeat the question. Only return the JSON object as specified."
        )
        logger.debug(f"Gemini fixed context: {fixed_context}")
        contents = [
            types.Content(role="user", parts=[types.Part.from_text(text=fixed_context)]),
        ]
        # 3. Add summarized context if available
        summarized_context = []
        if repository is not None:
            summarized_context = await self.load_summarized_context(repository)
            logger.debug(f"[GeminiService] Loaded summarized context: {summarized_context}")
        if summarized_context:
            summary_text = "Summarized context of previous important interactions (highest priority first):\n" + "\n".join(
                f"[{c.get('timestamp', '')} | priority: {c.get('context_priority', '')}] {c['relevant_info']}" for c in summarized_context
            )
            logger.debug(f"[GeminiService] Summarized context string sent to Gemini: {summary_text}")
            contents.append(types.Content(role="system", parts=[types.Part.from_text(text=summary_text)]))
        # 4. Add conversational context if available
        filtered_context_conversations = []
        if context_conversations:
            for conv in reversed(context_conversations):
                # Only include user_input, server_reply, and timestamp for prompt and logs
                user_input = conv.get('user_input', '')
                server_reply = conv.get('server_reply', '')
                timestamp = conv.get('timestamp', None)
                filtered_context_conversations.append({
                    'user_input': user_input,
                    'server_reply': server_reply,
                    'timestamp': timestamp
                })
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"User: {user_input} (at {timestamp})")]))
                # Remove any leading 'Assistant:' (case-insensitive) and extra whitespace
                clean_reply = server_reply
                if clean_reply.lower().startswith('assistant:'):
                    clean_reply = clean_reply[len('assistant:'):].strip()
                contents.append(types.Content(role="assistant", parts=[types.Part.from_text(text=clean_reply)]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"User Request: {prompt}")]))
        logger.debug(f"Prompt to Gemini: {prompt}")
        logger.debug(f"Summarized context sent to Gemini: {summarized_context}")
        logger.debug(f"Conversational context sent to Gemini: {filtered_context_conversations}")
        # 5. Response schema
        response_schema = types.Schema(
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
            },
            required=["server_reply", "interaction_params"],
        )
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        )
        logger.info(f"Sending user prompt to Gemini: {prompt}")
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text or ""
        logger.debug(f"Raw Gemini response text: {response_text}")
        import json
        gemini_response = json.loads(response_text)
        logger.debug(f"Parsed Gemini response: {gemini_response}")
        # 6. If repository is provided, update summarized context with the new interaction
        if repository is not None:
            new_interaction = {
                'interaction_params': gemini_response.get('interaction_params', {}),
                'server_reply': gemini_response.get('server_reply', ''),
                'user_input': prompt
            }
            updated_summarized_context = self.build_and_update_summarized_context(
                last_conversations, new_interaction=new_interaction
            )
            await self.save_summarized_context(updated_summarized_context, repository)
        return gemini_response
