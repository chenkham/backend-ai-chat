"""
Chat service for managing chat history in SQLite.
"""
from typing import List, Dict, Any, Optional
from database.db import get_database
from database.models import ChatMessage


class ChatService:
    """Manages chat history operations."""
    
    def __init__(self):
        self.db = get_database()
    
    def save_conversation(
        self,
        session_id: str,
        question: str,
        answer: str,
        retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Save a complete conversation (question + answer) to the database.
        
        Args:
            session_id: Session identifier
            question: User's question
            answer: Assistant's answer
            retrieved_chunks: Optional list of retrieved chunks for context
            
        Returns:
            True if successful
        """
        try:
            # Save user question
            self.db.save_message(
                session_id=session_id,
                message_type="user",
                content=question,
                metadata=None
            )
            
            # Save assistant answer with retrieved chunks as metadata
            metadata = {"retrieved_chunks": retrieved_chunks} if retrieved_chunks else None
            self.db.save_message(
                session_id=session_id,
                message_type="assistant",
                content=answer,
                metadata=metadata
            )
            
            return True
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
            return False
    
    def get_history(
        self, 
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Retrieve chat history.
        
        Args:
            session_id: Optional session filter
            limit: Optional limit on number of messages
            
        Returns:
            List of ChatMessage objects
        """
        try:
            messages_data = self.db.get_chat_history(session_id, limit)
            
            # Convert to Pydantic models
            messages = []
            for msg_data in messages_data:
                messages.append(ChatMessage(**msg_data))
            
            return messages
        except Exception as e:
            print(f"Error retrieving history: {str(e)}")
            return []
    
    def delete_session_history(self, session_id: str) -> int:
        """
        Delete all messages for a session.
        
        Args:
            session_id: Session to delete
            
        Returns:
            Number of messages deleted
        """
        try:
            return self.db.delete_session(session_id)
        except Exception as e:
            print(f"Error deleting session: {str(e)}")
            return 0


# Singleton instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create the chat service singleton."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
