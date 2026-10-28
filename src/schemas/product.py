from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ProductResponse(BaseModel):
    id: UUID
    title: str = Field(..., min_length=3, max_length=255)
    image_key: str = Field(..., max_length=255)

    model_config = ConfigDict(from_attributes=True)
