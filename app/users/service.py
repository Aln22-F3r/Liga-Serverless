import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

import boto3
from jose import jwt
from passlib.context import CryptContext
from app.users.models import UserModel, UserCreate

# Variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
DYNAMO_TABLE_NAME = os.getenv("USERS_TABLE", "Users")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# DynamoDB
def get_users_table():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return dynamodb.Table(DYNAMO_TABLE_NAME)

# JWT y hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------------
# Funciones de usuario
# ---------------------
def get_user_by_email(email: str) -> Optional[dict]:
    table = get_users_table()
    resp = table.get_item(Key={"pk": f"USER#{email}", "sk": "PROFILE"})
    return resp.get("Item")

def register_user(user_in: UserCreate):
    table = get_users_table()
    if get_user_by_email(user_in.email):
        raise ValueError("Usuario ya existe")

    user_id = str(uuid.uuid4())
    hashed_pw = hash_password(user_in.password)

    user_item = UserModel(
        pk=f"USER#{user_in.email}",  # Cambié a email para consistencia con get_user_by_email
        sk="PROFILE",
        id=user_id,
        username=user_in.username,
        email=user_in.email,
        roles=["usuario"],
        permissions=["ver"]
    )

    table.put_item(Item={**user_item.dict(), "password": hashed_pw})

    token = create_access_token({"sub": user_in.email})
    return {"access_token": token, "token_type": "bearer"}

def login_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user.get("password", "")):
        raise ValueError("Credenciales incorrectas")
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}
