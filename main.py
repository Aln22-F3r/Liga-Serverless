from fastapi import FastAPI
from mangum import Mangum
from app.users.routes import router as users_router

app = FastAPI(title="Liga Serverless API")

# Rutas de usuario
app.include_router(users_router, prefix="/users")

# Handler para Lambda
handler = Mangum(app)
