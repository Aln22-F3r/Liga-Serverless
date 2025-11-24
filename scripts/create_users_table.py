import boto3
from botocore.exceptions import ClientError

# Configuración #

TABLE_NAME = "Usuarios"
REGION = "us-east-1"

dynamodb = boto3.client("dynamodb", region_name=REGION)

def create_users_table():
    try:
        response = dynamodb.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        print("Creando tabla...")
        dynamodb.get_waiter("table_exists").wait(TableName=TABLE_NAME)
        print(f"Tabla '{TABLE_NAME}' creada correctamente.")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"La tabla '{TABLE_NAME}' ya existe.")
        else:
            print("Error al crear la tabla:", e)

if __name__ == "__main__":
    create_users_table()
