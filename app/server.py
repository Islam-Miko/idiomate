from fastapi import FastAPI

from app.configure_app import lifespan
from core.settings import get_settings

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def check_health():
    settings = get_settings()
    return {"ok": True, "env": settings.ENVIRONMENT}
