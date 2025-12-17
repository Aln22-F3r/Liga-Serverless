from pydantic import BaseModel
from app.images.types import ImageEntityType, ImagePurpose

class ImageUploadRequest(BaseModel):
    entityType: ImageEntityType
    purpose: ImagePurpose
    entityId: str
    contentType: str
