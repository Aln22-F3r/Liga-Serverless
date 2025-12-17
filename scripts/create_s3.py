import boto3
from botocore.exceptions import ClientError

# ================= CONFIG ================= #
AWS_REGION = "us-east-1"

ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
BUCKET_NAME = f"liga-images-prod-{ACCOUNT_ID}"

s3 = boto3.client("s3", region_name=AWS_REGION)

def bucket_exists():
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
        return True
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            return False
        elif code == "403":
            raise Exception(
                f"El bucket '{BUCKET_NAME}' existe pero NO te pertenece"
            )
        else:
            raise

def create_bucket():
    if bucket_exists():
        print(f"ℹBucket ya existe y es accesible: {BUCKET_NAME}")
        return

    try:
        if AWS_REGION == "us-east-1":
            s3.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={
                    "LocationConstraint": AWS_REGION
                }
            )
        print(f"Bucket creado: {BUCKET_NAME}")
    except ClientError as e:
        raise Exception(f"Error creando bucket: {e}")

def block_public_access():
    s3.put_public_access_block(
        Bucket=BUCKET_NAME,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
    )
    print("Acceso público bloqueado")

def configure_cors():
    s3.put_bucket_cors(
        Bucket=BUCKET_NAME,
        CORSConfiguration={
            "CORSRules": [
                {
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
                    "AllowedOrigins": ["*"],
                    "ExposeHeaders": ["ETag"],
                    "MaxAgeSeconds": 3000
                }
            ]
        }
    )
    print("CORS configurado")

def enable_versioning():
    s3.put_bucket_versioning(
        Bucket=BUCKET_NAME,
        VersioningConfiguration={"Status": "Enabled"}
    )
    print("Versionado activado")

def main():
    print("=" * 60)
    print("CONFIGURANDO S3 PARA LIGA SERVERLESS (READY TO USE)")
    print("=" * 60)

    create_bucket()
    block_public_access()
    configure_cors()
    enable_versioning()

    print()
    print("=" * 60)
    print("S3 LISTO PARA PRODUCCIÓN")
    print("=" * 60)
    print()
    print("Bucket:", BUCKET_NAME)
    print("Región:", AWS_REGION)
    print()
    print("Permisos IAM requeridos para Lambda:")
    print(f"  arn:aws:s3:::{BUCKET_NAME}/*")
    print("  - s3:PutObject")
    print("  - s3:GetObject")
    print("  - s3:DeleteObject")

if __name__ == "__main__":
    main()
