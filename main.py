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
