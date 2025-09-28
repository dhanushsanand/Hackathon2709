import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status
from config import settings

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.firebase_credentials_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': settings.firebase_storage_bucket
    })

async def verify_firebase_token(token: str) -> dict:
    """Verify Firebase ID token with retry logic"""
    import asyncio
    import time
    
    if not token or token.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided"
        )
    
    # Retry logic for Firebase API calls
    max_retries = 3
    retry_delay = 0.5  # Start with 500ms delay
    
    for attempt in range(max_retries):
        try:
            print(f"🔐 Firebase token verification attempt {attempt + 1}/{max_retries}")
            
            # Verify the token
            decoded_token = auth.verify_id_token(token, check_revoked=True)
            
            # Additional validation
            if not decoded_token.get('uid'):
                raise ValueError("Token missing user ID")
            
            # Check token expiration
            current_time = time.time()
            if decoded_token.get('exp', 0) < current_time:
                raise ValueError("Token has expired")
            
            print(f"✅ Token verified successfully for user: {decoded_token.get('uid')}")
            return decoded_token
            
        except auth.ExpiredIdTokenError:
            print(f"❌ Token expired on attempt {attempt + 1}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please login again."
            )
            
        except auth.RevokedIdTokenError:
            print(f"❌ Token revoked on attempt {attempt + 1}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has been revoked. Please login again."
            )
            
        except auth.InvalidIdTokenError as e:
            print(f"❌ Invalid token on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token format"
                )
            
        except auth.CertificateFetchError as e:
            print(f"⚠️  Certificate fetch error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service temporarily unavailable"
                )
            
        except Exception as e:
            print(f"⚠️  Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Authentication failed: {str(e)}"
                )
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries - 1:
            wait_time = retry_delay * (2 ** attempt)
            print(f"⏳ Waiting {wait_time}s before retry...")
            await asyncio.sleep(wait_time)
    
    # This should never be reached due to the exception handling above
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication failed after all retries"
    )

async def get_user_by_uid(uid: str):
    """Get Firebase user by UID with retry logic"""
    import asyncio
    
    if not uid or uid.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is required"
        )
    
    # Retry logic for Firebase API calls
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            print(f"👤 Getting user record attempt {attempt + 1}/{max_retries} for UID: {uid}")
            
            user_record = auth.get_user(uid)
            
            print(f"✅ User record retrieved successfully: {user_record.email}")
            return user_record
            
        except auth.UserNotFoundError:
            print(f"❌ User not found: {uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in Firebase"
            )
            
        except Exception as e:
            print(f"⚠️  Error getting user on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve user information: {str(e)}"
                )
            
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
    
    # This should never be reached
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to retrieve user after all retries"
    )