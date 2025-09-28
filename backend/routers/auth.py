# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.auth import verify_firebase_token, get_user_by_uid
from middleware.auth import get_current_user
from models.user import User
from datetime import datetime

router = APIRouter()

class LoginRequest(BaseModel):
    token: str

class LoginResponse(BaseModel):
    user: User
    access_token: str

@router.post("/google", response_model=LoginResponse)
async def login_with_google(request: LoginRequest):
    """Login with Google using Firebase token"""
    try:
        decoded_token = await verify_firebase_token(request.token)
        user_record = await get_user_by_uid(decoded_token["uid"])
        
        user = User(
            uid=user_record.uid,
            email=user_record.email,
            display_name=user_record.display_name,
            photo_url=user_record.photo_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # In a real app, you might want to create a custom JWT here
        # For now, we'll just return the Firebase token
        return LoginResponse(user=user, access_token=request.token)
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=User)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    from config import settings
    
    # Test mode bypass - return test user directly
    if settings.test_mode and current_user["uid"] == "test_user_123":
        return User(
            uid=current_user["uid"],
            email=current_user["email"],
            display_name=current_user.get("name", "Test User"),
            photo_url=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    # Normal Firebase user lookup
    user_record = await get_user_by_uid(current_user["uid"])
    
    return User(
        uid=user_record.uid,
        email=user_record.email,
        display_name=user_record.display_name,
        photo_url=user_record.photo_url,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Logged out successfully"}

# routers/pdf.py


# routers/quiz.py

# routers/user.py
