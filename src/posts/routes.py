from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.core.database.helpers.db_helper import get_session
from src.core.database.models.user_model import User
from src.posts.exceptions.category_already_exists_exception import (
    CategoryAlreadyExistsException,
)
from src.posts.exceptions.category_does_not_exist_exception import (
    CategoryDoesNotExistException,
)
from src.posts.exceptions.post_not_found_exception import (
    PostNotFoundException,
)
from src.posts.exceptions.user_has_no_access_exception import (
    UserHasNoAccessException,
)
from src.posts.schemas.category_schema import CategorySchema
from src.posts.schemas.create_category_schema import CreateCategorySchema
from src.posts.schemas.create_post_schema import CreatePostSchema
from src.posts.schemas.post_paginate_schema import PostPaginateSchema
from src.posts.schemas.posts_schema import PostSchema
from src.posts.schemas.update_post_schema import UpdatePostSchema
from src.posts.services.category_service import CategoryService
from src.posts.services.post_service import PostService

router = APIRouter(
    tags=["Posts"],
)


def get_category_service(
    session: AsyncSession = Depends(get_session),
) -> CategoryService:
    return CategoryService(session)


def get_post_service(
    session: AsyncSession = Depends(get_session),
) -> PostService:
    return PostService(session)


@router.post(
    "/categories",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
    tags=["Categories"],
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
    "/categories",
    response_model=list[CategorySchema],
    tags=["Categories"],
)
async def get_categories(
    service: CategoryService = Depends(get_category_service),
) -> list[CategorySchema]:
    categories = await service.get_all()

    return [CategorySchema.model_validate(category) for category in categories]


@router.post(
    "/posts",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    data: CreatePostSchema,
    service: PostService = Depends(get_post_service),
    user: User = Depends(get_current_user),
) -> PostSchema:
    try:
        post = await service.create(
            title=data.title,
            content=data.content,
            category_id=data.category_id,
            user_id=user.id,
            image_url=data.image_url,
        )
    except CategoryDoesNotExistException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        ) from exc

    return PostSchema.model_validate(post)


@router.get(
    "/posts",
    response_model=PostPaginateSchema,
)
async def get_posts(
    page_number: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=255,
    ),
    category_id: int | None = Query(
        default=None,
        gt=0,
    ),
    service: PostService = Depends(get_post_service),
) -> PostPaginateSchema:
    result = await service.get_list(
        page_number=page_number,
        page_size=page_size,
        search=search,
        category_id=category_id,
    )

    return PostPaginateSchema.model_validate(result)


@router.get(
    "/posts/{post_id}",
    response_model=PostSchema,
)
async def get_post(
    post_id: UUID,
    service: PostService = Depends(get_post_service),
) -> PostSchema:
    try:
        post = await service.get_by_id(post_id)
    except PostNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        ) from exc

    return PostSchema.model_validate(post)


@router.patch(
    "/posts/{post_id}",
    response_model=PostSchema,
)
async def update_post(
    post_id: UUID,
    data: UpdatePostSchema,
    service: PostService = Depends(get_post_service),
    user: User = Depends(get_current_user),
) -> PostSchema:
    try:
        post = await service.update(
            post_id=post_id,
            user_id=user.id,
            title=data.title,
            content=data.content,
            category_id=data.category_id,
            image_url=data.image_url,
        )
    except PostNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        ) from exc
    except CategoryDoesNotExistException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        ) from exc
    except UserHasNoAccessException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this post",
        ) from exc

    return PostSchema.model_validate(post)


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: UUID,
    service: PostService = Depends(get_post_service),
    user: User = Depends(get_current_user),
) -> None:
    try:
        await service.delete(
            post_id=post_id,
            user_id=user.id,
        )
    except PostNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        ) from exc
    except UserHasNoAccessException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this post",
        ) from exc
