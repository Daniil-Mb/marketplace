from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routes import router as auth_router
from src.core.config import get_settings
from src.core.logging.config import setup_logging
from src.core.middleware.auth import AuthMiddleware
from src.core.s3_client import ensure_bucket
from src.posts.routes import router as posts_router

settings = get_settings()

setup_logging()

app = FastAPI(
    title=settings.app_name,
)

app.add_middleware(AuthMiddleware)

app.include_router(auth_router)
app.include_router(posts_router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    ensure_bucket()
    yield


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
