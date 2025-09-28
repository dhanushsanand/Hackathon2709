from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Firebase
    firebase_credentials_path: str
    firebase_storage_bucket: str
    
    # Cloudinary
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    
    # Pinecone
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "asu-agent"
    
    # Gemini
    gemini_api_key: str
    
    # Convex
    convex_url: Optional[str] = None
    
    # App settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Testing (REMOVE IN PRODUCTION!)
    test_mode: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # This allows extra fields in .env to be ignored

settings = Settings()