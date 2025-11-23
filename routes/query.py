"""
Query route for retrieving relevant chunks from Pinecone.
"""
from fastapi import APIRouter, HTTPException
from database.models import QueryRequest, QueryResponse, RetrievedChunk
from services.embedding_service import get_embedding_service
from services.pinecone_service import get_pinecone_service

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base for relevant chunks.
    
    Steps:
    1. Generate embedding for the query
    2. Search Pinecone for similar vectors
    3. Return top-k chunks with metadata
    """
    try:
        # Get services
        embedding_service = get_embedding_service()
        pinecone_service = get_pinecone_service()
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(request.query)
        
        # Query Pinecone
        results = pinecone_service.query(
            query_embedding=query_embedding,
            top_k=request.top_k
        )
        
        # Format results
        chunks = []
        for result in results:
            chunks.append(RetrievedChunk(
                text=result['text'],
                score=result['score'],
                metadata=result['metadata']
            ))
        
        return QueryResponse(
            success=True,
            query=request.query,
            chunks=chunks,
            message=f"Retrieved {len(chunks)} relevant chunks"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {str(e)}")
