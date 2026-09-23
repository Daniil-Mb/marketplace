from fastapi import FastAPI

from src.auth.routes import router as auth_router
from src.core.config import get_settings
from src.core.logging.config import setup_logging
from src.core.middleware.auth import AuthMiddleware
from src.posts.routes import router as posts_router

settings = get_settings()

setup_logging()

app = FastAPI(
    title=settings.app_name,
)

app.add_middleware(AuthMiddleware)

app.include_router(auth_router)
app.include_router(posts_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
