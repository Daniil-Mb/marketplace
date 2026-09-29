from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.auth_service import hash_password
from src.core.database.models.category_model import Category
from src.core.database.models.user_model import User

TEST_USER_EMAIL = "posts@example.com"
TEST_USER_PASSWORD = "password123"

SECOND_USER_EMAIL = "second@example.com"
SECOND_USER_PASSWORD = "password123"


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        email=TEST_USER_EMAIL,
        password_hash=hash_password(TEST_USER_PASSWORD),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def second_user(db_session: AsyncSession) -> User:
    user = User(
        email=SECOND_USER_EMAIL,
        password_hash=hash_password(SECOND_USER_PASSWORD),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession) -> Category:
    category = Category(name="Test Category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient,
    test_user: User,
) -> AsyncClient:
    response = await client.post(
        "/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 200
    return client


@pytest_asyncio.fixture
async def second_authenticated_client(
    client: AsyncClient,
    second_user: User,
) -> AsyncClient:
    response = await client.post(
        "/auth/login",
        json={
            "email": SECOND_USER_EMAIL,
            "password": SECOND_USER_PASSWORD,
        },
    )
    assert response.status_code == 200
    return client


@pytest.fixture(autouse=True)
def mock_file_service(monkeypatch):
    """
    Заменяем FileService на мок, чтобы интеграционные тесты
    не ходили в RustFS/S3.
    """
    fake = MagicMock()
    fake.upload_image = AsyncMock(return_value="posts/fake.jpg")
    fake.build_public_url = MagicMock(
        return_value="http://localhost:9000/post-images/posts/fake.jpg",
    )
    fake.delete_object = MagicMock(return_value=None)
    fake.delete_image = MagicMock(return_value=None)

    import src.posts.routes as routes_module
    import src.posts.services.post_service as service_module

    monkeypatch.setattr(
        routes_module, "FileService", lambda *a, **kw: fake,
    )
    monkeypatch.setattr(
        service_module, "FileService", lambda *a, **kw: fake,
    )

    return fake
