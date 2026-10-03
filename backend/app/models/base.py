from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TimestampMixin(CreatedAtMixin):
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    """Rows are never hard-deleted; set deleted_at instead."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


def enum_check(column: str, enum_cls: type[Enum], name: str) -> CheckConstraint:
    """CHECK constraint built from a Python enum, so values live in one place."""
    values = ", ".join(f"'{member.value}'" for member in enum_cls)
    return CheckConstraint(f"{column} IN ({values})", name=name)
