from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import OrmBase

if TYPE_CHECKING:
    from .branch import Branch
    from .commit import Commit


class PullRequest(OrmBase):
    __tablename__ = "pull_request"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branch.id"),
        nullable=False,
    )

    pr_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    author: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    branch: Mapped["Branch"] = relationship(
        back_populates="pull_requests"
    )

    commits: Mapped[list["Commit"]] = relationship(
        back_populates="pull_request",
        cascade="all, delete-orphan",
    )