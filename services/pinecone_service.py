"""
Pinecone service for vector storage and retrieval.
"""
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any
import config
import uuid


class PineconeService:
    """Manages Pinecone vector database operations."""
    
    def __init__(self):
        self.api_key = config.PINECONE_API_KEY
        self.index_name = config.PINECONE_INDEX_NAME
        self.dimension = config.EMBEDDING_DIMENSION
        self.pc = None
        self.index = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone client and connect to index."""
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists, create if not
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"Index {self.index_name} created successfully")
            
            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            print(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            raise Exception(f"Error initializing Pinecone: {str(e)}")
    
    def upsert_embeddings(
        self, 
        embeddings: List[List[float]], 
        metadata_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Upsert embeddings with metadata to Pinecone.
        
        Args:
            embeddings: List of embedding vectors
            metadata_list: List of metadata dicts (one per embedding)
            
        Returns:
            Upsert response from Pinecone
        """
        if len(embeddings) != len(metadata_list):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        try:
            # Create vectors with unique IDs
            vectors = []
            for i, (embedding, metadata) in enumerate(zip(embeddings, metadata_list)):
                vector_id = str(uuid.uuid4())
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            # Upsert to Pinecone
            response = self.index.upsert(vectors=vectors)
            
            print(f"Upserted {len(vectors)} vectors to Pinecone")
            return response
            
        except Exception as e:
            raise Exception(f"Error upserting to Pinecone: {str(e)}")
    
    def query(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filter_dict: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar vectors.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of matches with scores and metadata
        """
        try:
            query_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            results = []
            for match in query_response.matches:
                results.append({
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', ''),
                    'metadata': match.metadata
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error querying Pinecone: {str(e)}")
    
    def delete_all(self):
        """Delete all vectors from the index (use with caution)."""
        try:
            self.index.delete(delete_all=True)
            print("All vectors deleted from Pinecone index")
        except Exception as e:
            raise Exception(f"Error deleting from Pinecone: {str(e)}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            raise Exception(f"Error getting index stats: {str(e)}")


# Singleton instance
_pinecone_service = None


def get_pinecone_service() -> PineconeService:
    """Get or create the Pinecone service singleton."""
    global _pinecone_service
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    return _pinecone_service
