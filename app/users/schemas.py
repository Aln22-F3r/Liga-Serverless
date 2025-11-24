from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserResponse(BaseModel):
    pk: str
    sk: str
    id: str
    username: str
    email: EmailStr
    photoUrl: Optional[str] = None
    roles: List[str]
    permissions: List[str]
    teamId: Optional[str] = None
    teamName: Optional[str] = None
    leagueId: Optional[str] = None
    leagueName: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
