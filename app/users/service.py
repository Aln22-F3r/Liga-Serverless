import uuid
import boto3
from passlib.context import CryptContext
from app.users.models import UserModel, UserCreate
from app.users.auth import create_access_token
from typing import Optional
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMO_TABLE = os.getenv("USERS_TABLE", "Usuarios")

pwd_context = CryptContext(
    schemes=["sha256_crypt"],
    deprecated="auto"
)

def get_table():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return dynamodb.Table(DYNAMO_TABLE)

def get_user_by_email(email: str) -> Optional[dict]:
    table = get_table()
    resp = table.get_item(Key={"pk": f"USER#{email}", "sk": "PROFILE"})
    return resp.get("Item")

def register_user(data: UserCreate):
    if get_user_by_email(data.email):
        raise ValueError("El usuario ya existe")

    user_id = str(uuid.uuid4())
    hashed_pw = pwd_context.hash(data.password)

    user = UserModel(
        pk=f"USER#{data.email}",
        id=user_id,
        username=data.username,
        email=data.email,
        roles=["usuario"],
        permissions=["ver"]
    )

    table = get_table()
    table.put_item(Item={**user.dict(), "password": hashed_pw})

def login_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        raise ValueError("Usuario no encontrado")

    if not pwd_context.verify(password, user["password"]):
        raise ValueError("Contraseña incorrecta")

    token = create_access_token(email)
    return {"access_token": token, "token_type": "bearer"}
