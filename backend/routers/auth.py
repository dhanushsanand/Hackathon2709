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

@router.post("/google", response_model=LoginResponse)
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
@router.get("/health")
async def auth_health_check():
    """Check Firebase authentication service health"""
    try:
        # Test Firebase connection by trying to get a non-existent user
        # This will fail but confirms Firebase is reachable
        from firebase_admin import auth as firebase_auth
        
        try:
            firebase_auth.get_user("test_health_check_user_that_does_not_exist")
        except firebase_auth.UserNotFoundError:
            # This is expected - means Firebase is working
            pass
        except Exception as e:
            # This indicates a real connectivity issue
            raise e
        
        return {
            "status": "healthy",
            "firebase_auth": "connected",
            "timestamp": datetime.now().isoformat(),
            "test_mode": settings.test_mode
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "firebase_auth": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "test_mode": settings.test_mode
        }

@router.post("/validate-token")
async def validate_token(current_user = Depends(get_current_user)):
    """Validate if the current token is working"""
    try:
        return {
            "valid": True,
            "user_id": current_user["uid"],
            "email": current_user.get("email"),
            "token_issued_at": current_user.get("iat"),
            "token_expires_at": current_user.get("exp"),
            "message": "Token is valid"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )