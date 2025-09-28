from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from services.auth import verify_firebase_token
from config import settings

security = HTTPBearer()

# Test bypass for development (REMOVE IN PRODUCTION!)
TEST_USER_ID = "test_user_123"

async def get_current_user(token: str = Depends(security)):
    """Dependency to get current authenticated user with enhanced error handling"""
    
    # Validate token format
    if not token or not token.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_value = token.credentials.strip()
    
    print(f"🔐 Auth request - Test mode: {settings.test_mode}")
    print(f"🔐 Token length: {len(token_value)} chars")
    
    # Test bypass - REMOVE IN PRODUCTION!
    if settings.test_mode and token_value == "test_token":
        print("✅ Using test bypass for development")
        return {
            "uid": TEST_USER_ID,
            "email": "test@example.com",
            "name": "Test User"
        }
    
    # Validate token format (Firebase ID tokens are typically JWT format)
    if not token_value.count('.') == 2:
        print("❌ Invalid token format - not a valid JWT")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print("🔐 Attempting Firebase token verification...")
    try:
        decoded_token = await verify_firebase_token(token_value)
        print(f"✅ Authentication successful for user: {decoded_token.get('uid')}")
        return decoded_token
        
    except HTTPException:
        # Re-raise HTTP exceptions from the auth service
        raise
        
    except Exception as e:
        print(f"❌ Unexpected authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(current_user = Depends(get_current_user)) -> str:
    """Get current user ID from token"""
    return current_user["uid"]