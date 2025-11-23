"""
Embedding service using Cohere API.
"""
import cohere
import os
from typing import List
import config


class EmbeddingService:
    """Generates embeddings using Cohere API."""
    
    def __init__(self):
        self.api_key = os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise Exception("COHERE_API_KEY environment variable not set")
        
        self.client = cohere.Client(self.api_key)
        self.model = "embed-english-light-v3.0"  # 384 dimensions, free tier
        print(f"Cohere embedding service initialized with model: {self.model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Cohere API.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type="search_document"
            )
            return response.embeddings[0]
        except Exception as e:
            raise Exception(f"Error generating embedding with Cohere: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch using Cohere API.
        More efficient than calling generate_embedding multiple times.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"
            )
            return response.embeddings
        except Exception as e:
            raise Exception(f"Error generating embeddings with Cohere: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return config.EMBEDDING_DIMENSION


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
