from pydantic import BaseModel, Field


class PostFilterSchema(BaseModel):
    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    category_id: int | None = Field(
        default=None,
        gt=0,
    )
