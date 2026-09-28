from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.helpers.db_helper import get_session
from src.files.dependencies import get_file_service
from src.files.services.file_service import FileService
from src.posts.services.post_service import PostService


async def get_post_service(
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
) -> PostService:
    return PostService(
        session=session,
        file_service=file_service,
    )
