import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from typing import Dict, Any, Optional, List
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
            
            print(f"DEBUG: Uploading to Cloudinary - public_id: {public_id}")
            print(f"DEBUG: File size: {len(file_bytes)} bytes")
            
            # Upload file
            result = cloudinary.uploader.upload(
                file_bytes,
                public_id=public_id,
                resource_type="raw",  # For non-image files
                context={
                    "user_id": user_id,
                    "original_filename": filename,
                    "upload_date": datetime.now().isoformat()
                },
                tags=["pdf", "user_upload", f"user_{user_id}"]
            )
            
            print(f"DEBUG: Upload successful - result keys: {result.keys()}")
            
            return {
                "public_id": result["public_id"],
                "secure_url": result["secure_url"],
                "url": result["url"],
                "bytes": result["bytes"],
                "format": result.get("format", "pdf"),  # Default to pdf if format not provided
                "resource_type": result["resource_type"],
                "created_at": result["created_at"]
            }
            
        except Exception as e:
            print(f"DEBUG: Cloudinary upload error: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
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
    
    async def get_files_by_user_id(self, user_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get all files uploaded by a specific user"""
        try:
            # Search for files with the user_id tag
            result = cloudinary.api.resources(
                type="upload",
                resource_type="raw",
                tags=[f"user_{user_id}"],
                max_results=max_results,
                context=True  # Include context metadata
            )
            
            files = []
            for resource in result.get('resources', []):
                # Extract file info
                file_info = {
                    "public_id": resource["public_id"],
                    "secure_url": resource["secure_url"],
                    "url": resource["url"],
                    "bytes": resource["bytes"],
                    "format": resource.get("format", ""),
                    "resource_type": resource["resource_type"],
                    "created_at": resource["created_at"],
                    "context": resource.get("context", {}),
                    "tags": resource.get("tags", [])
                }
                
                # Extract original filename from context if available
                context = resource.get("context", {})
                if "original_filename" in context:
                    file_info["original_filename"] = context["original_filename"]
                
                files.append(file_info)
            
            print(f"DEBUG: Found {len(files)} files for user {user_id}")
            return files
            
        except Exception as e:
            print(f"DEBUG: Error getting files by user_id: {str(e)}")
            raise Exception(f"Failed to get files by user_id: {str(e)}")
    
    async def get_files_by_user_id_in_folder(self, user_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get all files uploaded by a specific user using folder structure"""
        try:
            # Search for files in the user's folder
            folder_prefix = f"{self.folder_prefix}/users/{user_id}/"
            
            result = cloudinary.api.resources(
                type="upload",
                resource_type="raw",
                prefix=folder_prefix,
                max_results=max_results,
                context=True
            )
            
            files = []
            for resource in result.get('resources', []):
                file_info = {
                    "public_id": resource["public_id"],
                    "secure_url": resource["secure_url"],
                    "url": resource["url"],
                    "bytes": resource["bytes"],
                    "format": resource.get("format", ""),
                    "resource_type": resource["resource_type"],
                    "created_at": resource["created_at"],
                    "context": resource.get("context", {}),
                    "tags": resource.get("tags", [])
                }
                
                # Extract original filename from context
                context = resource.get("context", {})
                if "original_filename" in context:
                    file_info["original_filename"] = context["original_filename"]
                
                files.append(file_info)
            
            print(f"DEBUG: Found {len(files)} files in folder for user {user_id}")
            return files
            
        except Exception as e:
            print(f"DEBUG: Error getting files by folder: {str(e)}")
            raise Exception(f"Failed to get files by folder: {str(e)}")