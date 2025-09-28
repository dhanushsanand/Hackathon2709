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
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

async def get_user_by_uid(uid: str):
    try:
        user_record = auth.get_user(uid)
        return user_record
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )