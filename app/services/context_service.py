"""
Context management service for handling AI context building and optimization.
Datetimes are stored in UTC in the DB; when user_timezone is provided they are
formatted in that timezone for context and display.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional
from app.config import settings
from app.logger import logger
from app.services.interfaces import ContextServiceInterface


def _format_timestamp(dt: Any, user_timezone: Optional[str] = None) -> str:
    """Format a datetime (UTC in DB) for display; convert to user_timezone if provided, else UTC."""
    if dt is None:
        return ""
    if not isinstance(dt, datetime):
        return str(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if user_timezone:
        try:
            tz = ZoneInfo(user_timezone)
            local = dt.astimezone(tz)
            return local.strftime("%A, %Y-%m-%d %H:%M %Z")
        except Exception as e:
            logger.debug("Invalid timezone %s: %s", user_timezone, e)
    return dt.strftime("%A, %Y-%m-%d %H:%M UTC")


class ContextService(ContextServiceInterface):
    """Service responsible for managing and optimizing context for AI interactions"""
    
    def __init__(self):
        self.max_key_context_chars = settings.MAX_KEY_CONTEXT_CHARS
        self.max_conversation_chars = settings.MAX_CONVERSATION_CHARS
        self.max_total_context_chars = settings.MAX_TOTAL_CONTEXT_CHARS
    
    def build_optimized_context(self, 
                              key_context_data: List[Dict[str, Any]], 
                              context_conversations: List[Dict[str, Any]],
                              fixed_context: str,
                              user_timezone: Optional[str] = None) -> str:
        """Build optimized context with character limits and smart prioritization.

        - Fixed context is always preserved.
        - Key context: most important first (by priority); truncated only by max_key_context_chars.
        - Conversation history: newest first; truncated only by max_conversation_chars.
        Sections are independent—they do not truncate one another. When key context is empty we
        simply omit that section; when conversation is empty we omit that section. No final-string
        truncation; total length = key section + conversation section.
        user_timezone: if provided, timestamps are formatted in this timezone (stored as UTC in DB).
        """
        # Start with fixed context
        instruction = fixed_context

        # Order: KEY CONTEXT first, then RECENT CONVERSATION HISTORY
        key_context_section = self._build_key_context_section(key_context_data, user_timezone)
        if key_context_section:
            instruction += "\n\n" + key_context_section

        conversation_section = self._build_conversation_section(context_conversations, user_timezone)
        if conversation_section:
            instruction += "\n\n" + conversation_section

        # No final string truncation: fixed context is always preserved; key context and conversation
        # are each truncated only by their own limits (max_key_context_chars, max_conversation_chars).
        return instruction
    
    def _build_key_context_section(
        self, key_context_data: List[Dict[str, Any]], user_timezone: Optional[str] = None
    ) -> Optional[str]:
        """Build key context section: most important first (by priority), up to max_key_context_chars. When empty, returns None (no section)."""
        if not key_context_data:
            return None
            
        section = "KEY CONTEXT FROM PREVIOUS IMPORTANT INTERACTIONS:\n"
        key_context_content = ""
        
        # Sort by priority (highest first) and add until limit
        sorted_key_context = sorted(key_context_data, key=lambda x: x.get('context_priority', 0), reverse=True)
        
        for i, context in enumerate(sorted_key_context, 1):
            ts_str = _format_timestamp(context.get("timestamp"), user_timezone)
            context_line = f"{i}. [{ts_str} | priority: {context.get('context_priority', '')}] {context['relevant_info']}\n"
            
            if len(key_context_content) + len(context_line) > self.max_key_context_chars:
                break
                
            key_context_content += context_line
        
        return section + key_context_content if key_context_content else None
    
    def _build_conversation_section(
        self, context_conversations: List[Dict[str, Any]], user_timezone: Optional[str] = None
    ) -> Optional[str]:
        """Build conversation section: newest first, up to max_conversation_chars. When empty, returns None (no section). Output order is older → newer. context_conversations is assumed newest-first (e.g. get_last_conversations)."""
        if not context_conversations:
            return None
            
        section = "RECENT CONVERSATION HISTORY (order: older → newer; last exchange is the most recent):\n"
        # Collect entries from newest to oldest until we hit the char limit
        entries: List[str] = []
        total_chars = 0
        for conv in context_conversations:  # newest first
            user_input = conv.get('user_input', '')
            server_reply = conv.get('server_reply', '')
            ts_str = _format_timestamp(conv.get('timestamp'), user_timezone)
            
            clean_reply = server_reply
            if clean_reply.lower().startswith('assistant:'):
                clean_reply = clean_reply[len('assistant:'):].strip()
            
            conv_entry = f"User: {user_input} (at {ts_str})\nAssistant: {clean_reply}\n\n"
            if total_chars + len(conv_entry) > self.max_conversation_chars:
                break
            entries.append(conv_entry)
            total_chars += len(conv_entry)
        # Chronological order (oldest first, newest last) for the model
        conversation_content = "".join(reversed(entries))
        return section + conversation_content if conversation_content else None
    
    def calculate_context_stats(self, key_context_data: List[Dict[str, Any]], 
                               context_conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics about context usage"""
        key_context_chars = sum(len(str(ctx.get('relevant_info', ''))) for ctx in key_context_data)
        conversation_chars = sum(len(str(conv.get('user_input', '')) + str(conv.get('server_reply', ''))) 
                               for conv in context_conversations)
        
        return {
            "key_context_entries": len(key_context_data),
            "key_context_chars": key_context_chars,
            "conversation_entries": len(context_conversations),
            "conversation_chars": conversation_chars,
            "total_dynamic_chars": key_context_chars + conversation_chars,
            "within_limits": {
                "key_context": key_context_chars <= self.max_key_context_chars,
                "conversations": conversation_chars <= self.max_conversation_chars,
                "total": (key_context_chars + conversation_chars) <= self.max_total_context_chars
            }
        }
