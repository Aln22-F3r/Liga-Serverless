import uuid
import boto3
from passlib.context import CryptContext
from app.users.models import UserModel, UserCreate
from app.users.auth import create_access_token, create_refresh_token
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
    
    # GSI1 busca por email #
    resp = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :email AND GSI1SK = :sk",
        ExpressionAttributeValues={
            ":email": f"EMAIL#{email}",
            ":sk": "PROFILE"
        }
    )
    
    items = resp.get("Items", [])
    return items[0] if items else None

def get_user_by_id(user_id: str) -> Optional[dict]:
    table = get_table()
    resp = table.get_item(Key={"pk": f"USER#{user_id}", "sk": "PROFILE"})
    return resp.get("Item")

def register_user(data: UserCreate):
    if get_user_by_email(data.email):
        raise ValueError("El usuario ya existe")

    user_id = str(uuid.uuid4())
    hashed_pw = pwd_context.hash(data.password)

    user_item = {
        "pk": f"USER#{user_id}",
        "sk": "PROFILE",
        
        # GSI1 para buscar por email #
        "GSI1PK": f"EMAIL#{data.email}",
        "GSI1SK": "PROFILE",
        
        # Datos del usuario #
        "id": user_id,
        "username": data.username,
        "email": data.email,
        "password": hashed_pw,
        "photoUrl": None,
        "roles": ["usuario"],
        "permissions": ["ver", "comentar"],
        "teamId": None,
        "teamName": None,
        "leagueId": None,
        "leagueName": None,
        
        # Metadata #
        "createdAt": str(uuid.uuid1().time),
        "updatedAt": str(uuid.uuid1().time)
    }

    table = get_table()
    table.put_item(Item=user_item)
    
    return user_id

def login_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        raise ValueError("Credenciales incorrectas")

    if not pwd_context.verify(password, user["password"]):
        raise ValueError("Credenciales incorrectas")

    # Generar ambos tokens #
    access_token = create_access_token(user["id"], user["email"])
    refresh_token = create_refresh_token(user["id"])
    
    # Preparar datos del usuario (sin password) #
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_data
    }

def refresh_access_token(refresh_token: str):
    from app.users.auth import decode_token
    
    payload = decode_token(refresh_token)
    
    # Verificar que sea un refresh token #
    if payload.get("type") != "refresh":
        raise ValueError("Token de refresco inválido")
    
    user_id = payload.get("sub")
    user = get_user_by_id(user_id)
    
    if not user:
        raise ValueError("Usuario no encontrado")
    
    # Generar nuevo access token #
    new_access_token = create_access_token(user["id"], user["email"])
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

def update_user_profile(user_id: str, username: Optional[str] = None, photoUrl: Optional[str] = None) -> Optional[dict]:
    table = get_table()
    
    # Siempre actualizar el timestamp #
    update_expr = "SET updatedAt = :updatedAt"
    expr_values = {":updatedAt": str(uuid.uuid1().time)}
    
    # Agregar campos opcionales si se proporcionaron #
    if username:
        update_expr += ", username = :username"
        expr_values[":username"] = username
    
    if photoUrl:
        update_expr += ", photoUrl = :photoUrl"
        expr_values[":photoUrl"] = photoUrl
    
    try:
        table.update_item(
            Key={"pk": f"USER#{user_id}", "sk": "PROFILE"},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values
        )
        
        # Retornar usuario actualizado #
        return get_user_by_id(user_id)
    except Exception as e:
        print(f"Error al actualizar usuario: {e}")
        return None