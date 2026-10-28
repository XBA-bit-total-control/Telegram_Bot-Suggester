from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Basket(Base):
    __tablename__ = "basket"

    user_id: Mapped[UUID] = mapped_column(
        "user",
        ForeignKey("user.id"),
        unique=True,
        nullable=False
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="baskets",
        secondary="baskets_products"
    )
