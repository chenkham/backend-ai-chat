"""
Embedding service using Sentence-Transformers.
"""
from sentence_transformers import SentenceTransformer
from typing import List
import config


class EmbeddingService:
    """Generates embeddings using Sentence-Transformers."""
    
    def __init__(self):
        self.model_name = config.EMBEDDING_MODEL_NAME
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Sentence-Transformers model."""
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"Model loaded successfully. Dimension: {config.EMBEDDING_DIMENSION}")
        except Exception as e:
            raise Exception(f"Error loading embedding model: {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if not self.model:
            raise Exception("Embedding model not loaded")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        More efficient than calling generate_embedding multiple times.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if not self.model:
            raise Exception("Embedding model not loaded")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
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
