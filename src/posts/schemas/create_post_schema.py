from pydantic import BaseModel, Field


class CreatePostSchema(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    content: str = Field(
        min_length=1,
    )

    category_id: int = Field(
        gt=0,
    )

    image_url: str | None = Field(
        default=None,
        max_length=1024,
    )
