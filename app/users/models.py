from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserModel(BaseModel):
    pk: str
    sk: str = "PROFILE"
    id: str
    username: str
    email: EmailStr
    photoUrl: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    teamId: Optional[str] = None
    teamName: Optional[str] = None
    leagueId: Optional[str] = None
    leagueName: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
