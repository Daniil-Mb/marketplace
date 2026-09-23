from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.core.database.helpers.db_helper import get_session
from src.core.database.models.user_model import User
from src.posts.exceptions.category_already_exists_exception import (
    CategoryAlreadyExistsException,
)
from src.posts.schemas.category_schema import CategorySchema
from src.posts.schemas.create_category_schema import CreateCategorySchema
from src.posts.services.category_service import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


def get_category_service(
    session: AsyncSession = Depends(get_session),
) -> CategoryService:
    return CategoryService(session)


@router.post(
    "",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CreateCategorySchema,
    service: CategoryService = Depends(get_category_service),
    _: User = Depends(get_current_user),
) -> CategorySchema:
    try:
        category = await service.create(data.name)
    except CategoryAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        ) from exc

    return CategorySchema.model_validate(category)


@router.get(
    "",
    response_model=list[CategorySchema],
)
async def get_categories(
    service: CategoryService = Depends(get_category_service),
) -> list[CategorySchema]:
    categories = await service.get_all()

    return [CategorySchema.model_validate(category) for category in categories]
