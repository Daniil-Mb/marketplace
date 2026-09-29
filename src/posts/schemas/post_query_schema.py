from pydantic import BaseModel, Field

MAX_PAGE_SIZE = 50


class PostQuerySchema(BaseModel):
    page_number: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=10,
        ge=1,
        le=MAX_PAGE_SIZE,
    )
