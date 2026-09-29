from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_database_connection(db_session: AsyncSession) -> None:
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar_one() == 1


async def _table_exists(db_session: AsyncSession, name: str) -> bool:
    result = await db_session.execute(
        text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = :name)"
        ),
        {"name": name},
    )
    return result.scalar_one()


async def test_users_table_exists(db_session: AsyncSession) -> None:
    assert await _table_exists(db_session, "users") is True


async def test_posts_table_exists(db_session: AsyncSession) -> None:
    assert await _table_exists(db_session, "posts") is True


async def test_deleted_posts_table_exists(db_session: AsyncSession) -> None:
    assert await _table_exists(db_session, "deleted_posts") is True



