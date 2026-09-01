from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
class Branch(Base):
    __tablename__ = "branch"

    branch_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    repo_id: Mapped[int] = mapped_column(
        ForeignKey("repository.repo_id"),
        nullable=False
    )

    branch_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(
        back_populates="branches"
    )

    pull_requests: Mapped[list["PullRequest"]] = relationship(
        back_populates="branch"
    )
