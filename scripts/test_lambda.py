import boto3
import json

# Configuración #

LAMBDA_NAME = "LigaServerless"
REGION = "us-east-1"

lambda_client = boto3.client("lambda", region_name=REGION)

# Datos de prueba #

user_register = {
    "username": "alan",
    "email": "alan@test.com",
    "password": "123456"
}

user_login = {
    "email": "alan@test.com",
    "password": "123456"
}

# Función auxiliar #

def invoke_lambda(path: str, body: dict):
    """Invoca la Lambda simulando API Gateway con payload v2.0"""
    event = {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": "",
        "headers": {"content-type": "application/json"},
        "requestContext": {
            "http": {
                "method": "POST",
                "path": path,
                "sourceIp": "127.0.0.1",
                "userAgent": "TestScript"
            }
        },
        "body": json.dumps(body),
        "isBase64Encoded": False
    }

    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        Payload=json.dumps(event),
    )

    result = json.loads(response["Payload"].read())
    return result

# Register #

print("=== Probando Register ===")
register_result = invoke_lambda("/users/register", user_register)
print(json.dumps(register_result, indent=4))

# Login #

print("\n=== Probando Login ===")
login_result = invoke_lambda("/users/login", user_login)
print(json.dumps(login_result, indent=4))

# Capturar token si login fue exitoso #

if login_result.get("statusCode") == 200:
    token = json.loads(login_result["body"]).get("access_token")
    print("\nToken recibido:", token)
else:
    print("\nLogin fallido")
