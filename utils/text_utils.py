"""
Text processing utilities for cleaning and chunking.
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters but keep everything else (unicode support)
    text = "".join(ch for ch in text if ch.isprintable())
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text.
    Simple approximation: ~4 characters per token.
    
    Args:
        text: Text to estimate tokens for
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def chunk_text(text: str, max_tokens: int = 800, overlap: int = 100) -> List[str]:
    """
    Split text into chunks with overlap for better context preservation.
    
    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Convert tokens to approximate characters (4 chars per token)
    max_chars = max_tokens * 4
    overlap_chars = overlap * 4
    
    # Split text into sentences for better chunking
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed max_chars, start a new chunk
        if len(current_chunk) + len(sentence) > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from previous chunk
            if overlap_chars > 0 and len(current_chunk) > overlap_chars:
                current_chunk = current_chunk[-overlap_chars:] + " " + sentence
            else:
                current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def validate_chunk(chunk: str, min_length: int = 10) -> bool:
    """
    Validate if a chunk is meaningful (not too short).
    
    Args:
        chunk: Text chunk to validate
        min_length: Minimum character length
        
    Returns:
        True if chunk is valid, False otherwise
    """
    return len(chunk.strip()) >= min_length
