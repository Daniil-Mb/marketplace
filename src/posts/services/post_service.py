from math import ceil
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.post_model import Post
from src.files.exceptions import (
    ImageTooLargeException,
    InvalidImageTypeException,
)
from src.files.services.file_service import FileService
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
    def __init__(
        self,
        session: AsyncSession,
        file_service: FileService | None = None,
    ) -> None:
        self.session = session
        self.post_repository = PostRepository(session)
        self.category_repository = CategoryRepository(session)
        self.file_service = file_service or FileService()

    async def create(
        self,
        *,
        title: str,
        content: str,
        category_id: int,
        user_id: UUID,
        image: UploadFile | None = None,
    ) -> Post:
        category = await self.category_repository.get_by_id(category_id)

        if category is None:
            raise CategoryDoesNotExistException

        object_key: str | None = None
        image_url: str | None = None

        try:
            if image is not None:
                object_key = await self.file_service.upload_image(image)
                image_url = self.file_service.build_public_url(object_key)

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

        except (InvalidImageTypeException, ImageTooLargeException):
            await self.session.rollback()
            raise

        except Exception:
            if object_key is not None:
                self.file_service.delete_object(object_key)

            await self.session.rollback()
            raise

    async def get_by_id(self, post_id: UUID) -> Post:
        post = await self.post_repository.get_by_id(post_id)

        if post is None:
            raise PostNotFoundException

        return post

    async def get_list(
        self,
        *,
        page_number: int,
        page_size: int,
        search: str | None = None,
        category_id: int | None = None,
    ) -> dict[str, object]:
        offset = (page_number - 1) * page_size

        total = await self.post_repository.get_total_count(
            search=search,
            category_id=category_id,
        )

        items = await self.post_repository.get_list(
            offset=offset,
            limit=page_size,
            search=search,
            category_id=category_id,
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
        image: UploadFile | None = None,
    ) -> Post:
        post = await self.get_by_id(post_id)

        if post.user_id != user_id:
            raise UserHasNoAccessException

        if category_id is not None:
            category = await self.category_repository.get_by_id(category_id)

            if category is None:
                raise CategoryDoesNotExistException

        old_image_url = post.image_url
        new_object_key: str | None = None
        new_image_url: str | None = None

        try:
            if image is not None:
                new_object_key = await self.file_service.upload_image(image)
                new_image_url = self.file_service.build_public_url(new_object_key)

            post = await self.post_repository.update(
                post,
                title=title,
                content=content,
                category_id=category_id,
                image_url=new_image_url,
            )

            await self.session.commit()
            await self.session.refresh(post)

        except (InvalidImageTypeException, ImageTooLargeException):
            await self.session.rollback()
            raise

        except Exception:
            if new_object_key is not None:
                self.file_service.delete_object(new_object_key)

            await self.session.rollback()
            raise

        if image is not None and old_image_url:
            self.file_service.delete_image(old_image_url)

        return post

    async def delete(
        self,
        *,
        post_id: UUID,
        user_id: UUID,
    ) -> None:
        post = await self.post_repository.get_by_id(post_id)

        if post is None:
            raise PostNotFoundException

        if post.user_id != user_id:
            raise UserHasNoAccessException

        await self.post_repository.move_to_deleted(post)

        await self.session.commit()
