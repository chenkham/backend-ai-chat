"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import config

# Import routers
from routes.upload import router as upload_router
from routes.query import router as query_router
from routes.chat import router as chat_router
from routes.sessions import router as sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize services
    print("=" * 50)
    print("🚀 Starting RAG Chatbot Backend")
    print("=" * 50)
    
    # Import services to trigger initialization
    from services.embedding_service import get_embedding_service
    from services.pinecone_service import get_pinecone_service
    from database.db import get_database
    
    # Initialize services
    print("\n📚 Initializing services...")
    get_database()
    print("✓ Database initialized")
    
    get_embedding_service()
    print("✓ Embedding service loaded")
    
    get_pinecone_service()
    print("✓ Pinecone service connected")
    
    print("\n✅ All services initialized successfully")
    print(f"📡 Server running on http://{config.API_HOST}:{config.API_PORT}")
    print("=" * 50)
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down RAG Chatbot Backend")


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend",
    description="Backend API for a personal RAG chatbot with PDF processing and vector search",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router, tags=["PDF Upload"])
app.include_router(query_router, tags=["Query"])
app.include_router(chat_router, tags=["Chat History"])
app.include_router(sessions_router, tags=["Sessions"])


# Wrapper endpoints for frontend compatibility

from fastapi import UploadFile, File
from database.models import QueryRequest, RetrievedChunk, ChatMessage
from services.embedding_service import get_embedding_service
from services.pinecone_service import get_pinecone_service
from database.db import get_database


from pydantic import BaseModel

class RetrieveRequest(BaseModel):
    query: str
    pdf_id: str = None
    top_k: int = 5

@app.post("/retrieve", tags=["Query"])
async def retrieve_chunks(request: RetrieveRequest):
    """
    Retrieve chunks for a query (wrapper for /query endpoint).
    Frontend compatibility endpoint.
    """
    try:
        embedding_service = get_embedding_service()
        pinecone_service = get_pinecone_service()
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(request.query)
        
        # Query Pinecone (optionally filter by pdf_id if provided)
        filter_dict = {"filename": request.pdf_id} if request.pdf_id else None
        results = pinecone_service.query(
            query_embedding=query_embedding,
            top_k=request.top_k,
            filter_dict=filter_dict
        )
        
        # Return just the text chunks
        chunks = [result['text'] for result in results]
        
        return {"chunks": chunks}
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error retrieving chunks: {str(e)}")


class SaveMessageWrapperRequest(BaseModel):
    session_id: str
    role: str
    content: str

@app.post("/messages", response_model=ChatMessage, tags=["Chat History"])
async def save_message_endpoint(request: SaveMessageWrapperRequest):
    """
    Save a message (wrapper for chat service).
    Frontend compatibility endpoint.
    """
    try:
        db = get_database()
        
        # Save message
        message_id = db.save_message(
            session_id=request.session_id,
            message_type=request.role,
            content=request.content
        )
        
        # Update session timestamp
        db.update_session_timestamp(request.session_id)
        
        from datetime import datetime
        return ChatMessage(
            id=str(message_id),
            session_id=request.session_id,
            message_type=request.role,  # Corrected from role to message_type to match model
            content=request.content,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error saving message: {str(e)}")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot Backend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
