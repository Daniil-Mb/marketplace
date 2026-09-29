from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from src.core.config import settings
from src.core.database.helpers.base_model import Base
from src.core.database.helpers.db_helper import get_session
from src.core.dependencies import get_db_session
from src.main import app


@pytest.fixture(autouse=True)
def mock_celery_tasks():
    """Мокаем Celery, чтобы тесты не требовали RabbitMQ."""
    with patch(
        "src.auth.services.auth_service.send_welcome_email.delay"
    ) as mock_delay:
        yield mock_delay


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncEngine:
    engine = create_async_engine(settings.test_database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncSession:
    async with test_engine.connect() as conn:
        trans = await conn.begin()

        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    async def override():
        yield db_session

    app.dependency_overrides[get_session] = override
    app.dependency_overrides[get_db_session] = override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
