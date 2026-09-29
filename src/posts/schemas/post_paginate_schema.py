from pydantic import BaseModel, Field

from src.posts.schemas.posts_schema import PostSchema


class PostPaginateSchema(BaseModel):
    items: list[PostSchema]

    total: int

    page: int = Field(
        ge=1,
    )

    page_size: int = Field(
        ge=1,
    )

    pages: int = Field(
        ge=0,
    )
