import os
from google import genai
from google.genai import types
from app.config import settings
from app.logger import logger
from app.repositories.mongo_repository import MongoRepository
from app.models.request_response import ServerResponse

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY

    def build_and_update_summarized_context(self, summarized_context, new_interaction=None, max_items=10, context_updates=None):
        """
        Update the summarized context (list of relevant interactions) by adding the new interaction if relevant.
        - Number the entries (add 'entry_number' field, 1-based).
        - Process context_updates to update priorities as requested by Gemini.
        - If the new interaction is relevant, add it and remove the lowest-priority one if the limit is reached.
        """
        # If no summarized context, start with empty list
        if not summarized_context:
            summarized_context = []
        # Number entries (1-based)
        for idx, entry in enumerate(summarized_context, start=1):
            entry['entry_number'] = idx
        # Process context_updates if provided
        if context_updates:
            for update in context_updates:
                entry_number = update.get('entry_number')
                new_priority = update.get('new_priority')
                if entry_number is not None and new_priority is not None:
                    # entry_number is 1-based
                    idx = entry_number - 1
                    if 0 <= idx < len(summarized_context):
                        summarized_context[idx]['context_priority'] = new_priority
        # Only add the new interaction if it is relevant
        if new_interaction and new_interaction.get('interaction_params', {}).get('relevant_for_context'):
            summarized_context.append({
                'relevant_info': new_interaction['interaction_params']['relevant_info'],
                'timestamp': new_interaction.get('timestamp'),
                'context_priority': new_interaction['interaction_params']['context_priority']
            })
        # Remove entries with context_priority 0
        summarized_context = [entry for entry in summarized_context if entry.get('context_priority', 1) != 0]
        # Sort by context_priority descending
        summarized_context.sort(key=lambda c: c['context_priority'], reverse=True)
        # Trim to max_items
        summarized_context = summarized_context[:max_items]
        # Re-number after changes
        for idx, entry in enumerate(summarized_context, start=1):
            entry['entry_number'] = idx
        return summarized_context

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

    async def get_gemini_response(self, prompt: str, summarized_context=None, last_conversations=None, context_conversations=None, max_items=10) -> dict:
        """
        Sends the prompt and summarized context to Gemini and gets the response. No repository access here.
        """
        client = genai.Client(api_key=self.api_key)
        model = "gemini-2.0-flash-lite"
        # 1. Use provided last_conversations and summarized_context
        if last_conversations is None:
            last_conversations = []
        if summarized_context is None:
            summarized_context = []
        # 2. Build fixed context
        fixed_context = (
            "You are a virtual assistant. Your responses must be structured as a JSON object with the following fields, matching exactly the provided schema and field names. Do not invent or omit fields.\n"
            "- Be a bit more personal and friendly. If you know the user's name, use it naturally in your responses.\n"
            "- When setting the context_priority for an interaction, start with low numbers for new facts.\n"
            f"- The summarized context (long-term memory) can hold up to {max_items} entries. Do not repeat information: each entry must be unique and not duplicate the 'relevant_info' of any other entry. If you see that an important entry is about to be replaced by a less important one, INCREASE the priority of the important entry so it is not lost. If you want to explicitly remove or replace an entry, set its priority to 0.\n"
            "- Each entry in the summarized context is numbered. In your structured response, you can reference the entry number(s) you want to update or remove in a dedicated field (for example, 'context_updates').\n"
            "- IMPORTANT: Do not simply repeat or re-assert facts already present in the summarized context (such as the user's name) as the most relevant information for new interactions. Only add or highlight new facts if they are truly relevant to the current user request. Focus your response and context updates on the user's actual intent and new information, not on repeating existing context.\n"
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
            "- 'context_updates' (array of objects, optional): Use this field to reference and update summarized context entries by their number, for example to increase their priority if an important entry is about to be replaced.\n"
            "You will be provided with the available skills, their parameters, and the exact structure to use. Always fill out the fields exactly as specified. If there is no skill available for the user's request, always answer directly in 'server_reply' and do not reference skills. Do not use phrases like 'As a language model' or 'I am an AI'. Do not include disclaimers, apologies, or repeat the question. Only return the JSON object as specified."
        ).format(max_items=max_items)
        logger.debug(f"Gemini fixed context: {fixed_context}")
        contents = [
            types.Content(role="user", parts=[types.Part.from_text(text=fixed_context)]),
        ]
        # 3. Add summarized context if available
        if summarized_context:
            summary_text = "Summarized context of previous important interactions:\n" + "\n".join(
                f"[{c.get('timestamp', '')} | priority: {c.get('context_priority', '')}] {c['relevant_info']}" for c in summarized_context
            )
            logger.debug(f"[GeminiService] Summarized context string sent to Gemini: {summary_text}")
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"[CONTEXT SUMMARY]\n{summary_text}")]))
        # 4. Add conversational context if available
        filtered_context_conversations = []
        if context_conversations:
            for conv in reversed(context_conversations):
                user_input = conv.get('user_input', '')
                server_reply = conv.get('server_reply', '')
                timestamp = conv.get('timestamp', None)
                filtered_context_conversations.append({
                    'user_input': user_input,
                    'server_reply': server_reply,
                    'timestamp': timestamp
                })
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"User: {user_input} (at {timestamp})")]))
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
        return gemini_response

    async def handle_user_request(self, user_req: str, max_items: int = 10):
        """
        Orchestrates the full flow: loads context, calls Gemini, saves conversation and summarized context, and returns ServerResponse.
        """
        repository = MongoRepository()
        # 1. Get last conversations
        last_conversations = await repository.get_last_conversations()
        # 2. Get summarized context
        summarized_context = await repository.get_summarized_context()
        # 3. Call Gemini
        gemini_reply = await self.get_gemini_response(
            user_req,
            summarized_context=summarized_context,
            last_conversations=last_conversations,
            context_conversations=last_conversations,
            max_items=max_items
        )
        # 4. Save the conversation
        await repository.save_conversation(
            user_req,
            gemini_reply.get('server_reply', ''),
            gemini_reply.get('interaction_params')
        )
        # 5. Update summarized context, process context_updates if present
        new_interaction = {
            'interaction_params': gemini_reply.get('interaction_params', {}),
            'server_reply': gemini_reply.get('server_reply', ''),
            'user_input': user_req
        }
        context_updates = gemini_reply.get('context_updates')
        updated_summarized_context = self.build_and_update_summarized_context(
            summarized_context, new_interaction=new_interaction, max_items=max_items, context_updates=context_updates
        )
        await self.save_summarized_context(updated_summarized_context, repository)
        # 6. Return structured response
        return ServerResponse(
            server_reply=gemini_reply.get('server_reply', ''),
            app_params=gemini_reply.get('app_params'),
            skills=gemini_reply.get('skills')
        )
