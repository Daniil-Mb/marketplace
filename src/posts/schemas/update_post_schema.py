from pydantic import BaseModel, Field


class UpdatePostSchema(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    content: str | None = Field(
        default=None,
        min_length=1,
    )

    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    image_url: str | None = Field(
        default=None,
        max_length=1024,
    )
