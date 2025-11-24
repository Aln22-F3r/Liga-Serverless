import os

aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_token = os.getenv("AWS_SESSION_TOKEN")
region = os.getenv("AWS_REGION", "us-east-1")

if not aws_key or not aws_secret or not aws_token:
    raise Exception("Faltan variables de entorno AWS del Learner Lab.")

aws_dir = os.path.join(os.path.expanduser("~"), ".aws")
os.makedirs(aws_dir, exist_ok=True)

creds_file = os.path.join(aws_dir, "credentials")

creds = f"""[default]
aws_access_key_id = {aws_key}
aws_secret_access_key = {aws_secret}
aws_session_token = {aws_token}
region = {region}
"""

with open(creds_file, "w") as f:
    f.write(creds)

print("Archivo creado en:", creds_file)
