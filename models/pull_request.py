from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from base import OrmBase

if TYPE_CHECKING:
    from .branch import Branch
    from .commit import Commit


class PullRequest(OrmBase):
    __tablename__ = "pull_request"

    pr_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,)

    pr_number: Mapped[int] = mapped_column( nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    branch: Mapped["Branch"] = relationship(back_populates="pull_requests")
    commits: Mapped[list["Commit"]] = relationship(
        back_populates="pull_request", cascade="all, delete-orphan"
    )