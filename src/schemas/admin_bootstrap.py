from pydantic import BaseModel, Field


class AdminBootstrapRequest(BaseModel):
    telegram_id: int = Field(gt=0)
