from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.post_model import Post


class PostRepository:
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

    async def get_total_count(self) -> int:
        result = await self.session.execute(
            select(func.count(Post.id)),
        )

        return result.scalar_one() or 0

    async def get_list(
        self,
        offset: int,
        limit: int,
    ) -> list[Post]:
        result = await self.session.execute(
            select(Post).order_by(Post.created_at.desc()).offset(offset).limit(limit),
        )

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

    async def delete(
        self,
        post: Post,
    ) -> None:
        await self.session.delete(post)

        await self.session.flush()
