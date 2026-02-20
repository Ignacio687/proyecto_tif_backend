"""
Unit tests for DTOs (skill params validation).
Covers SendMessageParams and CallContactParams exactly-one-identifier rules.
"""
import pytest
from pydantic import ValidationError

from app.models.dtos import CallContactParams, SendMessageParams


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
            SendMessageParams(recipient="John")

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
