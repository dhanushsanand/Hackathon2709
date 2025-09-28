from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from services.auth import verify_firebase_token
from config import settings

security = HTTPBearer()

# Test bypass for development (REMOVE IN PRODUCTION!)
TEST_USER_ID = "test_user_123"

async def get_current_user(token: str = Depends(security)):
    """Dependency to get current authenticated user"""
    # Debug logging
    print(f"DEBUG: TEST_MODE = {settings.test_mode}")
    print(f"DEBUG: Received token = {token.credentials}")
    
    # Test bypass - REMOVE IN PRODUCTION!
    if settings.test_mode and token.credentials == "test_token":
        print("DEBUG: Using test bypass")
        return {
            "uid": TEST_USER_ID,
            "email": "test@example.com",
            "name": "Test User"
        }
    
    print("DEBUG: Attempting Firebase verification")
    try:
        decoded_token = await verify_firebase_token(token.credentials)
        return decoded_token
    except Exception as e:
        print(f"DEBUG: Firebase verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(current_user = Depends(get_current_user)) -> str:
    """Get current user ID from token"""
    return current_user["uid"]