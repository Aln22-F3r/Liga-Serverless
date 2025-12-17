import boto3
from botocore.exceptions import ClientError

TABLE_NAME = "LigaDB"
REGION = "us-east-1"

dynamodb = boto3.client("dynamodb", region_name=REGION)

def create_users_table():
    try:
        response = dynamodb.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"  # Incluye todos los atributos #
                    }
                }
            ],
            BillingMode="PAY_PER_REQUEST"  # On-demand #
        )

        print("Creando tabla con GSI...")
        dynamodb.get_waiter("table_exists").wait(TableName=TABLE_NAME)
        print(f"Tabla '{TABLE_NAME}' creada correctamente con GSI para email.")
        print("\nEstructura de datos:")
        print("  pk: USER#{user_id} <- Clave principal (más eficiente)")
        print("  GSI1PK: EMAIL#{email} <- Para búsquedas por email")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"La tabla '{TABLE_NAME}' ya existe.")
        else:
            print("Error al crear la tabla:", e)

if __name__ == "__main__":
    create_users_table()