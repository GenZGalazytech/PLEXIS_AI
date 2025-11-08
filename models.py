from pydantic import BaseModel
from typing import Optional


# Pydantic model for a user in the database
class UserInDB(BaseModel):
    id: str  # or ObjectId
    username: str
    role: str  # e.g., 'photographer', 'client'```


class TokenData(BaseModel):
    user_id: Optional[str] = None


class CurrentUser(BaseModel):
    username: str
    role: str


class SearchImageRequest(BaseModel):
    event_name: str
    query_text: str