from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import OrmBase

if TYPE_CHECKING:
    from .branch import Branch
    from .contributor import Contributor


class Repository(OrmBase):
    __tablename__ = "repository"


    repo_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    github_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    branches: Mapped[list["Branch"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
    contributors: Mapped[list["Contributor"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )