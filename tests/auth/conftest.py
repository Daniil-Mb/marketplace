import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.auth_service import hash_password
from src.core.database.models.user_model import User

TEST_USER_EMAIL = "login@example.com"
TEST_USER_PASSWORD = "password123"


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
