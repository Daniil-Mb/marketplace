import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.auth.exceptions.incorrect_password_exception import (
    IncorrectPasswordException,
)
from src.auth.exceptions.multiple_validation_exception import (
    MultipleValidationException,
)
from src.auth.services.auth_service import (
    AuthService,
    hash_password,
    verify_password,
)
from src.core.database.models.user_model import User



def test_hash_password() -> None:
    password = "password123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)




async def test_register_success(mock_celery_tasks) -> None:
    session = AsyncMock()

    repository = MagicMock()
    repository.get_by_email = AsyncMock(return_value=None)

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="placeholder",
    )
    repository.create = AsyncMock(return_value=user)

    service = AuthService(session, user_repository=repository)

    result = await service.register(
        email="test@example.com",
        password="password123",
    )

    assert result is user

    repository.get_by_email.assert_awaited_once_with("test@example.com")
    repository.create.assert_awaited_once()

    create_call = repository.create.await_args
    assert create_call.kwargs["email"] == "test@example.com"

    hashed = create_call.kwargs["password_hash"]
    assert hashed != "password123"
    assert verify_password("password123", hashed)

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)

    mock_celery_tasks.assert_called_once_with("test@example.com")


async def test_register_duplicate_email() -> None:
    session = AsyncMock()

    existing_user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("password123"),
    )

    repository = MagicMock()
    repository.get_by_email = AsyncMock(return_value=existing_user)
    repository.create = AsyncMock()

    service = AuthService(session, user_repository=repository)

    with pytest.raises(
        MultipleValidationException,
        match="User with this email already exists",
    ):
        await service.register(
            email="test@example.com",
            password="password123",
        )

    repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()




async def test_login_success() -> None:
    session = AsyncMock()

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("password123"),
    )

    repository = MagicMock()
    repository.get_by_email = AsyncMock(return_value=user)

    service = AuthService(session, user_repository=repository)

    token = await service.login(
        email="test@example.com",
        password="password123",
    )

    assert isinstance(token, str)
    assert token

    repository.get_by_email.assert_awaited_once_with("test@example.com")


async def test_login_unknown_user() -> None:
    session = AsyncMock()

    repository = MagicMock()
    repository.get_by_email = AsyncMock(return_value=None)

    service = AuthService(session, user_repository=repository)

    with pytest.raises(IncorrectPasswordException):
        await service.login(
            email="unknown@example.com",
            password="password123",
        )


async def test_login_incorrect_password() -> None:
    session = AsyncMock()

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("password123"),
    )

    repository = MagicMock()
    repository.get_by_email = AsyncMock(return_value=user)

    service = AuthService(session, user_repository=repository)

    with pytest.raises(IncorrectPasswordException):
        await service.login(
            email="test@example.com",
            password="wrong-password",
        )
