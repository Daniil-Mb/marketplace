from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PostSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    image_url: str | None
    user_id: UUID
    category_id: int
    created_at: datetime
    updated_at: datetime
