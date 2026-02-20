"""
Unit tests for DTOs (skill params validation).
Covers SendMessageParams, CallContactParams, and CreateReminderParams validation rules.
"""
import pytest
from pydantic import ValidationError

from app.models.dtos import CallContactParams, SendMessageParams, CreateReminderParams


class TestSendMessageParams:
    """SendMessageParams: message required; exactly one of recipient or recipient_phone."""

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"message": "Hello", "recipient": "John"},
            {"message": "Hi there", "recipient_phone": "+54 11 1234-5678"},
            {"message": "x", "recipient": "María"},
        ],
    )
    def test_valid_recipient_only_or_recipient_phone_only(self, kwargs):
        """recipient only or recipient_phone only (with message) is valid."""
        obj = SendMessageParams(**kwargs)
        assert obj.message == kwargs["message"]
        if "recipient" in kwargs:
            assert obj.recipient == kwargs["recipient"]
            assert obj.recipient_phone is None
        else:
            assert obj.recipient_phone == kwargs["recipient_phone"]
            assert obj.recipient is None

    def test_both_recipient_and_recipient_phone_raises(self):
        """Both recipient and recipient_phone set raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SendMessageParams(message="Hi", recipient="John", recipient_phone="5551234")
        assert "exactly one" in str(exc_info.value).lower() or "recipient" in str(exc_info.value).lower()

    def test_neither_recipient_nor_recipient_phone_raises(self):
        """Only message (no recipient, no recipient_phone) raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SendMessageParams(message="Hi")
        assert "either" in str(exc_info.value).lower() or "recipient" in str(exc_info.value).lower()

    def test_message_missing_raises(self):
        """Missing message raises ValidationError."""
        with pytest.raises(ValidationError):
            SendMessageParams(**{"recipient": "John"})

    def test_whitespace_only_recipient_treated_as_not_provided(self):
        """Whitespace-only recipient is normalized to None; then neither set raises."""
        with pytest.raises(ValidationError):
            SendMessageParams(message="Hi", recipient="   ", recipient_phone=None)

    def test_whitespace_only_recipient_phone_treated_as_not_provided(self):
        """Whitespace-only recipient_phone is normalized to None; then neither set raises."""
        with pytest.raises(ValidationError):
            SendMessageParams(message="Hi", recipient=None, recipient_phone="  \t  ")


class TestCallContactParams:
    """CallContactParams: exactly one of contact_name or contact_phone."""

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"contact_name": "John"},
            {"contact_phone": "+54 11 1234-5678"},
            {"contact_name": "María"},
        ],
    )
    def test_valid_contact_name_only_or_contact_phone_only(self, kwargs):
        """contact_name only or contact_phone only is valid."""
        obj = CallContactParams(**kwargs)
        if "contact_name" in kwargs:
            assert obj.contact_name == kwargs["contact_name"]
            assert obj.contact_phone is None
        else:
            assert obj.contact_phone == kwargs["contact_phone"]
            assert obj.contact_name is None

    def test_both_contact_name_and_contact_phone_raises(self):
        """Both contact_name and contact_phone set raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CallContactParams(contact_name="John", contact_phone="5551234")
        assert "exactly one" in str(exc_info.value).lower() or "contact" in str(exc_info.value).lower()

    def test_neither_contact_name_nor_contact_phone_raises(self):
        """Neither contact_name nor contact_phone raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CallContactParams()
        assert "either" in str(exc_info.value).lower() or "contact" in str(exc_info.value).lower()


class TestCreateReminderParams:
    """CreateReminderParams: title required; exactly one of datetime or delay_minutes."""

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"title": "Tomar la pastilla", "datetime": "2025-02-21T09:00:00"},
            {"title": "Llamar a Juan", "datetime": "2025-02-21 15:00"},
            {"title": "Salir", "delay_minutes": 30},
            {"title": "Reunión", "delay_minutes": 60, "description": "Con el equipo"},
        ],
    )
    def test_valid_title_with_datetime_or_delay_only(self, kwargs):
        """title + datetime only, or title + delay_minutes only (optionally description) is valid."""
        obj = CreateReminderParams(**kwargs)
        assert obj.title == kwargs["title"]
        if "datetime" in kwargs:
            assert obj.datetime == kwargs["datetime"]
            assert obj.delay_minutes is None
        else:
            assert obj.delay_minutes == kwargs["delay_minutes"]
            assert obj.datetime is None
        if "description" in kwargs:
            assert obj.description == kwargs["description"]

    def test_both_datetime_and_delay_minutes_raises(self):
        """Both datetime and delay_minutes set raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CreateReminderParams(
                title="Test",
                datetime="2025-02-21 10:00",
                delay_minutes=30,
            )
        assert "exactly one" in str(exc_info.value).lower() or "datetime" in str(exc_info.value).lower()

    def test_neither_datetime_nor_delay_minutes_raises(self):
        """Only title (no datetime, no delay_minutes) raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CreateReminderParams(title="Solo título")
        assert "either" in str(exc_info.value).lower() or "datetime" in str(exc_info.value).lower()

    def test_empty_title_raises(self):
        """Empty title raises ValidationError (min_length=1)."""
        with pytest.raises(ValidationError):
            CreateReminderParams(title="", datetime="2025-02-21 10:00")

    def test_delay_minutes_zero_treated_as_not_provided(self):
        """delay_minutes=0 with no datetime is invalid (need positive delay or datetime)."""
        with pytest.raises(ValidationError):
            CreateReminderParams(title="Test", delay_minutes=0)

    def test_delay_minutes_negative_raises(self):
        """delay_minutes < 1 raises ValidationError (ge=1)."""
        with pytest.raises(ValidationError):
            CreateReminderParams(title="Test", delay_minutes=-1)

    def test_description_optional(self):
        """description can be omitted or None."""
        obj = CreateReminderParams(title="X", delay_minutes=5)
        assert obj.description is None
        obj2 = CreateReminderParams(title="Y", datetime="2025-02-21 12:00", description="Optional body")
        assert obj2.description == "Optional body"
