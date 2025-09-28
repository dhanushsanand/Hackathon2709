from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserInDB(User):
    pass