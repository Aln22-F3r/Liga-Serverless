from fastapi import APIRouter, HTTPException
from app.users.models import UserCreate
from app.users.schemas import TokenResponse
from app.users import service

router = APIRouter()

@router.post("/register")
def register(user: UserCreate):
    try:
        service.register_user(user)
        return {"message": "Usuario registrado correctamente"}
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
