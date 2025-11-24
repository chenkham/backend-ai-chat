"""
Pydantic models for request/response validation and data structures.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Model for a single chat message."""
    id: Optional[str] = None
    session_id: str
    message_type: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class PDFUploadResponse(BaseModel):
    """Response after PDF upload and processing."""
    success: bool
    message: str
    chunks_processed: int
    filename: str
    pdf_id: Optional[str] = None
    number_of_chunks: Optional[int] = None


class QueryRequest(BaseModel):
    """Request model for querying the knowledge base."""
    query: str = Field(..., min_length=1, description="The user's question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    session_id: Optional[str] = Field(default=None, description="Optional session ID for context")


class RetrievedChunk(BaseModel):
    """Model for a retrieved chunk with metadata."""
    text: str
    score: float
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    """Response model for query results."""
    success: bool
    query: str
    chunks: List[RetrievedChunk]
    message: Optional[str] = None


class SaveMessageRequest(BaseModel):
    """Request to save a chat message."""
    session_id: str
    question: str
    answer: str
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None


class SaveMessageResponse(BaseModel):
    """Response after saving a message."""
    success: bool
    message: str


class ChatHistoryResponse(BaseModel):
    """Response with chat history."""
    success: bool
    messages: List[ChatMessage]
    session_id: Optional[str] = None


class Session(BaseModel):
    """Model for a chat session."""
    id: str
    name: str
    mode: str  # "chat" or "pdf"
    pdf_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    name: str
    mode: str = Field(..., pattern="^(chat|pdf)$")
    pdf_id: Optional[str] = None


class SessionsResponse(BaseModel):
    """Response with list of sessions."""
    sessions: List[Session]


class MessagesResponse(BaseModel):
    """Response with messages for a session."""
    messages: List[ChatMessage]
