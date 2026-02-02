"""
Unit tests for assistant service timezone conversion.
Datetimes are stored in UTC; when timezone is provided they are converted for API response (ISO format).
"""
from datetime import datetime, timezone
import pytest

from app.services.assistant_service import _format_timestamp_for_response


class TestFormatTimestampForResponse:
    """Tests for _format_timestamp_for_response (UTC in DB; ISO in user TZ or UTC)."""

    def test_none_returns_empty(self):
        assert _format_timestamp_for_response(None) == ""
        assert _format_timestamp_for_response(None, "America/Argentina/Buenos_Aires") == ""

    def test_non_datetime_returns_str(self):
        assert _format_timestamp_for_response("2025-01-15T12:00:00") == "2025-01-15T12:00:00"

    def test_naive_datetime_treated_as_utc(self):
        dt = datetime(2025, 1, 15, 12, 0, 0)
        result = _format_timestamp_for_response(dt)
        assert "2025-01-15" in result
        assert "12:00" in result
        assert "+00:00" in result or "Z" in result or result.endswith("00:00")

    def test_aware_utc_no_user_tz_returns_iso_utc(self):
        dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = _format_timestamp_for_response(dt)
        assert "2025-01-15" in result
        assert "12:00" in result
        assert "+00:00" in result or "Z" in result

    def test_aware_utc_with_valid_user_tz_returns_iso_local(self):
        dt = datetime(2025, 1, 15, 15, 0, 0, tzinfo=timezone.utc)  # 15:00 UTC
        result = _format_timestamp_for_response(dt, "America/Argentina/Buenos_Aires")
        assert "2025-01-15" in result
        # Buenos Aires UTC-3 -> 12:00 local
        assert "12:00" in result
        assert "-03" in result or "+00:00" not in result

    def test_invalid_user_tz_fallback_to_utc_iso(self):
        dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = _format_timestamp_for_response(dt, "Invalid/Timezone")
        assert "2025-01-15" in result
        assert "12:00" in result
        assert "+00:00" in result or "Z" in result
