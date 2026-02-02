"""
Unit tests for context service timezone conversion.
Datetimes are stored in UTC; when user_timezone is provided they are formatted in that timezone.
"""
from datetime import datetime, timezone
import pytest

from app.services.context_service import (
    _format_timestamp,
    ContextService,
)


class TestFormatTimestamp:
    """Tests for _format_timestamp (UTC in DB; format in user TZ or UTC)."""

    def test_none_returns_empty(self):
        assert _format_timestamp(None) == ""
        assert _format_timestamp(None, "America/Argentina/Buenos_Aires") == ""

    def test_non_datetime_returns_str(self):
        assert _format_timestamp("2025-01-15 12:00") == "2025-01-15 12:00"
        assert _format_timestamp(123) == "123"

    def test_naive_datetime_treated_as_utc(self):
        dt = datetime(2025, 1, 15, 12, 0, 0)
        result = _format_timestamp(dt)
        assert "2025-01-15" in result
        assert "12:00" in result
        assert "UTC" in result

    def test_aware_utc_no_user_tz_returns_utc_format(self):
        dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = _format_timestamp(dt)
        assert "2025-01-15" in result
        assert "12:00" in result
        assert "UTC" in result

    def test_aware_utc_with_valid_user_tz_returns_local_format(self):
        dt = datetime(2025, 1, 15, 15, 0, 0, tzinfo=timezone.utc)  # 15:00 UTC
        result = _format_timestamp(dt, "America/Argentina/Buenos_Aires")
        assert "2025-01-15" in result
        # Buenos Aires is UTC-3 in January
        assert "12:00" in result
        assert "UTC" not in result or "ART" in result or "-03" in result

    def test_aware_utc_with_europe_london(self):
        dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = _format_timestamp(dt, "Europe/London")
        assert "2025-01-15" in result
        # London is UTC+0 in January (GMT)
        assert "12:00" in result

    def test_invalid_user_tz_fallback_to_utc(self):
        dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = _format_timestamp(dt, "Invalid/Timezone")
        assert "2025-01-15" in result
        assert "12:00" in result
        assert "UTC" in result


class TestBuildOptimizedContextTimezone:
    """Tests that build_optimized_context formats timestamps in user_timezone when provided."""

    def test_key_context_timestamp_in_user_tz(self):
        service = ContextService()
        key_context_data = [
            {
                "relevant_info": "User prefers Spanish",
                "context_priority": 10,
                "timestamp": datetime(2025, 1, 15, 15, 0, 0, tzinfo=timezone.utc),
            }
        ]
        result = service.build_optimized_context(
            key_context_data,
            [],
            "Fixed context.",
            user_timezone="America/Argentina/Buenos_Aires",
        )
        assert "KEY CONTEXT" in result
        assert "User prefers Spanish" in result
        assert "2025-01-15" in result
        assert "12:00" in result  # UTC-3

    def test_conversation_timestamp_in_user_tz(self):
        service = ContextService()
        context_conversations = [
            {
                "user_input": "Hello",
                "server_reply": "Hi",
                "timestamp": datetime(2025, 1, 15, 15, 0, 0, tzinfo=timezone.utc),
            }
        ]
        result = service.build_optimized_context(
            [],
            context_conversations,
            "Fixed context.",
            user_timezone="Europe/London",
        )
        assert "RECENT CONVERSATION" in result
        assert "Hello" in result
        assert "2025-01-15" in result
        assert "15:00" in result  # London = UTC in winter

    def test_no_user_tz_uses_utc_in_output(self):
        service = ContextService()
        context_conversations = [
            {
                "user_input": "Hi",
                "server_reply": "Hello",
                "timestamp": datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            }
        ]
        result = service.build_optimized_context(
            [],
            context_conversations,
            "Fixed context.",
            user_timezone=None,
        )
        assert "12:00" in result
        assert "UTC" in result
