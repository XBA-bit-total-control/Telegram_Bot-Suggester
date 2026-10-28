from sqlalchemy import String, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class BasketProduct(Base):
    __tablename__ = "baskets_products"

    __table_args__ = (
        UniqueConstraint(
            "basket_id",
            "product_id",
            name="uq_baskets_products_pair",
        ),
    )

    basket_id: Mapped[UUID] = mapped_column(ForeignKey("basket.id"), nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)


class Product(Base):
    __tablename__ = "product"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    image_key: Mapped[str] = mapped_column(String(255), nullable=False)
    baskets: Mapped[list["Basket"]] = relationship(
        back_populates="products",
        secondary="baskets_products"
    )
