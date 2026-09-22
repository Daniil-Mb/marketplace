from fastapi import FastAPI

from src.core.config import get_settings
from src.core.logging.config import setup_logging

settings = get_settings()

setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
