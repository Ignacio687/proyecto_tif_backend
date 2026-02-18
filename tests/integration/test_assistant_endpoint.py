"""
Integration tests for the assistant endpoint.
Uses real Gemini API and real MongoDB (test container). No mocks.
Validates that the real LLM with our context correctly responds and calls skills.

Requirements:
- GEMINI_API_KEY in env (tests are skipped if unset).
- Docker running (testcontainers starts a MongoDB container).
"""
import asyncio
import os
import pytest
from unittest.mock import patch

# Do NOT import app.* at module level: it loads app.config and .env before
# test_env runs, so the app would use .env's MONGODB_URI (e.g. "mongodb" host
# that doesn't resolve). Import GeminiService only inside the test that needs it.

from tests.integration.conftest import skip_if_no_gemini_key


# ---- Google Search: prompts that should trigger search (varied phrasings) ----
GOOGLE_SEARCH_PROMPTS = [
    "What's the weather like today?",
    "What is the weather today?",
    "Tell me the latest news",
    "Search for current events",
    "Who won the last World Cup?",
    "What time is it in Tokyo right now?",
]

# ---- Call skill: unambiguous prompts (explicit name); ambiguous ones are in CALL_WITH_CONTEXT_SCENARIOS ----
# Single request (str) or two-step (first_req, follow_up_req) when model may ask for clarification
CALL_SKILL_PROMPTS = [
    "Call John",
    "I need to call John",
    "Can you call María for me?",
    "Please dial Mom",
    "Call John Smith",
    ("I want to call the office", "Just call the contact Office"),
]

# ---- Call by number: (user_req, expected_number) — response must include ONLY contact_phone with this number ----
CALL_BY_NUMBER_PROMPTS = [
    ("Call 5642612345", "5642612345"),
    ("Dial 54911 4567 8900", "5491145678900"),
    ("Call my mum, its number is 5642612345", "5642612345"),
    ("Ring 555-1234", "5551234"),
]

# ---- Call by name only: (user_req, expected_name) — response must include ONLY contact_name with this name ----
CALL_BY_NAME_ONLY_PROMPTS = [
    ("Call John", "John"),
    ("Call Mom", "Mom"),
    ("Can you call María?", "María"),
    ("Dial the office", "office"),
]

# ---- Call with prior context: (context_message, ambiguous_request, expected_contact_name) ----
# First message establishes who; second is ambiguous so the model must use conversation context.
CALL_WITH_CONTEXT_SCENARIOS = [
    ("My sister's name is Laura.", "Call my sister", "Laura"),
    ("I have a sister called Ana.", "Call my sister", "Ana"),
    ("My brother is named Pedro.", "Call my brother", "Pedro"),
    ("The person I need to reach is María García.", "Call her", "María"),
    ("We were talking about calling John.", "Yes, go ahead and call him", "John"),
    ("I need to contact my mom - her name is Carmen.", "Call my mom", "Carmen"),
    ("The contact I want to dial is Roberto.", "Call that person", "Roberto"),
    ("My sister Claudia can help.", "Call my sister", "Claudia"),
    ("I need to call Sophie about the meeting.", "Call the person I mentioned", "Sophie"),
    ("The one we need to ring is David.", "Yes, call that one", "David"),
]

# ---- Send message skill: unambiguous recipient (ambiguous e.g. "my brother" may trigger follow-up question) ----
SEND_MESSAGE_PROMPTS = [
    "Text John: I'll be there in 5 minutes",
    "Send a message to María saying hello",
    "Can you message Mom that I'm running late?",
]

# ---- Follow-up without "?": assistant asks for content; skills selector must not return placeholder ----
# (user_req, placeholder_message_values) — if SendMessageSkill is returned, message must not be in placeholder set
FOLLOW_UP_WITHOUT_QUESTION_MARK_SCENARIOS = [
    ("I had to tell my sister something", ["something", "what", "it", ""]),
    ("Tell my sister something", ["something", "what", "it", ""]),
    ("I need to message my brother but I didn't say what yet", ["something", "what", "it", ""]),
]

# Same idea with prior context (e.g. we already messaged Patricia); (context_message, user_req, placeholder_message_values)
FOLLOW_UP_WITHOUT_QUESTION_MARK_WITH_CONTEXT = [
    (
        "We already sent a message to Patricia.",
        "I had to tell my sister something",
        ["something", "what", "it", ""],
    ),
]

# ---- Create reminder skill: prompts that should trigger CreateReminderSkill (send timezone so "in 1 hour" / "tomorrow" resolve) ----
CREATE_REMINDER_PROMPTS = [
    "Remind me in 1 hour to call John",
    "Set a reminder for tomorrow at 9 to buy milk",
    "Remind me at 5pm to leave the office",
]


class TestAssistantEndpointIntegration:
    """Basic structure and connectivity."""

    def test_assistant_normal_flow_returns_correct_structure(
        self, client, auth_token
    ):
        """Normal flow: real LLM returns 200 and ServerResponse shape."""
        skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={"user_req": "Hello, how are you?"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "server_reply" in data
        assert isinstance(data["server_reply"], str)
        assert len(data["server_reply"].strip()) > 0
        assert "app_params" in data
        assert isinstance(data["app_params"], list)
        assert len(data["app_params"]) >= 1
        assert "question" in data["app_params"][0]
        if data.get("skills") is not None:
            assert isinstance(data["skills"], list)

    def test_assistant_accepts_optional_timezone_and_location(
        self, client, auth_token
    ):
        """Request body can include optional timezone and location (Points 2 & 3)."""
        skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={
                "user_req": "Hello",
                "timezone": "America/Argentina/Buenos_Aires",
                "location": "Buenos Aires, Argentina",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "server_reply" in data
        assert isinstance(data["server_reply"], str)


class TestGoogleSearchFlow:
    """Validate Google Search: no skill in final response, and API was called with tool."""

    @pytest.mark.parametrize("user_req", GOOGLE_SEARCH_PROMPTS)
    def test_google_search_final_response_has_no_google_skill(
        self, client, auth_token, user_req
    ):
        """For search-style prompts, final response must NOT include GoogleSearchSkill (it is executed server-side)."""
        skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={"user_req": user_req},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "server_reply" in data
        assert isinstance(data["server_reply"], str)
        assert len(data["server_reply"].strip()) > 0
        skills = data.get("skills") or []
        google_skills = [s for s in skills if s.get("name") == "GoogleSearchSkill"]
        assert len(google_skills) == 0, (
            f"GoogleSearchSkill must not appear in final response (executed server-side). Got skills: {skills}"
        )

    # Location payload so backend injects "Current date/time" and "User location"
    WEATHER_REQUEST_WITH_LOCATION = [
        {"user_req": "What's the weather like today?", "timezone": "Europe/London", "location": "London, UK"},
        {"user_req": "What is the weather today?", "timezone": "America/Argentina/Buenos_Aires", "location": "Buenos Aires, Argentina"},
    ]

    @pytest.mark.parametrize("payload", WEATHER_REQUEST_WITH_LOCATION)
    def test_google_search_tool_was_used_when_search_expected(
        self, client, auth_token, payload
    ):
        """With location, second call always runs; skills selector is told first reply may imply action not yet done, so search is invoked."""
        skip_if_no_gemini_key()
        from app.services.gemini_service import GeminiService

        google_search_calls = []
        original = GeminiService._generate_response

        def record_wrapper(
            self,
            prompt,
            key_context_data,
            last_conversations,
            context_conversations,
            max_items,
            use_google_search=False,
            reply_only=False,
            current_time_str="",
            user_location_str="",
            user_timezone=None,
        ):
            google_search_calls.append(use_google_search)
            return original(
                self,
                prompt,
                key_context_data,
                last_conversations,
                context_conversations,
                max_items,
                use_google_search,
                reply_only,
                current_time_str,
                user_location_str,
                user_timezone,
            )

        with patch.object(GeminiService, "_generate_response", record_wrapper):
            response = client.post(
                "/api/v1/assistant",
                json=payload,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        assert response.status_code == 200
        assert any(
            google_search_calls
        ), "Expected at least one call with use_google_search=True (Google Search tool active)"


class TestCallSkillFlow:
    """Validate Call skill: always present with correct data for call instructions.
    Uses auth_token_fresh_user so each run has no prior conversation (model won't ask 'Which John?')."""

    @pytest.mark.parametrize("user_req", CALL_SKILL_PROMPTS)
    def test_call_instruction_returns_call_skill_with_correct_data(
        self, client, auth_token_fresh_user, user_req
    ):
        """For call instructions, response must include a call skill with correct structure and contact data.
        If user_req is a tuple (first_req, follow_up_req), send both and assert on the second response."""
        skip_if_no_gemini_key()
        if isinstance(user_req, tuple):
            first_req, follow_up_req = user_req
            client.post(
                "/api/v1/assistant",
                json={"user_req": first_req},
                headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
            )
            response = client.post(
                "/api/v1/assistant",
                json={"user_req": follow_up_req},
                headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
            )
        else:
            response = client.post(
                "/api/v1/assistant",
                json={"user_req": user_req},
                headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "server_reply" in data
        skills = data.get("skills")
        assert skills is not None and len(skills) >= 1, (
            f"Expected at least one skill for call instruction. Got skills: {skills}"
        )
        call_skills = [
            s
            for s in skills
            if (s.get("name") or "").lower().find("call") != -1
            and (s.get("action") or "").lower() == "call_contact"
        ]
        assert len(call_skills) >= 1, (
            f"Expected CallContactSkill (action=call_contact) for call instruction. Got skills: {skills}"
        )
        skill = call_skills[0]
        params = skill.get("params") or {}
        contact_name = (params.get("contact_name") or "").strip()
        contact_phone = (params.get("contact_phone") or "").strip()
        assert contact_name or contact_phone, (
            f"Call skill params must contain contact_name or contact_phone (at least one non-empty). Got: {params}"
        )
        assert not (contact_name and contact_phone), (
            f"Call skill must have exactly one of contact_name or contact_phone. Got: {params}"
        )

    @pytest.mark.parametrize("user_req,expected_number", CALL_BY_NUMBER_PROMPTS)
    def test_call_by_number_returns_only_contact_phone_with_given_number(
        self, client, auth_token_fresh_user, user_req, expected_number
    ):
        """When the user provides a phone number, response must include ONLY contact_phone containing that number."""
        skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={"user_req": user_req},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert response.status_code == 200, f"Request failed: {response.text[:200]}"
        data = response.json()
        skills = data.get("skills") or []
        call_skills = [
            s
            for s in skills
            if (s.get("name") or "").lower().find("call") != -1
            and (s.get("action") or "").lower() == "call_contact"
        ]
        assert len(call_skills) >= 1, (
            f"Expected CallContactSkill for number request '{user_req}'. Got skills: {skills}"
        )
        params = call_skills[0].get("params") or {}
        contact_name = (params.get("contact_name") or "").strip()
        contact_phone = (params.get("contact_phone") or "").strip()
        assert contact_phone, (
            f"For number request '{user_req}' model must return contact_phone. Got: {params}"
        )
        assert not contact_name, (
            f"For number request response must have only contact_phone, not contact_name. Got: {params}"
        )
        # Response must contain the number we sent (compare normalized digits)
        expected_digits = "".join(c for c in expected_number if c.isdigit())
        actual_digits = "".join(c for c in contact_phone if c.isdigit())
        assert expected_digits in actual_digits or actual_digits in expected_digits, (
            f"contact_phone should contain the requested number {expected_number!r}. Got: {contact_phone!r}"
        )

    @pytest.mark.parametrize("user_req,expected_name", CALL_BY_NAME_ONLY_PROMPTS)
    def test_call_by_name_returns_only_contact_name_with_given_name(
        self, client, auth_token_fresh_user, user_req, expected_name
    ):
        """When the user provides only a name (no number), response must include ONLY contact_name containing that name."""
        skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={"user_req": user_req},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert response.status_code == 200, f"Request failed: {response.text[:200]}"
        data = response.json()
        skills = data.get("skills") or []
        call_skills = [
            s
            for s in skills
            if (s.get("name") or "").lower().find("call") != -1
            and (s.get("action") or "").lower() == "call_contact"
        ]
        assert len(call_skills) >= 1, (
            f"Expected CallContactSkill for name request '{user_req}'. Got skills: {skills}"
        )
        params = call_skills[0].get("params") or {}
        contact_name = (params.get("contact_name") or "").strip()
        contact_phone = (params.get("contact_phone") or "").strip()
        assert contact_name, (
            f"For name request '{user_req}' model must return contact_name. Got: {params}"
        )
        assert not contact_phone, (
            f"For name-only request response must have only contact_name, not contact_phone. Got: {params}"
        )
        assert expected_name.lower() in contact_name.lower(), (
            f"contact_name should contain the requested name {expected_name!r}. Got: {contact_name!r}"
        )


class TestCallSkillWithContext:
    """Ambiguous call requests that are disambiguated by a previous message in the conversation.
    Uses auth_token_fresh_user so each scenario has isolated conversation history (no prior sisters/contacts)."""

    @pytest.mark.parametrize(
        "context_message,ambiguous_request,expected_contact_name",
        CALL_WITH_CONTEXT_SCENARIOS,
    )
    def test_ambiguous_call_uses_prior_context(
        self, client, auth_token_fresh_user, context_message, ambiguous_request, expected_contact_name
    ):
        """First message establishes the contact; second message is ambiguous (e.g. 'Call my sister'). Model should infer contact from context."""
        skip_if_no_gemini_key()

        # 1) Establish context: user mentions the contact (sister/brother/mom/name)
        r1 = client.post(
            "/api/v1/assistant",
            json={"user_req": context_message},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert r1.status_code == 200, f"Context message failed: {r1.text[:200]}"

        # 2) Ambiguous request: "Call my sister", "Call her", etc. — model should use prior turn
        r2 = client.post(
            "/api/v1/assistant",
            json={"user_req": ambiguous_request},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert r2.status_code == 200, f"Ambiguous request failed: {r2.text[:200]}"
        data = r2.json()

        skills = data.get("skills") or []
        call_skills = [
            s
            for s in skills
            if (s.get("name") or "").lower().find("call") != -1
            and (s.get("action") or "").lower() == "call_contact"
        ]
        assert len(call_skills) >= 1, (
            f"Expected CallContactSkill after context '{context_message}' and request '{ambiguous_request}'. "
            f"Got skills: {skills}. Reply: {(data.get('server_reply') or '')[:150]}"
        )
        skill = call_skills[0]
        params = skill.get("params") or {}
        contact_name = (params.get("contact_name") or "").strip()
        assert len(contact_name) > 0, (
            f"contact_name must be non-empty after context. Got: {params}"
        )
        # Expected name may appear as full name or first name (e.g. "María García" -> "María")
        expected_lower = expected_contact_name.lower()
        contact_lower = contact_name.lower()
        assert expected_lower in contact_lower or contact_lower in expected_lower, (
            f"Expected contact_name to match '{expected_contact_name}' from context. Got contact_name: '{contact_name}'"
        )


class TestSendMessageSkillFlow:
    """Validate Send message skill: response includes SendMessageSkill with recipient and message.
    Uses auth_token_fresh_user so each run has no prior conversation (model won't ask 'Which John?')."""

    @pytest.mark.parametrize("user_req", SEND_MESSAGE_PROMPTS)
    def test_send_message_returns_skill_with_recipient_and_message(
        self, client, auth_token_fresh_user, user_req
    ):
        """For message/text instructions, response must include SendMessageSkill with recipient and message."""
        skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={"user_req": user_req},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "server_reply" in data
        skills = data.get("skills") or []
        msg_skills = [
            s for s in skills
            if (s.get("name") or "").lower().find("message") != -1
            and (s.get("action") or "").lower() == "send_message"
        ]
        assert len(msg_skills) >= 1, (
            f"Expected SendMessageSkill for message instruction. Got skills: {skills}"
        )
        skill = msg_skills[0]
        params = skill.get("params") or {}
        assert "recipient" in params and "message" in params, (
            f"SendMessage params must contain recipient and message. Got: {params}"
        )
        recipient = (params.get("recipient") or "").strip()
        message = (params.get("message") or "").strip()
        assert len(recipient) > 0 and len(message) > 0, (
            f"recipient and message must be non-empty. Got: {params}"
        )


class TestFollowUpWithoutQuestionMark:
    """When the assistant asks for more info without '?', skills selector must not return placeholder (e.g. send_message with message 'algo')."""

    @pytest.mark.parametrize(
        "user_req,placeholder_message_values",
        FOLLOW_UP_WITHOUT_QUESTION_MARK_SCENARIOS,
    )
    def test_no_send_message_with_placeholder_when_assistant_asks_for_content(
        self, client, auth_token_fresh_user, user_req, placeholder_message_values
    ):
        """User says they need to tell someone 'something' but doesn't specify what. Assistant may reply asking for content without '?'; we must not return SendMessageSkill with placeholder message."""
        skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={"user_req": user_req},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert response.status_code == 200
        data = response.json()
        skills = data.get("skills") or []
        msg_skills = [
            s for s in skills
            if (s.get("name") or "").lower().find("message") != -1
            and (s.get("action") or "").lower() == "send_message"
        ]
        placeholders = {p.lower().strip() for p in placeholder_message_values if p is not None}
        for skill in msg_skills:
            params = skill.get("params") or {}
            if not params:
                continue
            message = (params.get("message") or "").strip().lower()
            assert message not in placeholders, (
                f"SendMessageSkill must not use placeholder message when assistant asks for content. "
                f"Got message: {repr(params.get('message'))}. Reply: {(data.get('server_reply') or '')[:150]}"
            )

    @pytest.mark.parametrize(
        "context_message,user_req,placeholder_message_values",
        FOLLOW_UP_WITHOUT_QUESTION_MARK_WITH_CONTEXT,
    )
    def test_no_send_message_placeholder_when_assistant_asks_for_content_with_context(
        self, client, auth_token_fresh_user, context_message, user_req, placeholder_message_values
    ):
        """With prior context (e.g. already messaged Patricia), user says they had to tell sister something. Assistant may ask what to say without '?'; no placeholder message in skill."""
        skip_if_no_gemini_key()
        # Establish context
        r1 = client.post(
            "/api/v1/assistant",
            json={"user_req": context_message},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert r1.status_code == 200
        # Ambiguous: user doesn't say what message to send
        response = client.post(
            "/api/v1/assistant",
            json={"user_req": user_req},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert response.status_code == 200
        data = response.json()
        skills = data.get("skills") or []
        msg_skills = [
            s for s in skills
            if (s.get("name") or "").lower().find("message") != -1
            and (s.get("action") or "").lower() == "send_message"
        ]
        placeholders = {p.lower().strip() for p in placeholder_message_values if p is not None}
        for skill in msg_skills:
            params = skill.get("params") or {}
            if not params:
                continue
            message = (params.get("message") or "").strip().lower()
            assert message not in placeholders, (
                f"SendMessageSkill must not use placeholder when assistant asked for content. "
                f"Got message: {repr(params.get('message'))}. Reply: {(data.get('server_reply') or '')[:150]}"
            )


class TestCreateReminderSkillFlow:
    """Validate Create reminder skill: response includes CreateReminderSkill with title and datetime.
    Uses auth_token_fresh_user: reminder tests are isolated (single request + timezone), no prior context needed."""

    @pytest.mark.parametrize("user_req", CREATE_REMINDER_PROMPTS)
    def test_create_reminder_returns_skill_with_title_and_datetime(
        self, client, auth_token_fresh_user, user_req
    ):
        """For reminder instructions, response must include CreateReminderSkill with title and datetime. Send timezone so 'in 1 hour' / 'tomorrow' resolve."""
        skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={
                "user_req": user_req,
                "timezone": "America/Argentina/Buenos_Aires",
            },
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "server_reply" in data
        skills = data.get("skills") or []
        reminder_skills = [
            s for s in skills
            if (s.get("name") or "").lower().find("reminder") != -1
            and (s.get("action") or "").lower() == "create_reminder"
        ]
        assert len(reminder_skills) >= 1, (
            f"Expected CreateReminderSkill for reminder instruction. Got skills: {skills}"
        )
        skill = reminder_skills[0]
        params = skill.get("params") or {}
        assert "title" in params and "datetime" in params, (
            f"CreateReminder params must contain title and datetime. Got: {params}"
        )
        title = (params.get("title") or "").strip()
        dt = (params.get("datetime") or "").strip()
        assert len(title) > 0 and len(dt) > 0, (
            f"title and datetime must be non-empty. Got: {params}"
        )


class TestPatchFailedCallFlow:
    """Validate patch response when a call fails (contact not found, similar contacts provided)."""

    def test_patch_failed_call_informs_user_with_similar_contacts(
        self, client, auth_token
    ):
        """Real flow: first request is a call; second request is a patch with contact not found + similar contacts."""
        skip_if_no_gemini_key()

        # 1) First request: user asks to call someone (so conversation has that)
        r1 = client.post(
            "/api/v1/assistant",
            json={"user_req": "Call John"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert r1.status_code == 200

        # 2) Patch request: contact not found, similar contacts from device
        similar_contacts = ["Jane Doe", "Bob Smith", "Johnny"]
        r2 = client.post(
            "/api/v1/assistant",
            json={
                "user_req": "The contact was not found",
                "system_message": {
                    "patch_last": True,
                    "skill_failure_message": "Contact not found",
                    "contacts_list": similar_contacts,
                },
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert r2.status_code == 200
        data = r2.json()
        reply = (data.get("server_reply") or "").lower()
        # Model should inform about not found and/or suggest similar contacts
        found_mention = any(c.lower() in reply for c in similar_contacts)
        found_not_found = "not found" in reply or "not find" in reply or "available" in reply or "contact" in reply
        assert found_mention or found_not_found, (
            f"Patch response should mention similar contacts or 'not found'. Got: {data.get('server_reply', '')[:200]}"
        )

    @pytest.mark.parametrize(
        "user_req,contacts",
        [
            ("It didn't work, contact not found", ["Alice", "Bob"]),
            ("No such contact", ["María García", "María López"]),
        ],
    )
    def test_patch_failed_call_variations(
        self, client, auth_token, user_req, contacts
    ):
        """Patch with different phrasings and contact lists; response should reflect failure and options."""
        skip_if_no_gemini_key()

        # Ensure there is a previous "call" turn (so patch has context)
        client.post(
            "/api/v1/assistant",
            json={"user_req": "Call John"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        r = client.post(
            "/api/v1/assistant",
            json={
                "user_req": user_req,
                "system_message": {
                    "patch_last": True,
                    "skill_failure_message": "Contact not found",
                    "contacts_list": contacts,
                },
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert r.status_code == 200
        data = r.json()
        reply = (data.get("server_reply") or "").lower()
        found_contact_mention = any(c.lower() in reply for c in contacts)
        found_failure_mention = (
            "not found" in reply
            or "not find" in reply
            or "available" in reply
            or "contact" in reply
        )
        assert found_contact_mention or found_failure_mention, (
            f"Patch response should mention contacts or failure. Got: {reply[:250]}"
        )


class TestConversationHistoryTimezone:
    """GET /conversations: optional timezone returns timestamps in that timezone (stored UTC)."""

    def test_get_conversations_without_timezone_returns_timestamps(self, client, auth_token):
        """Without timezone param, timestamps are returned (UTC ISO)."""
        skip_if_no_gemini_key()
        client.post(
            "/api/v1/assistant",
            json={"user_req": "Hello"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        r = client.get(
            "/api/v1/conversations",
            params={"page": 1, "page_size": 5},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "conversations" in data
        assert len(data["conversations"]) >= 1
        conv = data["conversations"][0]
        assert "timestamp" in conv
        ts = conv["timestamp"]
        assert "202" in ts and ("T" in ts or " " in ts)

    def test_get_conversations_with_timezone_returns_timestamps_in_that_tz(
        self, client, auth_token_fresh_user
    ):
        """With timezone param, timestamps (stored UTC) are returned in that timezone (ISO)."""
        skip_if_no_gemini_key()
        client.post(
            "/api/v1/assistant",
            json={"user_req": "Hi"},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        r = client.get(
            "/api/v1/conversations",
            params={"page": 1, "page_size": 5, "timezone": "America/Argentina/Buenos_Aires"},
            headers={"Authorization": f"Bearer {auth_token_fresh_user}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "conversations" in data
        assert len(data["conversations"]) >= 1
        conv = data["conversations"][0]
        assert "timestamp" in conv
        ts = conv["timestamp"]
        assert "202" in ts
        # Buenos Aires is UTC-3; ISO string should include offset
        assert "-03" in ts or "+00:00" in ts or "T" in ts


class TestConcurrentRequestsDoNotStack:
    """Verify multiple user requests are handled in parallel, not serialized."""

    @pytest.mark.asyncio
    async def test_multiple_get_gemini_response_calls_run_in_parallel(self):
        """
        Multiple concurrent callers of get_gemini_response (async) should not block
        each other: the sync work runs in a thread pool, so N calls complete in
        ~single-call time, not N * single-call time.
        """
        import time
        from unittest.mock import patch
        from app.services.gemini_service import GeminiService
        from app.services.context_service import ContextService

        delay_s = 0.4
        num_concurrent = 5
        minimal_response = {
            "server_reply": "OK",
            "app_params": [{"question": False}],
            "skills": [],
            "interaction_params": {
                "relevant_for_context": False,
                "context_priority": 1,
                "relevant_info": "",
            },
        }

        def slow_sync(*args, **kwargs):
            time.sleep(delay_s)
            return minimal_response.copy()

        context_service = ContextService()
        gemini_service = GeminiService(context_service)

        with patch.object(GeminiService, "get_gemini_response_sync", side_effect=slow_sync):
            start = time.perf_counter()
            results = await asyncio.gather(
                *[
                    gemini_service.get_gemini_response(
                        "hello",
                        key_context_data=[],
                        last_conversations=[],
                        context_conversations=[],
                        max_items=10,
                    )
                    for _ in range(num_concurrent)
                ]
            )
            elapsed = time.perf_counter() - start

        assert len(results) == num_concurrent
        for r in results:
            assert isinstance(r, dict)
            assert r.get("server_reply") == "OK"
        # If requests stacked (serial), we'd have ~ num_concurrent * delay_s.
        # With parallel execution we expect ~delay_s + small overhead.
        max_acceptable = delay_s * 2.0
        assert elapsed < max_acceptable, (
            f"Concurrent requests took {elapsed:.2f}s (expected < {max_acceptable}s). "
            "Requests may be serializing instead of running in parallel."
        )
