from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Contributor(Base):
    __tablename__ = "contributor"

    contributor_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    repo_id: Mapped[int] = mapped_column(
        ForeignKey("repository.repo_id"),
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    permission: Mapped[str | None] = mapped_column(
        String(50)
    )

    # Relationship
    repository: Mapped["Repository"] = relationship(
        back_populates="contributors"
    )

