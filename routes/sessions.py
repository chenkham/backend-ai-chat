"""
Sessions routes for managing chat sessions.
"""
from fastapi import APIRouter, HTTPException
from database.models import (
    Session,
    CreateSessionRequest,
    SessionsResponse,
    MessagesResponse,
    ChatMessage
)
from database.db import get_database
import uuid

router = APIRouter()


@router.post("/sessions", response_model=Session)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session."""
    try:
        db = get_database()
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create session in database
        session_data = db.create_session(
            session_id=session_id,
            name=request.name,
            mode=request.mode,
            pdf_id=request.pdf_id
        )
        
        return Session(**session_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/sessions", response_model=SessionsResponse)
async def get_sessions():
    """Get all chat sessions."""
    try:
        db = get_database()
        sessions_data = db.get_all_sessions()
        
        sessions = [Session(**session) for session in sessions_data]
        
        return SessionsResponse(sessions=sessions)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")


@router.get("/sessions/{session_id}/messages", response_model=MessagesResponse)
async def get_session_messages(session_id: str):
    """Get all messages for a specific session."""
    try:
        db = get_database()
        
        # Check if session exists
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get messages for this session
        messages_data = db.get_chat_history(session_id)
        
        messages = [ChatMessage(**msg) for msg in messages_data]
        
        return MessagesResponse(messages=messages)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages."""
    try:
        db = get_database()
        
        # Check if session exists
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete session and messages
        db.delete_session_and_messages(session_id)
        
        return {
            "success": True,
            "message": f"Session {session_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
