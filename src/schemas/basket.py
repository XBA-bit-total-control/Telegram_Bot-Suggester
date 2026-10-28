from pydantic import BaseModel, ConfigDict, Field

from schemas.product import ProductResponse


class BasketResponse(BaseModel):
    products: list[ProductResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(from_attributes=True)
