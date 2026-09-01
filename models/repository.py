from datetime import datetime

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Repository(Base):
    __tablename__ = "repository"

    repo_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    github_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    url: Mapped[str] = mapped_column(
        String(512),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False
    )

    # Relationships
    branches: Mapped[list["Branch"]] = relationship(
        back_populates="repository"
    )

    contributors: Mapped[list["Contributor"]] = relationship(
        back_populates="repository"
    )
