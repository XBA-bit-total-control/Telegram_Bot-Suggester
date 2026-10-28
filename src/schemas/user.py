from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    telegram_id: int
    role: str

    model_config = {"from_attributes": True}
