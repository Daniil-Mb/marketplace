from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.schemas.login_user import LoginUserSchema
from src.auth.schemas.register_user import RegisterUserSchema
from src.auth.schemas.user_out import UserOutSchema
from src.auth.services.auth_service import AuthService
from src.core.database.helpers.db_helper import get_session
from src.core.database.models.user_model import User

router = APIRouter(prefix="/auth", tags=["Auth"])

ACCESS_TOKEN_COOKIE = "access_token"


def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(session)


@router.post(
    "/register",
    response_model=UserOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterUserSchema,
    service: AuthService = Depends(get_auth_service),
) -> UserOutSchema:
    try:
        user = await service.register(
            email=data.email,
            password=data.password,
        )
    except Exception as exc:
        if "already exists" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            ) from exc

        raise

    return UserOutSchema.model_validate(user)


@router.post("/login")
async def login(
    data: LoginUserSchema,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    from src.auth.exceptions.incorrect_password_exception import (
        IncorrectPasswordException,
    )

    try:
        token = await service.login(
            email=data.email,
            password=data.password,
        )
    except IncorrectPasswordException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        ) from exc

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60,
    )

    return {"message": "Successfully logged in"}


@router.get("/me", response_model=UserOutSchema)
async def me(
    user: User = Depends(get_current_user),
) -> UserOutSchema:
    return UserOutSchema.model_validate(user)


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
    )

    return {"message": "Successfully logged out"}
