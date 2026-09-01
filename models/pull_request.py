from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class PullRequest(Base):
    __tablename__ = "pull_request"

    pr_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branch.branch_id"),
        nullable=False
    )

    pr_number: Mapped[int] = mapped_column(
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    state: Mapped[str | None] = mapped_column(
        String(50)
    )

    author: Mapped[str | None] = mapped_column(
        String(255)
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False
    )

    # Relationships
    branch: Mapped["Branch"] = relationship(
        back_populates="pull_requests"
    )

    commits: Mapped[list["Commit"]] = relationship(
        back_populates="pull_request"
    )
