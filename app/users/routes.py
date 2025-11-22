from fastapi import APIRouter, HTTPException
from app.users.models import UserCreate
from app.users.schemas import TokenResponse
from app.users import service

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register(user: UserCreate):
    try:
        return service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class LoginData(UserCreate):
    pass

@router.post("/login", response_model=TokenResponse)
def login(data: LoginData):
    try:
        return service.login_user(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
