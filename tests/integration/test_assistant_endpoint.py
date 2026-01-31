"""
Integration tests for the assistant endpoint.
Uses real Gemini API and real MongoDB (test container). No mocks.
Validates that the real LLM with our context correctly responds and calls skills.

Requirements:
- GEMINI_API_KEY in env (tests are skipped if unset).
- Docker running (testcontainers starts a MongoDB container).
"""
import json
import os
import pytest
from unittest.mock import patch

# Do NOT import app.* at module level: it loads app.config and .env before
# test_env runs, so the app would use .env's MONGODB_URI (e.g. "mongodb" host
# that doesn't resolve). Import GeminiService only inside the test that needs it.


def _skip_if_no_gemini_key():
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set; integration tests require real Gemini API")


# ---- Google Search: prompts that should trigger search (varied phrasings) ----
GOOGLE_SEARCH_PROMPTS = [
    "What's the weather like today?",
    "What is the weather today?",
    "Tell me the latest news",
    "Search for current events",
    "Who won the last World Cup?",
    "What time is it in Tokyo right now?",
]

# ---- Call skill: clear and misleading phrasings ----
CALL_SKILL_PROMPTS = [
    "Call John",
    "I need to call John",
    "Can you call María for me?",
    "Please dial Mom",
    "Ring my brother",
    "Call John Smith",
    "I want to call the office",
    "Call my sister",
]


class TestAssistantEndpointIntegration:
    """Basic structure and connectivity."""

    def test_assistant_normal_flow_returns_correct_structure(
        self, client, auth_token
    ):
        """Normal flow: real LLM returns 200 and ServerResponse shape."""
        _skip_if_no_gemini_key()
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


class TestGoogleSearchFlow:
    """Validate Google Search: no skill in final response, and API was called with tool."""

    @pytest.mark.parametrize("user_req", GOOGLE_SEARCH_PROMPTS)
    def test_google_search_final_response_has_no_google_skill(
        self, client, auth_token, user_req
    ):
        """For search-style prompts, final response must NOT include GoogleSearchSkill (it is executed server-side)."""
        _skip_if_no_gemini_key()
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

    @pytest.mark.parametrize("user_req", GOOGLE_SEARCH_PROMPTS[:2])  # subset to avoid rate limits
    def test_google_search_tool_was_used_when_search_expected(
        self, client, auth_token, user_req
    ):
        """Verify that _generate_response was called with use_google_search=True (Google Search tool active)."""
        _skip_if_no_gemini_key()
        from app.services.gemini_service import GeminiService

        google_search_calls = []
        original = GeminiService._generate_response

        async def record_wrapper(
            self,
            prompt,
            key_context_data,
            last_conversations,
            context_conversations,
            max_items,
            use_google_search=False,
        ):
            google_search_calls.append(use_google_search)
            return await original(
                self,
                prompt,
                key_context_data,
                last_conversations,
                context_conversations,
                max_items,
                use_google_search,
            )

        with patch.object(GeminiService, "_generate_response", record_wrapper):
            response = client.post(
                "/api/v1/assistant",
                json={"user_req": user_req},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        assert response.status_code == 200
        assert any(
            google_search_calls
        ), "Expected at least one call with use_google_search=True (Google Search tool active)"


class TestCallSkillFlow:
    """Validate Call skill: always present with correct data for call instructions."""

    @pytest.mark.parametrize("user_req", CALL_SKILL_PROMPTS)
    def test_call_instruction_returns_call_skill_with_correct_data(
        self, client, auth_token, user_req
    ):
        """For call instructions, response must include a call skill with correct structure and contact data."""
        _skip_if_no_gemini_key()
        response = client.post(
            "/api/v1/assistant",
            json={"user_req": user_req},
            headers={"Authorization": f"Bearer {auth_token}"},
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
        data_str = params.get("data")
        assert data_str is not None, f"Call skill must have params.data. Got params: {params}"
        try:
            parsed = json.loads(data_str) if isinstance(data_str, str) else data_str
        except (TypeError, json.JSONDecodeError):
            parsed = {}
        assert "contact_name" in parsed, (
            f"Call skill params.data must contain contact_name. Got: {parsed}"
        )
        contact_name = (parsed.get("contact_name") or "").strip()
        assert len(contact_name) > 0, (
            f"contact_name must be non-empty. Got: {parsed}"
        )


class TestPatchFailedCallFlow:
    """Validate patch response when a call fails (contact not found, similar contacts provided)."""

    def test_patch_failed_call_informs_user_with_similar_contacts(
        self, client, auth_token
    ):
        """Real flow: first request is a call; second request is a patch with contact not found + similar contacts."""
        _skip_if_no_gemini_key()

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
        _skip_if_no_gemini_key()

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
