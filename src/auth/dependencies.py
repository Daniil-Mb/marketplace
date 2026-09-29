from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.user_repository import UserRepository
from src.core.database.helpers.db_helper import get_session
from src.core.database.models.user_model import User


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User:
    user_id: UUID | None = getattr(
        request.state,
        "user_id",
        None,
    )

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    repository = UserRepository(session)

    user = await repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_optional_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User | None:
    user_id: UUID | None = getattr(
        request.state,
        "user_id",
        None,
    )

    if user_id is None:
        return None

    repository = UserRepository(session)

    return await repository.get_by_id(user_id)
