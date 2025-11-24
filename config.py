"""
Configuration settings for the RAG chatbot backend.
Loads environment variables and provides configuration constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Embedding Configuration
EMBEDDING_DIMENSION = 384  # Dimension for Cohere embed-english-light-v3.0

# File Upload Configuration
# Use /tmp for serverless/container environments (Render, Vercel, etc.)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 31457280))  # 30MB default

# Text Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))

# Database Configuration
# Use /tmp for serverless/container environments
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "/tmp/chat_history.db"))

# Appwrite Configuration
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID", "chat-db")
APPWRITE_COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_ID", "chat-history")
APPWRITE_BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID", "pdf-storage")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8001))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001,http://0.0.0.0:8001").split(",")

# Retrieval Configuration
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", 5))
