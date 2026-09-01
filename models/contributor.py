from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import OrmBase

if TYPE_CHECKING:
    from .repository import Repository


class Contributor(OrmBase):
    __tablename__ = "contributor"

    contributor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repository.repo_id"), nullable=False
    )
    github_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    permission: Mapped[str | None] = mapped_column(String(50), nullable=True)

    repository: Mapped["Repository"] = relationship(back_populates="contributors")