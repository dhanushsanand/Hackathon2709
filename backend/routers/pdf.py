from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from typing import List
import uuid
from datetime import datetime
import asyncio

from middleware.auth import get_current_user_id
from models.pdf import PDFDocument, PDFUploadResponse, ProcessingStatus
from services.pdf_processor import PDFProcessor
from services.embeddings import EmbeddingService
from utils.storage import upload_to_firebase_storage
from utils.database import (
    save_pdf_document, get_pdf_document, update_pdf_status,
    get_pdfs_by_user_id, delete_pdf_document
)
from utils.cloudinary import CloudinaryService
router = APIRouter()

pdf_processor = PDFProcessor()
embedding_service = EmbeddingService()
cloudinary_service = CloudinaryService()

async def process_pdf_background(pdf_id: str, file_bytes: bytes, user_id: str):
    """Background task to process PDF"""
    try:
        # Update status to processing
        await update_pdf_status(pdf_id, ProcessingStatus.PROCESSING)
        
        # Extract text
        text_content = await pdf_processor.extract_text(file_bytes)
        
        # Chunk text
        chunks = pdf_processor.chunk_text(text_content)
        
        # Generate and store embeddings
        embedding_ids = await embedding_service.store_embeddings(chunks, pdf_id)
        
        # Update PDF document with processed content
        pdf_doc = await get_pdf_document(pdf_id)
        pdf_doc.content_chunks = chunks
        pdf_doc.embedding_ids = embedding_ids
        pdf_doc.status = ProcessingStatus.COMPLETED
        pdf_doc.updated_at = datetime.now()
        
        await save_pdf_document(pdf_doc)
        
    except Exception as e:
        await update_pdf_status(pdf_id, ProcessingStatus.FAILED)
        print(f"Error processing PDF {pdf_id}: {str(e)}")

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Upload and process a PDF file"""
    
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    file_bytes = await file.read()
    # Validate file size (10MB limit)
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
    
    # Generate unique PDF ID
    pdf_id = f"pdf_{uuid.uuid4().hex}"
    filename = f"{pdf_id}_{file.filename}"
    
    try:
        # Upload to Cloudinary
        upload_result = await cloudinary_service.upload_pdf(file_bytes, filename, user_id)
        # Create PDF document record
        pdf_doc = PDFDocument(
            id=pdf_id,
            user_id=user_id,
            filename=upload_result['public_id'],
            original_filename=file.filename,
            file_size=upload_result['bytes'],
            storage_path=upload_result['secure_url'],
            status=ProcessingStatus.UPLOADED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to database
        await save_pdf_document(pdf_doc)
        
        # Start background processing
        background_tasks.add_task(process_pdf_background, pdf_id, file_bytes, user_id)
        
        return PDFUploadResponse(
            pdf_id=pdf_id,
            filename=filename,
            status=ProcessingStatus.UPLOADED,
            message="PDF uploaded successfully. Processing started."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {str(e)}")

@router.get("/{pdf_id}")
async def get_pdf(
    pdf_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get PDF document details"""
    try:
        pdf_doc = await get_pdf_document(pdf_id)
        
        # Verify ownership
        if pdf_doc.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return pdf_doc
        
    except Exception as e:
        raise HTTPException(status_code=404, detail="PDF not found")

@router.get("/user/all")
async def get_user_pdfs(user_id: str = Depends(get_current_user_id)):
    """Get all PDFs for current user"""
    try:
        print(f"📄 Fetching PDFs for user: {user_id}")
        pdfs = await get_pdfs_by_user_id(user_id)
        
        # Add summary statistics
        total_pdfs = len(pdfs)
        completed_pdfs = len([pdf for pdf in pdfs if pdf.status == ProcessingStatus.COMPLETED])
        processing_pdfs = len([pdf for pdf in pdfs if pdf.status == ProcessingStatus.PROCESSING])
        failed_pdfs = len([pdf for pdf in pdfs if pdf.status == ProcessingStatus.FAILED])
        
        return {
            "pdfs": pdfs,
            "summary": {
                "total": total_pdfs,
                "completed": completed_pdfs,
                "processing": processing_pdfs,
                "failed": failed_pdfs
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching PDFs for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch PDFs: {str(e)}")

@router.delete("/{pdf_id}")
async def delete_pdf(
    pdf_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a PDF document and all related data"""
    try:
        print(f"🗑️  Delete request for PDF: {pdf_id} by user: {user_id}")
        
        # Get PDF document first
        pdf_doc = await get_pdf_document(pdf_id)
        
        # Verify ownership
        if pdf_doc.user_id != user_id:
            print(f"❌ Access denied: PDF {pdf_id} belongs to {pdf_doc.user_id}, not {user_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Clean up embeddings from Pinecone first
        embeddings_deleted = 0
        if pdf_doc.embedding_ids and embedding_service.index:
            try:
                embedding_service.index.delete(ids=pdf_doc.embedding_ids)
                embeddings_deleted = len(pdf_doc.embedding_ids)
                print(f"✅ Deleted {embeddings_deleted} embeddings from Pinecone")
            except Exception as e:
                print(f"⚠️  Warning: Failed to delete embeddings: {e}")
        
        # Delete from database (this also deletes related quizzes, attempts, notes)
        deletion_stats = await delete_pdf_document(pdf_id)
        
        # Try to delete from Cloudinary storage
        try:
            if hasattr(cloudinary_service, 'delete_file'):
                await cloudinary_service.delete_file(pdf_doc.filename)
                print(f"✅ Deleted file from Cloudinary: {pdf_doc.filename}")
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete from Cloudinary: {e}")
        
        return {
            "message": "PDF and all related data deleted successfully",
            "pdf_id": pdf_id,
            "filename": pdf_doc.original_filename,
            "deletion_stats": {
                "embeddings_deleted": embeddings_deleted,
                **deletion_stats
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"❌ Error deleting PDF {pdf_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF: {str(e)}")