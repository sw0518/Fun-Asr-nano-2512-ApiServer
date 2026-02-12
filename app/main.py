from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.core.model_load import model_manager
import uvicorn

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    model_manager.load_model()

app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
