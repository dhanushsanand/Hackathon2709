from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class PDFDocument(BaseModel):
    id: str
    user_id: str
    filename: str
    original_filename: str
    file_size: int
    storage_path: str
    status: ProcessingStatus
    content_chunks: Optional[List[str]] = None
    embedding_ids: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

class PDFUploadResponse(BaseModel):
    pdf_id: str
    filename: str
    status: ProcessingStatus
    message: str