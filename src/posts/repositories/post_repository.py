from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.deleted_post_model import DeletedPost
from src.core.database.models.post_model import Post
from src.posts.repositories.mixins.post_filter_mixin import (
    PostFilterMixin,
)


class PostRepository(PostFilterMixin):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        post_id: UUID,
    ) -> Post | None:
        result = await self.session.execute(
            select(Post).where(Post.id == post_id),
        )

        return result.scalar_one_or_none()

    async def get_total_count(
        self,
        *,
        search: str | None = None,
        category_id: int | None = None,
    ) -> int:
        query = select(func.count(Post.id))

        query = self.apply_category_filter(
            query,
            category_id,
        )

        query = self.apply_search_filter(
            query,
            search,
        )

        result = await self.session.execute(query)

        return result.scalar_one() or 0

    async def get_list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        category_id: int | None = None,
    ) -> list[Post]:
        query = select(Post)

        query = self.apply_category_filter(
            query,
            category_id,
        )

        query = self.apply_search_filter(
            query,
            search,
        )

        query = self.apply_search_order(
            query,
            search,
        )

        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def create(
        self,
        *,
        title: str,
        content: str,
        category_id: int,
        user_id: UUID,
        image_url: str | None = None,
    ) -> Post:
        post = Post(
            title=title,
            content=content,
            category_id=category_id,
            user_id=user_id,
            image_url=image_url,
        )

        self.session.add(post)

        await self.session.flush()

        return post

    async def update(
        self,
        post: Post,
        *,
        title: str | None = None,
        content: str | None = None,
        category_id: int | None = None,
        image_url: str | None = None,
    ) -> Post:
        if title is not None:
            post.title = title

        if content is not None:
            post.content = content

        if category_id is not None:
            post.category_id = category_id

        if image_url is not None:
            post.image_url = image_url

        await self.session.flush()

        return post

    async def move_to_deleted(
        self,
        post: Post,
    ) -> None:
        deleted_post = DeletedPost(
            original_post_id=post.id,
            title=post.title,
            content=post.content,
            image_url=post.image_url,
            user_id=post.user_id,
            category_id=post.category_id,
            created_at=post.created_at,
            updated_at=post.updated_at,
            deleted_at=datetime.now(UTC),
        )

        self.session.add(deleted_post)

        await self.session.delete(post)
