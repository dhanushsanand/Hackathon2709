# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.auth import verify_firebase_token, get_user_by_uid
from middleware.auth import get_current_user
from models.user import User
from utils.database import save_user, get_user
from datetime import datetime
from config import settings

router = APIRouter()

class LoginRequest(BaseModel):
    firebase_token: str

class LoginResponse(BaseModel):
    message: str
    user: User
    access_token: str

@router.post("/login", response_model=LoginResponse)
async def login_with_firebase(request: LoginRequest):
    """Login with Firebase token"""
    try:
        # Verify Firebase token
        decoded_token = await verify_firebase_token(request.firebase_token)
        
        # Get user record from Firebase Auth
        user_record = await get_user_by_uid(decoded_token["uid"])
        
        # Create User object
        user = User(
            uid=user_record.uid,
            email=user_record.email or "unknown@example.com",
            display_name=user_record.display_name,
            photo_url=user_record.photo_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save/update user in database
        await save_user(user)
        
        return LoginResponse(
            message="Login successful",
            user=user,
            access_token=request.firebase_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")

@router.get("/me", response_model=User)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    try:
        # Test mode bypass - return test user directly
        if settings.test_mode and current_user["uid"] == "test_user_123":
            return User(
                uid=current_user["uid"],
                email=current_user.get("email", "test@example.com"),
                display_name=current_user.get("name", "Test User"),
                photo_url=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        # Try to get user from database first
        db_user = await get_user(current_user["uid"])
        if db_user:
            return db_user
        
        # If not in database, get from Firebase Auth
        user_record = await get_user_by_uid(current_user["uid"])
        
        # Create and save user
        user = User(
            uid=user_record.uid,
            email=user_record.email or "unknown@example.com",
            display_name=user_record.display_name,
            photo_url=user_record.photo_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await save_user(user)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Logged out successfully"}