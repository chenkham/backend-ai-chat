"""
Chat routes for managing chat history.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database.models import (
    SaveMessageRequest, 
    SaveMessageResponse, 
    ChatHistoryResponse
)
from services.chat_service import get_chat_service

router = APIRouter()


@router.post("/save-message", response_model=SaveMessageResponse)
async def save_message(request: SaveMessageRequest):
    """
    Save a chat message (question + answer) to the database.
    """
    try:
        chat_service = get_chat_service()
        
        success = chat_service.save_conversation(
            session_id=request.session_id,
            question=request.question,
            answer=request.answer,
            retrieved_chunks=request.retrieved_chunks
        )
        
        if success:
            return SaveMessageResponse(
                success=True,
                message="Message saved successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save message")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving message: {str(e)}")


@router.get("/chat-history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: Optional[str] = Query(None, description="Session ID to filter by"),
    limit: Optional[int] = Query(None, description="Maximum number of messages to return")
):
    """
    Retrieve chat history, optionally filtered by session.
    """
    try:
        chat_service = get_chat_service()
        
        messages = chat_service.get_history(session_id=session_id, limit=limit)
        
        return ChatHistoryResponse(
            success=True,
            messages=messages,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")


@router.delete("/chat-history/{session_id}")
async def delete_chat_history(session_id: str):
    """
    Delete all messages for a specific session.
    """
    try:
        chat_service = get_chat_service()
        
        deleted_count = chat_service.delete_session_history(session_id)
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} messages",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chat history: {str(e)}")
