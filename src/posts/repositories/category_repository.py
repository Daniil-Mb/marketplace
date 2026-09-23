from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.category_model import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        category_id: int,
    ) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == category_id),
        )

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.name == name),
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        result = await self.session.execute(
            select(Category).order_by(Category.id),
        )

        return list(result.scalars().all())

    async def create(
        self,
        name: str,
    ) -> Category:
        category = Category(
            name=name,
        )

        self.session.add(category)

        await self.session.flush()

        return category
