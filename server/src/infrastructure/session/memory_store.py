"""
InMemorySessionStore - Simple in-memory session storage
"""

from typing import Dict, Optional

from ...application.interfaces.session_store import ISessionStore
from ...domain.value_objects import SessionContext, TaskType
from ...domain.entities import Question, Answer


class InMemorySessionStore(ISessionStore):
    """
    In-memory session storage using Python dictionaries.
    
    Suitable for:
    - Development and testing
    - Single-process applications
    - Sessions that can be lost on restart
    
    Not suitable for:
    - Production with multiple processes
    - Long-term persistence
    """
    
    def __init__(self):
        self._sessions: Dict[str, SessionContext] = {}
    
    def get_context(self, chat_id: str) -> SessionContext:
        """Get or create session context"""
        if chat_id not in self._sessions:
            self._sessions[chat_id] = SessionContext(chat_id=chat_id)
        return self._sessions[chat_id]
    
    def update_context(
        self,
        chat_id: str,
        question: Question,
        answer: Answer,
    ) -> None:
        """Update session with new Q&A exchange"""
        context = self.get_context(chat_id)
        
        # Add to history
        context.add_exchange(question.text, answer.text)
        
        # Update last task and filters
        if answer.task_type:
            try:
                context.last_task = TaskType.from_string(answer.task_type)
            except ValueError:
                pass
        
        if answer.context and answer.context.documents:
            # Extract filters from first document metadata
            first_doc = answer.context.documents[0]
            from ...domain.value_objects import Filters
            context.last_filters = Filters(
                doc_type=first_doc.metadata.get("doc_type"),
                bloc_name=first_doc.metadata.get("bloc_name"),
                chapter=first_doc.metadata.get("chapter"),
            )
    
    def clear_context(self, chat_id: str) -> None:
        """Clear session context"""
        if chat_id in self._sessions:
            del self._sessions[chat_id]
    
    def exists(self, chat_id: str) -> bool:
        """Check if session exists"""
        return chat_id in self._sessions
    
    def get_all_chat_ids(self) -> list[str]:
        """Get all active chat IDs"""
        return list(self._sessions.keys())
