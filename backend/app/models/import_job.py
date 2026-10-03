from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import CreatedAtMixin, enum_check
from app.models.enums import ImportKind, ImportStatus


class ImportJob(CreatedAtMixin, Base):
    """A bulk upload (students, results, companies) tracked with progress and errors."""

    __tablename__ = "import_jobs"
    __table_args__ = (
        enum_check("kind", ImportKind, "kind"),
        enum_check("status", ImportStatus, "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"))
    status: Mapped[str] = mapped_column(
        String(20), server_default=ImportStatus.PENDING.value
    )
    total_rows: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    success_rows: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    failed_rows: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    started_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    errors: Mapped[list["ImportJobError"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class ImportJobError(Base):
    """One row per failed line, so errors can be paged, filtered and downloaded."""

    __tablename__ = "import_job_errors"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("import_jobs.id", ondelete="CASCADE"), index=True
    )
    row_number: Mapped[int] = mapped_column(Integer)
    column_name: Mapped[str | None] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text)
    raw_row: Mapped[dict | None] = mapped_column(JSONB)

    job: Mapped["ImportJob"] = relationship(back_populates="errors")
