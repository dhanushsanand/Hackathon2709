import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from config import settings
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)

class CloudinaryService:
    def __init__(self):
        self.folder_prefix = "pdf-quiz-system"
    
    async def upload_pdf(self, file_bytes: bytes, filename: str, user_id: str) -> Dict[str, Any]:
        """Upload PDF to Cloudinary"""
        try:
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            clean_filename = filename.replace(" ", "_").replace(".", "_")
            public_id = f"{self.folder_prefix}/users/{user_id}/pdfs/{timestamp}_{unique_id}_{clean_filename}"
            
            # Upload file
            result = cloudinary.uploader.upload(
                file_bytes,
                public_id=public_id,
                resource_type="raw",  # For non-image files
                format="pdf",
                context={
                    "user_id": user_id,
                    "original_filename": filename,
                    "upload_date": datetime.now().isoformat()
                },
                tags=["pdf", "user_upload", f"user_{user_id}"]
            )
            
            return {
                "public_id": result["public_id"],
                "secure_url": result["secure_url"],
                "url": result["url"],
                "bytes": result["bytes"],
                "format": result["format"],
                "resource_type": result["resource_type"],
                "created_at": result["created_at"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload to Cloudinary: {str(e)}")
    
    async def get_file_url(self, public_id: str, expires_in: int = 3600) -> str:
        """Generate signed URL for file access"""
        try:
            # Generate signed URL that expires
            url, options = cloudinary_url(
                public_id,
                resource_type="raw",
                secure=True,
                sign_url=True,
                auth_token={
                    "duration": expires_in
                }
            )
            return url
        except Exception as e:
            raise Exception(f"Failed to generate file URL: {str(e)}")
    
    async def delete_file(self, public_id: str) -> bool:
        """Delete file from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type="raw"
            )
            return result.get("result") == "ok"
        except Exception as e:
            raise Exception(f"Failed to delete file: {str(e)}")
    
    async def get_file_info(self, public_id: str) -> Dict[str, Any]:
        """Get file information from Cloudinary"""
        try:
            result = cloudinary.api.resource(
                public_id,
                resource_type="raw"
            )
            return result
        except Exception as e:
            raise Exception(f"Failed to get file info: {str(e)}")