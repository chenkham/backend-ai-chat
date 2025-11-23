"""
PDF processing service for text extraction and chunking.
"""
from PyPDF2 import PdfReader
from pathlib import Path
from typing import List, Dict, Any
import config
from utils.text_utils import clean_text, chunk_text, validate_chunk


class PDFProcessor:
    """Handles PDF text extraction and chunking."""
    
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        try:
            reader = PdfReader(str(pdf_path))
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def process_pdf(self, pdf_path: Path, filename: str) -> List[Dict[str, Any]]:
        """
        Process a PDF: extract text, clean, and chunk it.
        
        Args:
            pdf_path: Path to the PDF file
            filename: Original filename for metadata
            
        Returns:
            List of chunks with metadata
        """
        # Extract text
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        # Clean text
        cleaned_text = clean_text(raw_text)
        
        # Chunk text
        chunks = chunk_text(
            cleaned_text, 
            max_tokens=self.chunk_size, 
            overlap=self.chunk_overlap
        )
        
        # Create chunk objects with metadata
        processed_chunks = []
        for idx, chunk in enumerate(chunks):
            if validate_chunk(chunk):
                processed_chunks.append({
                    'text': chunk,
                    'metadata': {
                        'filename': filename,
                        'chunk_index': idx,
                        'total_chunks': len(chunks),
                        'source': 'pdf'
                    }
                })
        
        return processed_chunks
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Path:
        """
        Save uploaded file to the upload directory.
        
        Args:
            file_content: Raw file content
            filename: Name of the file
            
        Returns:
            Path to the saved file
        """
        file_path = config.UPLOAD_DIR / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path


# Singleton instance
_pdf_processor = None


def get_pdf_processor() -> PDFProcessor:
    """Get or create the PDF processor singleton."""
    global _pdf_processor
    if _pdf_processor is None:
        _pdf_processor = PDFProcessor()
    return _pdf_processor
