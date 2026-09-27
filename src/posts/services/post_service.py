from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.post_model import Post
from src.posts.exceptions.category_does_not_exist_exception import (
    CategoryDoesNotExistException,
)
from src.posts.exceptions.post_not_found_exception import (
    PostNotFoundException,
)
from src.posts.exceptions.user_has_no_access_exception import (
    UserHasNoAccessException,
)
from src.posts.repositories.category_repository import CategoryRepository
from src.posts.repositories.post_repository import PostRepository


class PostService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.post_repository = PostRepository(session)
        self.category_repository = CategoryRepository(session)

    async def create(
        self,
        *,
        title: str,
        content: str,
        category_id: int,
        user_id: UUID,
        image_url: str | None = None,
    ) -> Post:
        category = await self.category_repository.get_by_id(
            category_id,
        )

        if category is None:
            raise CategoryDoesNotExistException

        post = await self.post_repository.create(
            title=title,
            content=content,
            category_id=category_id,
            user_id=user_id,
            image_url=image_url,
        )

        await self.session.commit()
        await self.session.refresh(post)

        return post

    async def get_by_id(
        self,
        post_id: UUID,
    ) -> Post:
        post = await self.post_repository.get_by_id(post_id)

        if post is None:
            raise PostNotFoundException

        return post

    async def get_list(
        self,
        *,
        page_number: int,
        page_size: int,
    ) -> dict[str, object]:
        offset = (page_number - 1) * page_size

        total = await self.post_repository.get_total_count()

        items = await self.post_repository.get_list(
            offset=offset,
            limit=page_size,
        )

        pages = ceil(total / page_size) if total else 0

        return {
            "items": items,
            "total": total,
            "page": page_number,
            "page_size": page_size,
            "pages": pages,
        }

    async def update(
        self,
        *,
        post_id: UUID,
        user_id: UUID,
        title: str | None = None,
        content: str | None = None,
        category_id: int | None = None,
        image_url: str | None = None,
    ) -> Post:
        post = await self.get_by_id(post_id)

        if post.user_id != user_id:
            raise UserHasNoAccessException

        if category_id is not None:
            category = await self.category_repository.get_by_id(
                category_id,
            )

            if category is None:
                raise CategoryDoesNotExistException

        post = await self.post_repository.update(
            post,
            title=title,
            content=content,
            category_id=category_id,
            image_url=image_url,
        )

        await self.session.commit()
        await self.session.refresh(post)

        return post

    async def delete(
        self,
        *,
        post_id: UUID,
        user_id: UUID,
    ) -> None:
        post = await self.get_by_id(post_id)

        if post.user_id != user_id:
            raise UserHasNoAccessException

        await self.post_repository.delete(post)

        await self.session.commit()
