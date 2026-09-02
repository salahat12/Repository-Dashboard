"""Branch model (fk = repository.id)."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import OrmBase

if TYPE_CHECKING:
    from .repository import Repository
    from .pull_request import PullRequest



class Branch(OrmBase):
    __tablename__ = "branch"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repository.id"), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    repository: Mapped["Repository"] = relationship(back_populates="branches")
    pull_requests: Mapped[list["PullRequest"]] = relationship(back_populates="branch")