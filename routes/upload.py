"""
Upload route for PDF file processing.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from database.models import PDFUploadResponse
from services.pdf_processor import get_pdf_processor
from services.embedding_service import get_embedding_service
from services.pinecone_service import get_pinecone_service
import config

router = APIRouter()


@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    
    Steps:
    1. Validate file is PDF
    2. Save file temporarily
    3. Extract and chunk text
    4. Generate embeddings
    5. Store in Pinecone
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail=f"Only PDF files are allowed. Got: {file.filename}")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File size ({len(file_content)} bytes) exceeds maximum allowed size of {config.MAX_FILE_SIZE} bytes"
        )
    
    print(f"Processing PDF: {file.filename}, size: {len(file_content)} bytes")
    
    try:
        # Get services
        pdf_processor = get_pdf_processor()
        embedding_service = get_embedding_service()
        pinecone_service = get_pinecone_service()
        
        # Save uploaded file
        file_path = pdf_processor.save_uploaded_file(file_content, file.filename)
        
        # Process PDF (extract, clean, chunk)
        chunks = pdf_processor.process_pdf(file_path, file.filename)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No text found in PDF. It might be scanned (image-only) or protected. Please use a text-based PDF.")
        
        # Extract text from chunks for embedding
        chunk_texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings for all chunks
        embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
        
        # Prepare metadata for Pinecone (include text in metadata)
        metadata_list = []
        for chunk in chunks:
            metadata = chunk['metadata'].copy()
            metadata['text'] = chunk['text']  # Store text in metadata for retrieval
            metadata_list.append(metadata)
        
        # Upsert to Pinecone
        pinecone_service.upsert_embeddings(embeddings, metadata_list)
        
        # Return frontend-compatible format
        return {
            "success": True,
            "pdf_id": file.filename,
            "number_of_chunks": len(chunks),
            "message": f"Successfully processed {file.filename}",
            "filename": file.filename,
            "chunks_processed": len(chunks)
        }

        
    except HTTPException:
        # Re-raise HTTP exceptions with their original status codes
        raise
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
