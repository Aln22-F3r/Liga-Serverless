from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.users import service, models, schemas

router = APIRouter()

@router.post("/register", response_model=schemas.TokenResponse)
def register(user_in: models.UserCreate):
    try:
        return service.register_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        return service.login_user(form_data.username, form_data.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
