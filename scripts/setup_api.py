import boto3
from botocore.exceptions import ClientError

# ============= CONFIGURACIÓN ============= #
LAMBDA_NAME = "LigaServerless"
API_NAME = "LigaServerlessAPI"
REGION = "us-east-1"

# Inicializar clientes #
apigw = boto3.client("apigatewayv2", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)
sts = boto3.client("sts")

def get_lambda_arn():
    try:
        response = lambda_client.get_function(FunctionName=LAMBDA_NAME)
        return response["Configuration"]["FunctionArn"]
    except ClientError as e:
        print(f"Error: Lambda '{LAMBDA_NAME}' no encontrada.")
        print(f"Asegúrate de que existe en la región {REGION}")
        raise

def get_or_create_api():
    try:
        existing = apigw.get_apis()["Items"]
        api = next((x for x in existing if x["Name"] == API_NAME), None)

        if api:
            api_id = api["ApiId"]
            print(f"API encontrada: {api_id}")
            return api_id
        else:
            print(f"Creando nueva API: {API_NAME}...")
            resp = apigw.create_api(
                Name=API_NAME,
                ProtocolType="HTTP",
                CorsConfiguration={
                    "AllowOrigins": ["*"],
                    "AllowMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "AllowHeaders": [
                        "Content-Type",
                        "Authorization",
                        "X-Amz-Date",
                        "X-Api-Key",
                        "X-Amz-Security-Token"
                    ],
                    "MaxAge": 300
                }
            )
            api_id = resp["ApiId"]
            print(f"API creada: {api_id}")
            return api_id
    except ClientError as e:
        print(f"Error al crear/obtener API: {e}")
        raise

def get_or_create_integration(api_id, lambda_arn):
    try:
        integrations = apigw.get_integrations(ApiId=api_id)["Items"]
        integration = next(
            (x for x in integrations if x.get("IntegrationUri") == lambda_arn), 
            None
        )

        if integration:
            integration_id = integration["IntegrationId"]
            print(f"Integración existente encontrada: {integration_id}")
            return integration_id
        else:
            print("Creando integración Lambda Proxy...")
            resp = apigw.create_integration(
                ApiId=api_id,
                IntegrationType="AWS_PROXY",
                IntegrationUri=lambda_arn,
                IntegrationMethod="POST",
                PayloadFormatVersion="2.0",
                TimeoutInMillis=30000
            )
            integration_id = resp["IntegrationId"]
            print(f"Integración creada: {integration_id}")
            return integration_id
    except ClientError as e:
        print(f"Error al crear integración: {e}")
        raise

def ensure_route(api_id, integration_id, method, route):
    route_key = f"{method} {route}"
    try:
        routes = apigw.get_routes(ApiId=api_id)["Items"]

        if any(r["RouteKey"] == route_key for r in routes):
            print(f"Ruta existente: {route_key}")
            return

        apigw.create_route(
            ApiId=api_id,
            RouteKey=route_key,
            Target=f"integrations/{integration_id}"
        )
        print(f"Ruta creada: {route_key}")
    except ClientError as e:
        print(f"Error al crear ruta {route_key}: {e}")

def add_lambda_permission(api_id, lambda_arn):
    account_id = sts.get_caller_identity()["Account"]
    source_arn = f"arn:aws:execute-api:{REGION}:{account_id}:{api_id}/*/*"

    try:
        try:
            lambda_client.remove_permission(
                FunctionName=LAMBDA_NAME,
                StatementId="APIInvoke"
            )
            print("Permiso anterior removido.")
        except:
            pass

        lambda_client.add_permission(
            FunctionName=LAMBDA_NAME,
            StatementId="APIInvoke",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn
        )
        print("Permiso agregado a Lambda.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceConflictException":
            print("El permiso ya existía.")
        else:
            print(f"Error al agregar permiso: {e}")

def ensure_stage(api_id):
    try:
        stages = apigw.get_stages(ApiId=api_id)["Items"]
        
        if not any(s["StageName"] == "$default" for s in stages):
            print("Creando stage $default...")
            apigw.create_stage(
                ApiId=api_id,
                StageName="$default",
                AutoDeploy=True,
                Description="Stage de producción con auto-deploy"
            )
            print("Stage $default creado.")
        else:
            print("Stage $default ya existe.")
            
            apigw.update_stage(
                ApiId=api_id,
                StageName="$default",
                AutoDeploy=True
            )
            print("AutoDeploy activado en $default.")
    except ClientError as e:
        print(f"Error al crear/actualizar stage: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("CONFIGURANDO API GATEWAY PARA LA LIGA SERVERLESS")
    print("=" * 60)
    print()

    try:
        # 1. Obtener Lambda ARN #
        print("Paso 1: Verificando Lambda...")
        lambda_arn = get_lambda_arn()
        print(f"   ARN: {lambda_arn}")
        print()

        # 2. Crear o usar API existente #
        print("Paso 2: Configurando API Gateway...")
        api_id = get_or_create_api()
        print()

        # 3. Crear integración Lambda Proxy #
        print("Paso 3: Configurando integración con Lambda...")
        integration_id = get_or_create_integration(api_id, lambda_arn)
        print()

        # 4. Crear rutas #
        print("Paso 4: Configurando rutas...")
        ensure_route(api_id, integration_id, "ANY", "/")
        ensure_route(api_id, integration_id, "ANY", "/{proxy+}")
        print()

        # 5. Dar permisos #
        print("Paso 5: Configurando permisos...")
        add_lambda_permission(api_id, lambda_arn)
        print()

        # 6. Crear/actualizar stage #
        print("Paso 6: Configurando stage de producción...")
        ensure_stage(api_id)
        print()

        # 7. Mostrar URL final #
        api_url = f"https://{api_id}.execute-api.{REGION}.amazonaws.com"
        print("=" * 60)
        print("¡CONFIGURACIÓN COMPLETADA!")
        print("=" * 60)
        print()
        print("URL de tu API:")
        print(f"   {api_url}")
        print()
        print("Prueba tu API:")
        print(f"   curl {api_url}/")
        print()
        print("Actualiza esta URL en tu app Flutter:")
        print(f"   api_service.dart → baseUrl = \"{api_url}\"")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("ERROR EN LA CONFIGURACIÓN")
        print("=" * 60)
        print(f"   {str(e)}")
        print()
        print("Verifica que:")
        print(f"   1. La función Lambda '{LAMBDA_NAME}' existe")
        print(f"   2. Tienes permisos de IAM suficientes")
        print(f"   3. Estás usando la región correcta ({REGION})")
        print()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())