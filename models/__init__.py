"""
SQLAlchemy ORM models for the Repository Dashboard.

Conventions
-----------
* Every model has a single ``id`` column that is its **foreign key** into
  the parent entity (or ``None`` for the root ``Repository``).
* The auto-increment primary key is always named ``pk``.
* Bidirectional relationships use matching ``back_populates`` names.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import OrmBase


# ---------------------------------------------------------------------------
# Repository  (root entity – ``id`` is None, no parent)
# ---------------------------------------------------------------------------

class Repository(OrmBase):
    __tablename__ = "repository"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    branches: Mapped[list["Branch"]] = relationship(back_populates="repository")
    contributors: Mapped[list["Contributor"]] = relationship(back_populates="repository")


# ---------------------------------------------------------------------------
# Branch  (fk = repository.id)
# ---------------------------------------------------------------------------

if TYPE_CHECKING:
    from .push import Push

class Branch(OrmBase):
    __tablename__ = "branch"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[int] = mapped_column(ForeignKey("repository.pk"), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    repository: Mapped["Repository"] = relationship(back_populates="branches")
    pull_requests: Mapped[list["PullRequest"]] = relationship(back_populates="branch")
    pushes: Mapped[list["Push"]] = relationship(back_populates="branch")


# ---------------------------------------------------------------------------
# Push  (fk = branch.id)
# ---------------------------------------------------------------------------

if TYPE_CHECKING:
    from .branch import Branch as _Branch
else:
    _Branch = "Branch"

class Push(OrmBase):
    __tablename__ = "push"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[int] = mapped_column(ForeignKey("branch.pk"), nullable=False)
    push_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    push_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    pushed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    branch: Mapped["Branch"] = relationship(back_populates="pushes")


# ---------------------------------------------------------------------------
# PullRequest  (fk = branch.id)
# ---------------------------------------------------------------------------

if TYPE_CHECKING:
    from .commit import Commit
else:
    Commit = "Commit"

class PullRequest(OrmBase):
    __tablename__ = "pull_request"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[int] = mapped_column(ForeignKey("branch.pk"), nullable=False)
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    branch: Mapped[Branch] = relationship(back_populates="pull_requests")
    commits: Mapped[list["Commit"]] = relationship(back_populates="pull_request")


# ---------------------------------------------------------------------------
# Commit  (fk = pull_request.id)
# ---------------------------------------------------------------------------

if TYPE_CHECKING:
    from .pull_request import PullRequest as _PR
else:
    _PR = "PullRequest"

class Commit(OrmBase):
    __tablename__ = "commit"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[int] = mapped_column(ForeignKey("pull_request.pk"), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    pull_request: Mapped["PullRequest"] = relationship(back_populates="commits")


# ---------------------------------------------------------------------------
# Contributor  (fk = repository.id)
# ---------------------------------------------------------------------------

class Contributor(OrmBase):
    __tablename__ = "contributor"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[int] = mapped_column(ForeignKey("repository.pk"), nullable=False)
    github_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    permission: Mapped[str] = mapped_column(String(50), nullable=False)

    repository: Mapped["Repository"] = relationship(back_populates="contributors")
