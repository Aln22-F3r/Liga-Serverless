import boto3
import os
import sys

# Configuración #
LAMBDA_FUNCTION_NAME = "LigaServerless"
API_NAME = "LigaServerlessAPI"
STAGE_NAME = "prod"
REGION = os.getenv("AWS_REGION", "us-east-1")

# Credenciales AWS #
if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
    print("Faltan credenciales AWS.")
    sys.exit(1)

# Clientes #
apigateway = boto3.client("apigatewayv2", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)
sts_client = boto3.client("sts", region_name=REGION)

# Lambda check #
try:
    lambda_arn = lambda_client.get_function(FunctionName=LAMBDA_FUNCTION_NAME)["Configuration"]["FunctionArn"]
    print(f"Lambda encontrada: {LAMBDA_FUNCTION_NAME}")
except lambda_client.exceptions.ResourceNotFoundException:
    print(f"No existe la Lambda '{LAMBDA_FUNCTION_NAME}'")
    sys.exit(1)

# API check #
apis = apigateway.get_apis()["Items"]
api = next((a for a in apis if a["Name"] == API_NAME), None)

if api:
    api_id = api["ApiId"]
    print(f"API encontrada: {API_NAME} → {api_id}")
else:
    response = apigateway.create_api(
        Name=API_NAME,
        ProtocolType="HTTP",
        Target=lambda_arn,
        CorsConfiguration={
            "AllowOrigins": ["*"],
            "AllowMethods": ["*"],
            "AllowHeaders": ["*"],
        },
    )
    api_id = response["ApiId"]
    print(f"API creada: {API_NAME} → {api_id}")

# Integration #
integrations = apigateway.get_integrations(ApiId=api_id)["Items"]
integration = next((i for i in integrations if i.get("IntegrationUri") == lambda_arn), None)

if integration:
    integration_id = integration["IntegrationId"]
    print(f"Integración existente: {integration_id}")
else:
    integration = apigateway.create_integration(
        ApiId=api_id,
        IntegrationType="AWS_PROXY",
        IntegrationUri=lambda_arn,
        PayloadFormatVersion="2.0",
    )
    integration_id = integration["IntegrationId"]
    print(f"Integración creada: {integration_id}")

# Routes #
routes = apigateway.get_routes(ApiId=api_id)["Items"]
route_keys = [r["RouteKey"] for r in routes]

if "$default" not in route_keys:
    apigateway.create_route(
        ApiId=api_id,
        RouteKey="$default",
        Target=f"integrations/{integration_id}",
    )
    print("Ruta $default creada")

# Stage #
stages = apigateway.get_stages(ApiId=api_id)["Items"]
if not any(s["StageName"] == STAGE_NAME for s in stages):
    apigateway.create_stage(ApiId=api_id, StageName=STAGE_NAME, AutoDeploy=True)
    print(f"Stage creado: {STAGE_NAME}")
else:
    print("Stage ya existe")

# Permisos #
account_id = sts_client.get_caller_identity()["Account"]
source_arn = f"arn:aws:execute-api:{REGION}:{account_id}:{api_id}/*/*"

try:
    lambda_client.add_permission(
        FunctionName=LAMBDA_FUNCTION_NAME,
        StatementId="ApiInvoke",
        Action="lambda:InvokeFunction",
        Principal="apigateway.amazonaws.com",
        SourceArn=source_arn,
    )
    print("Permiso agregado")
except lambda_client.exceptions.ResourceConflictException:
    print("Permiso ya existe")

print(f"\nAPI lista: https://{api_id}.execute-api.{REGION}.amazonaws.com/{STAGE_NAME}")
