from fastapi import APIRouter, Depends
from app.images.schemas import ImageUploadRequest
from app.images.service import generate_presigned_upload
from app.users.auth import get_current_user

router = APIRouter()

@router.post("/upload")
async def request_image_upload(
    data: ImageUploadRequest,
    current_user: dict = Depends(get_current_user),
):
    # Seguridad básica: solo el usuario dueño puede subir su profile
    if data.entityType == "user" and data.entityId != current_user["user_id"]:
        raise ValueError("No autorizado")

    return generate_presigned_upload(
        entity_type=data.entityType,
        entity_id=data.entityId,
        purpose=data.purpose,
        content_type=data.contentType,
    )
