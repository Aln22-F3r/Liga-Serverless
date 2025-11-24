from fastapi import FastAPI
from app.users.routes import router as users_router
from mangum import Mangum

app = FastAPI(title="Liga Serverless API")

# Rutas de usuarios #
app.include_router(users_router, prefix="/users")

@app.get("/")
def root():
    return {"message": "Liga Serverless API funcionando"}

# Handler para AWS Lambda #
handler = Mangum(app)

# Para desarrollo local #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
