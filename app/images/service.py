import boto3
import os
import uuid

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET_NAME = os.getenv("ASSETS_BUCKET", "liga-assets")

s3 = boto3.client("s3", region_name=AWS_REGION)

def build_s3_key(entity_type: str, entity_id: str, purpose: str, content_type: str) -> str:
    extension = content_type.split("/")[-1]
    return f"{entity_type}s/{entity_id}/{purpose}.{extension}"

def generate_presigned_upload(entity_type: str, entity_id: str, purpose: str, content_type: str):
    key = build_s3_key(entity_type, entity_id, purpose, content_type)

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=300,
    )

    file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"

    return {
        "uploadUrl": upload_url,
        "fileUrl": file_url,
    }
