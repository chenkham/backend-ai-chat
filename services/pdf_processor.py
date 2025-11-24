"""
PDF processing service with OCR support for scanned documents.
"""
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any
import config
from utils.text_utils import clean_text, chunk_text, validate_chunk
import requests
import os


class PDFProcessor:
    """Handles PDF text extraction, OCR, and chunking."""
    
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
        self.ocr_api_key = os.getenv("OCR_API_KEY", "K87899142388957")  # Free OCR.space API key
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF using pdfplumber (better than pypdf).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        try:
            text = ""
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                    except Exception as e:
                        print(f"Error extracting text from page {page_num}: {e}")
                        continue
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def ocr_pdf_page(self, pdf_path: Path, page_num: int = 0) -> str:
        """
        Perform OCR on a PDF page using OCR.space API.
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number to OCR (0-indexed)
            
        Returns:
            OCR text from the page
        """
        try:
            # OCR.space free API endpoint
            url = "https://api.ocr.space/parse/image"
            
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                payload = {
                    'apikey': self.ocr_api_key,
                    'language': 'eng',
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'scale': True,
                    'OCREngine': 2,  # Engine 2 is more accurate
                }
                
                response = requests.post(url, files=files, data=payload, timeout=30)
                result = response.json()
                
                if result.get('IsErroredOnProcessing'):
                    print(f"OCR error: {result.get('ErrorMessage')}")
                    return ""
                
                # Extract text from OCR result
                ocr_text = ""
                if result.get('ParsedResults'):
                    for parsed in result['ParsedResults']:
                        ocr_text += parsed.get('ParsedText', '')
                
                return ocr_text.strip()
                
        except Exception as e:
            print(f"OCR failed: {e}")
            return ""
    
    def process_pdf(self, pdf_path: Path, filename: str) -> List[Dict[str, Any]]:
        """
        Process a PDF: extract text, use OCR if needed, clean, and chunk it.
        
        Args:
            pdf_path: Path to the PDF file
            filename: Original filename for metadata
            
        Returns:
            List of chunks with metadata
        """
        # Try regular text extraction first
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        # If no text found, try OCR
        if not raw_text or len(raw_text.strip()) < 50:
            print(f"⚠️ No text found in {filename}, attempting OCR...")
            ocr_text = self.ocr_pdf_page(pdf_path)
            
            if ocr_text and len(ocr_text.strip()) > 20:
                raw_text = ocr_text
                print(f"✅ OCR successful, extracted {len(ocr_text)} characters")
            else:
                print(f"❌ OCR failed or no text found")
                return []
        
        if not raw_text:
            print(f"Warning: No text extracted from {filename}")
            return []
        
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
            
        # Upload to Appwrite Storage if configured
        try:
            if config.APPWRITE_PROJECT_ID:
                from services.appwrite_service import get_appwrite_service
                appwrite = get_appwrite_service()
                if appwrite:
                    file_id = appwrite.upload_file(file_content, filename)
                    print(f"Uploaded to Appwrite Storage: {file_id}")
        except Exception as e:
            print(f"Failed to upload to Appwrite: {e}")
        
        return file_path


# Singleton instance
_pdf_processor = None


def get_pdf_processor() -> PDFProcessor:
    """Get or create the PDF processor singleton."""
    global _pdf_processor
    if _pdf_processor is None:
        _pdf_processor = PDFProcessor()
    return _pdf_processor
