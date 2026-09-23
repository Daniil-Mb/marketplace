from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.category_model import Category
from src.posts.exceptions.category_already_exists_exception import (
    CategoryAlreadyExistsException,
)
from src.posts.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = CategoryRepository(session)

    async def create(
        self,
        name: str,
    ) -> Category:
        existing_category = await self.repository.get_by_name(name)

        if existing_category:
            raise CategoryAlreadyExistsException

        category = await self.repository.create(name)

        await self.session.commit()

        await self.session.refresh(category)

        return category

    async def get_all(self):
        return await self.repository.get_all()
