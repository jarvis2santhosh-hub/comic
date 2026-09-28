from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI comic story creator using Gemini and Hugging Face image generation.",
)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
