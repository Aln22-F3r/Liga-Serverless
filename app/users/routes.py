from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.users.models import UserCreate
from app.users.schemas import TokenResponse, UserResponse, RefreshTokenRequest
from app.users.auth import get_current_user, get_optional_user
from app.users import service

router = APIRouter()

# Modelos para el request body #

class LoginData(BaseModel):
    email: EmailStr
    password: str

class UpdateProfileData(BaseModel):
    username: Optional[str] = None
    photoUrl: Optional[str] = None

# Routes publicas #

@router.post("/register", response_model=TokenResponse)
def register(user: UserCreate):
    try:
        user_id = service.register_user(user)
        # Después de registrar, hacer login automático #
        return service.login_user(user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(data: LoginData):
    try:
        return service.login_user(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh", response_model=dict)
def refresh_token(data: RefreshTokenRequest):
    try:
        return service.refresh_access_token(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Routes protegidas #

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    user = service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Remover password antes de retornar #
    user_data = {k: v for k, v in user.items() if k != "password"}
    return user_data

@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UpdateProfileData,
    current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Llamar al servicio para actualizar #
    user = service.update_user_profile(
        user_id=user_id,
        username=data.username,
        photoUrl=data.photoUrl
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Remover password antes de retornar #
    user_data = {k: v for k, v in user.items() if k != "password"}
    return user_data
