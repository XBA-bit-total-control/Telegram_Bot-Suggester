from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "user"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    role: Mapped[str] = mapped_column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "role": self.role
        }
