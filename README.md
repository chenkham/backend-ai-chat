# RAG Chatbot Backend

A complete FastAPI backend for a personal RAG (Retrieval-Augmented Generation) chatbot with PDF processing, semantic search, and chat history management.

## Features

- 📄 **PDF Processing**: Upload and extract text from PDF files
- 🧠 **Semantic Embeddings**: Generate embeddings using Sentence-Transformers (all-MiniLM-L6-v2)
- 🔍 **Vector Search**: Store and retrieve embeddings from Pinecone
- 💬 **Chat History**: Persistent conversation storage in SQLite
- 🚀 **FastAPI**: Modern, fast, async API with automatic documentation
- 🌐 **CORS Enabled**: Ready for Next.js frontend integration

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Sentence-Transformers** - Embedding generation
- **Pinecone** - Vector database
- **PyPDF2** - PDF text extraction
- **SQLite** - Chat history storage
- **Pydantic** - Data validation

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
│
├── database/
│   ├── __init__.py
│   ├── db.py             # SQLite database operations
│   └── models.py         # Pydantic models
│
├── services/
│   ├── __init__.py
│   ├── pdf_processor.py  # PDF text extraction and chunking
│   ├── embedding_service.py  # Sentence-Transformers embeddings
│   ├── pinecone_service.py   # Pinecone vector operations
│   └── chat_service.py   # Chat history management
│
├── routes/
│   ├── __init__.py
│   ├── upload.py         # PDF upload endpoint
│   ├── query.py          # Knowledge base query endpoint
│   └── chat.py           # Chat history endpoints
│
└── utils/
    ├── __init__.py
    └── text_utils.py     # Text processing utilities
```

## Installation

### Prerequisites

- Python 3.8+
- Pinecone account and API key
- Virtual environment (recommended)

### Setup

1. **Clone the repository** (or navigate to backend folder)
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   
   Update the `.env` file with your settings:
   ```env
   # Pinecone Configuration
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=rag
   
   # App Configuration
   UPLOAD_DIR=./uploads
   MAX_FILE_SIZE=10485760  # 10MB
   CHUNK_SIZE=800
   CHUNK_OVERLAP=100
   
   # API Configuration (optional)
   API_HOST=0.0.0.0
   API_PORT=8000
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

## Usage

### Start the Server

```bash
uvicorn main:app --reload --port 8000
```

Or run directly:
```bash
python main.py
```

The API will be available at: `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```http
GET /health
```

Returns server health status.

### PDF Upload

```http
POST /upload-pdf
Content-Type: multipart/form-data

file: <PDF file>
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed document.pdf",
  "chunks_processed": 15,
  "filename": "document.pdf"
}
```

### Query Knowledge Base

```http
POST /query
Content-Type: application/json

{
  "query": "What is the main topic of the document?",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "query": "What is the main topic of the document?",
  "chunks": [
    {
      "text": "Retrieved chunk text...",
      "score": 0.85,
      "metadata": {
        "filename": "document.pdf",
        "chunk_index": 3,
        "source": "pdf"
      }
    }
  ],
  "message": "Retrieved 5 relevant chunks"
}
```

### Save Chat Message

```http
POST /save-message
Content-Type: application/json

{
  "session_id": "user-123",
  "question": "What is this about?",
  "answer": "This document is about...",
  "retrieved_chunks": [...]
}
```

### Get Chat History

```http
GET /chat-history?session_id=user-123
```

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "session_id": "user-123",
      "message_type": "user",
      "content": "What is this about?",
      "timestamp": "2025-11-23T12:00:00",
      "metadata": null
    },
    {
      "id": 2,
      "session_id": "user-123",
      "message_type": "assistant",
      "content": "This document is about...",
      "timestamp": "2025-11-23T12:00:05",
      "metadata": {...}
    }
  ],
  "session_id": "user-123"
}
```

### Delete Chat History

```http
DELETE /chat-history/{session_id}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Your Pinecone API key | Required |
| `PINECONE_INDEX_NAME` | Pinecone index name | `rag` |
| `UPLOAD_DIR` | Directory for uploaded files | `./uploads` |
| `MAX_FILE_SIZE` | Max upload size in bytes | `10485760` (10MB) |
| `CHUNK_SIZE` | Max tokens per chunk | `800` |
| `CHUNK_OVERLAP` | Overlap between chunks | `100` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

### Embedding Model

The backend uses `sentence-transformers/all-MiniLM-L6-v2` which:
- Produces 384-dimensional embeddings
- Is lightweight and fast
- Works well for semantic search
- First run will download the model (~80MB)

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --port 8000
```

The `--reload` flag enables auto-reloading on code changes.

### Testing with curl

**Upload a PDF:**
```bash
curl -X POST http://localhost:8000/upload-pdf \
  -F "file=@sample.pdf"
```

**Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test question", "top_k": 3}'
```

**Get History:**
```bash
curl http://localhost:8000/chat-history?session_id=test-123
```

## Database

The backend uses SQLite to store chat history. The database file is created automatically at `chat_history.db` in the backend directory.

### Schema

**chat_history** table:
- `id`: Primary key (auto-increment)
- `session_id`: Session identifier
- `message_type`: "user" or "assistant"
- `content`: Message content
- `timestamp`: When the message was created
- `metadata`: JSON metadata (e.g., retrieved chunks)

## Pinecone Setup

1. Create a Pinecone account at https://www.pinecone.io/
2. Create a new index or use an existing one
3. The backend will automatically create the index if it doesn't exist
4. Index specs:
   - Dimension: 384 (for all-MiniLM-L6-v2)
   - Metric: cosine
   - Cloud: AWS (us-east-1)

## Error Handling

The API includes comprehensive error handling:
- File validation (type, size)
- Service initialization errors
- Database connection errors
- Pinecone API errors
- Invalid requests

All errors return appropriate HTTP status codes and descriptive messages.

## Production Deployment

For production deployment:

1. Set `API_HOST` to `0.0.0.0`
2. Use a production ASGI server (uvicorn with workers)
3. Set up HTTPS/TLS
4. Configure proper CORS origins
5. Use environment-specific `.env` files
6. Set up monitoring and logging

Example production command:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
