from firebase_admin import storage
from typing import Optional
import uuid
from datetime import datetime, timedelta

bucket = storage.bucket()

async def upload_to_firebase_storage(file_bytes: bytes, filename: str) -> str:
    """Upload file to Firebase Storage and return download URL"""
    try:
        # Generate unique path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"pdfs/{timestamp}_{filename}"
        
        # Upload file
        blob = bucket.blob(unique_filename)
        blob.upload_from_string(file_bytes, content_type='application/pdf')
        
        # Make blob publicly accessible (optional, depending on your security needs)
        # blob.make_public()
        
        # Generate signed URL (valid for 1 hour)
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.utcnow() + timedelta(hours=1),
            method="GET"
        )
        
        return unique_filename  # Return path, not URL for security
        
    except Exception as e:
        raise Exception(f"Failed to upload file to storage: {str(e)}")

async def get_file_download_url(file_path: str, expiration_hours: int = 1) -> str:
    """Generate a signed URL for file download"""
    try:
        blob = bucket.blob(file_path)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.utcnow() + timedelta(hours=expiration_hours),
            method="GET"
        )
        
        return url
        
    except Exception as e:
        raise Exception(f"Failed to generate download URL: {str(e)}")

async def delete_file_from_storage(file_path: str) -> None:
    """Delete file from Firebase Storage"""
    try:
        blob = bucket.blob(file_path)
        blob.delete()
    except Exception as e:
        raise Exception(f"Failed to delete file from storage: {str(e)}")

async def upload_user_file(file_bytes: bytes, user_id: str, original_filename: str) -> str:
    """Upload user file with organized folder structure"""
    try:
        # Create organized path
        file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'pdf'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        
        file_path = f"users/{user_id}/pdfs/{timestamp}_{unique_id}.{file_extension}"
        
        # Upload file
        blob = bucket.blob(file_path)
        blob.upload_from_string(file_bytes, content_type='application/pdf')
        
        # Set metadata
        metadata = {
            'original_filename': original_filename,
            'upload_date': datetime.now().isoformat(),
            'user_id': user_id
        }
        blob.metadata = metadata
        blob.patch()
        
        return file_path
        
    except Exception as e:
        raise Exception(f"Failed to upload user file: {str(e)}")
