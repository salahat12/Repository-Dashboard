from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Commit(Base):
    __tablename__ = "commit"

    commit_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    pr_id: Mapped[int] = mapped_column(
        ForeignKey("pull_request.pr_id"),
        nullable=False
    )

    commit_sha: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    author: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    committed_at: Mapped[datetime] = mapped_column(
        nullable=False
    )

    # Relationship
    pull_request: Mapped["PullRequest"] = relationship(
        back_populates="commits"
    )
