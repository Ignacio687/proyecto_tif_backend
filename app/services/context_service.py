"""
Context management service for handling AI context building and optimization
"""
from typing import List, Dict, Any, Optional
from app.config import settings
from app.logger import logger
from app.services.interfaces import ContextServiceInterface


class ContextService(ContextServiceInterface):
    """Service responsible for managing and optimizing context for AI interactions"""
    
    def __init__(self):
        self.max_key_context_chars = settings.MAX_KEY_CONTEXT_CHARS
        self.max_conversation_chars = settings.MAX_CONVERSATION_CHARS
        self.max_total_context_chars = settings.MAX_TOTAL_CONTEXT_CHARS
    
    def build_optimized_context(self, 
                              key_context_data: List[Dict[str, Any]], 
                              context_conversations: List[Dict[str, Any]],
                              fixed_context: str) -> str:
        """Build optimized context with character limits and smart prioritization"""
        
        # Start with fixed context
        instruction = fixed_context
        
        # Add key context with optimization
        key_context_section = self._build_key_context_section(key_context_data)
        if key_context_section:
            instruction += "\n\n" + key_context_section
        
        # Add conversation context with optimization
        conversation_section = self._build_conversation_section(context_conversations)
        if conversation_section:
            instruction += "\n\n" + conversation_section
        
        # Final length check and truncation if needed
        instruction = self._ensure_total_length_limit(instruction, fixed_context)
        
        total_length = len(instruction)
        logger.debug(f"Total optimized context length: {total_length} characters (~{total_length//4} tokens)")
        
        return instruction
    
    def _build_key_context_section(self, key_context_data: List[Dict[str, Any]]) -> Optional[str]:
        """Build key context section with character limits and priority sorting"""
        if not key_context_data:
            return None
            
        section = "KEY CONTEXT FROM PREVIOUS IMPORTANT INTERACTIONS:\n"
        key_context_content = ""
        
        # Sort by priority (highest first) and add until limit
        sorted_key_context = sorted(key_context_data, key=lambda x: x.get('context_priority', 0), reverse=True)
        
        for i, context in enumerate(sorted_key_context, 1):
            context_line = f"{i}. [{context.get('timestamp', '')} | priority: {context.get('context_priority', '')}] {context['relevant_info']}\n"
            
            if len(key_context_content) + len(context_line) > self.max_key_context_chars:
                logger.debug(f"Key context truncated at {len(key_context_content)} characters, skipping {len(sorted_key_context) - i + 1} entries")
                break
                
            key_context_content += context_line
        
        return section + key_context_content if key_context_content else None
    
    def _build_conversation_section(self, context_conversations: List[Dict[str, Any]]) -> Optional[str]:
        """Build conversation section with character limits and recency priority"""
        if not context_conversations:
            return None
            
        section = "RECENT CONVERSATION HISTORY:\n"
        conversation_content = ""
        
        # Process recent conversations first (reverse chronological)
        for conv in reversed(context_conversations):
            user_input = conv.get('user_input', '')
            server_reply = conv.get('server_reply', '')
            timestamp = conv.get('timestamp', None)
            
            clean_reply = server_reply
            if clean_reply.lower().startswith('assistant:'):
                clean_reply = clean_reply[len('assistant:'):].strip()
            
            conv_entry = f"User: {user_input} (at {timestamp})\nAssistant: {clean_reply}\n\n"
            
            if len(conversation_content) + len(conv_entry) > self.max_conversation_chars:
                logger.debug(f"Conversation history truncated at {len(conversation_content)} characters")
                break
                
            conversation_content = conv_entry + conversation_content  # Prepend to maintain chronological order
        
        return section + conversation_content if conversation_content else None
    
    def _ensure_total_length_limit(self, instruction: str, fixed_context: str) -> str:
        """Ensure total instruction doesn't exceed maximum length"""
        if len(instruction) <= self.max_total_context_chars:
            return instruction
        
        # If too long, keep fixed context and truncate the rest
        logger.warning(f"Total context too long ({len(instruction)} chars), truncating to preserve fixed context")
        
        available_space = self.max_total_context_chars - len(fixed_context) - 50  # 50 chars buffer
        if available_space <= 0:
            logger.error("Fixed context too long, returning only fixed context")
            return fixed_context
        
        # Truncate and add indication
        truncated = instruction[:self.max_total_context_chars - 50] + "\n\n[Context truncated to fit limits]"
        return truncated
    
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
