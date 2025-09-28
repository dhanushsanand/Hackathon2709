from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from services.auth import verify_firebase_token

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    """Dependency to get current authenticated user"""
    try:
        decoded_token = await verify_firebase_token(token.credentials)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(current_user = Depends(get_current_user)) -> str:
    """Get current user ID from token"""
    return current_user["uid"]