from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions.incorrect_password_exception import (
    IncorrectPasswordException,
)
from src.auth.exceptions.multiple_validation_exception import (
    MultipleValidationException,
)
from src.auth.jwt.utils import create_access_token
from src.auth.repositories.user_repository import UserRepository
from src.auth.tasks import send_welcome_email
from src.core.database.models.user_model import User

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    async def register(
        self,
        email: str,
        password: str,
    ) -> User:
        existing_user = await self.user_repository.get_by_email(email)

        if existing_user:
            raise MultipleValidationException(
                "User with this email already exists",
            )

        user = await self.user_repository.create(
            email=email,
            password_hash=hash_password(password),
        )

        await self.session.commit()

        await self.session.refresh(user)

        send_welcome_email.delay(user.email)

        return user

    async def login(
        self,
        email: str,
        password: str,
    ) -> str:
        user = await self.user_repository.get_by_email(email)

        if user is None:
            raise IncorrectPasswordException

        if not verify_password(password, user.password_hash):
            raise IncorrectPasswordException

        return create_access_token(user.id)
