from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from src.core.config import get_settings

settings = get_settings()


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_expire_minutes,
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> UUID:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    user_id = payload.get("sub")

    if not user_id:
        raise ValueError("Token does not contain user id")

    return UUID(user_id)
