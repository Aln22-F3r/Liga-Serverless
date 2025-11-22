from fastapi import FastAPI
from datetime import datetime
from app.users.routes import router as users_router

app = FastAPI(title="Liga Serverless API")

# Rutas
app.include_router(users_router, prefix="/users")

@app.get("/")
def root():
    return {"message": "Liga Serverless API funcionando"}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
