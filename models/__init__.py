"""
SQLAlchemy ORM models for the Repository Dashboard.

Conventions
-----------
* Every model has a single ``id`` column that is its **foreign key** into
  the parent entity (or ``None`` for the root ``Repository``).
* The auto-increment primary key is always named ``pk``.
* Bidirectional relationships use matching ``back_populates`` names.

This package is split into one module per model. All models are imported
here so that SQLAlchemy's mapper configuration can resolve the string-based
type hints used in ``relationship()`` calls (e.g. ``Mapped["Branch"]``)
regardless of which module is imported first.
"""

from models.base import OrmBase
from models.repository import Repository
from models.branch import Branch
from models.pull_request import PullRequest
from models.commit import Commit
from models.contributor import Contributor

__all__ = [
    "OrmBase",
    "Repository",
    "Branch",
    "PullRequest",
    "Commit",
    "Contributor",
]