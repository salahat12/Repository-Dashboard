from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import OrmBase
from . import pull_request

if TYPE_CHECKING:
    from .pull_request import PullRequest


class Commit(OrmBase):
    __tablename__ = "commit"

    commit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pr_id: Mapped[int] = mapped_column(Integer, ForeignKey("pull_request.id"), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    pull_request: Mapped["PullRequest"] = relationship(back_populates="commits")