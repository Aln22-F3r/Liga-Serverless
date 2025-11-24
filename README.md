# Liga Serverless - Proyecto FastAPI con AWS

## Descripción

**Liga Serverless** es una aplicación web desarrollada con **FastAPI**, que utiliza servicios de **AWS** de manera programática para implementar un entorno **serverless**.  
El proyecto permite gestionar información de una liga deportiva, incluyendo usuarios, equipos y partidos, de manera escalable y segura, sin depender de infraestructura tradicional.

Este proyecto fue desarrollado cumpliendo las siguientes reglas:

1. La infraestructura no se crea usando la consola web de AWS, todo se hace mediante scripts.
2. Se incluyen pruebas básicas de resiliencia.
3. Es una aplicación móvil.

---

## Tecnologías Utilizadas

- **Python 3.10**
- **FastAPI** – Framework web moderno y rápido.
- **Uvicorn** – Servidor ASGI para FastAPI.
- **Boto3** – Interacción con servicios de AWS.
- **AWS Lambda** – Funciones serverless.
- **API Gateway (HTTP API)** – Exposición de endpoints HTTP para Lambda.
- **DynamoDB** – Base de datos NoSQL serverless.
- **Python-JOSE** – Gestión de JWT.
- **Passlib** – Encriptación segura de contraseñas.
- **Pydantic** – Validación de datos.
- **Python-Multipart** – Manejo de formularios y archivos.
- **Mangum** – Ejecutar aplicaciones ASGI en AWS Lambda.
- **Annotated-Types / Annotated-Doc / AnyIO / Sniffio / Starlette** – Utilidades y dependencias de FastAPI.
- **DNSpython / ECDSA / RSA / Six / Typing-Extensions / Typing-Inspection / Email-Validator** – Librerías auxiliares de validación, seguridad y compatibilidad.

---

## Requisitos

1. Python 3.10.
2. Git instalado.  
3. VS Code recomendado (con extensión de Python).  

Instalar dependencias:

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt