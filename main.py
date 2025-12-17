from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users.routes import router as users_router
from app.images.routes import router as images_router
from mangum import Mangum

app = FastAPI(title="Liga Serverless API")

# CORS para permitir peticiones desde la app #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de usuarios #
app.include_router(users_router, prefix="/users")
app.include_router(images_router, prefix="/images")

@app.get("/")
def root():
    return {"message": "Liga Serverless API funcionando"}

# Handler para AWS Lambda #
handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)

# Para desarrollo local #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)