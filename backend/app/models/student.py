from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, enum_check
from app.models.enums import AcademicLevel, Gender, VerificationStatus


class Student(SoftDeleteMixin, TimestampMixin, Base):
    """Placement profile. Name and phone live on `users`. 'Placed' is derived from offers."""

    __tablename__ = "students"
    __table_args__ = (
        enum_check("verification_status", VerificationStatus, "verification_status"),
        enum_check("gender", Gender, "gender"),
        CheckConstraint("cgpa BETWEEN 0 AND 10", name="cgpa_range"),
        CheckConstraint("active_backlogs >= 0", name="backlogs_non_negative"),
        CheckConstraint("gap_years >= 0", name="gap_years_non_negative"),
        CheckConstraint(
            "profile_completeness BETWEEN 0 AND 100", name="completeness_range"
        ),
        Index("ix_students_batch_course", "batch_id", "course_id"),
        Index("ix_students_verification_status", "verification_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    enrollment_no: Mapped[str] = mapped_column(String(30), unique=True, index=True)

    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    specialization_id: Mapped[int | None] = mapped_column(
        ForeignKey("specializations.id")
    )
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"))
    current_semester: Mapped[int | None] = mapped_column(SmallInteger)

    # Verified values used by the eligibility engine.
    cgpa: Mapped[float | None] = mapped_column(Numeric(4, 2))
    active_backlogs: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    gap_years: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))

    # Optional personal details. Gender is for reporting only, never a model feature.
    gender: Mapped[str | None] = mapped_column(String(20))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    linkedin_url: Mapped[str | None] = mapped_column(String(255))
    github_url: Mapped[str | None] = mapped_column(String(255))
    portfolio_url: Mapped[str | None] = mapped_column(String(255))

    placement_opt_in: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))

    verification_status: Mapped[str] = mapped_column(
        String(20), server_default=VerificationStatus.PENDING.value
    )
    verified_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_remarks: Mapped[str | None] = mapped_column(Text)
    profile_completeness: Mapped[int] = mapped_column(
        SmallInteger, server_default=text("0")
    )

    user: Mapped["User"] = relationship(foreign_keys=[user_id])  # noqa: F821
    course: Mapped["Course"] = relationship()  # noqa: F821
    specialization: Mapped["Specialization | None"] = relationship()  # noqa: F821
    batch: Mapped["Batch"] = relationship()  # noqa: F821
    academics: Mapped[list["StudentAcademic"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class StudentAcademic(TimestampMixin, Base):
    """One row per education level (10th, 12th, graduation, ...)."""

    __tablename__ = "student_academics"
    __table_args__ = (
        UniqueConstraint("student_id", "level"),
        enum_check("level", AcademicLevel, "level"),
        CheckConstraint("percentage BETWEEN 0 AND 100", name="percentage_range"),
        CheckConstraint("cgpa BETWEEN 0 AND 10", name="cgpa_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    level: Mapped[str] = mapped_column(String(20))
    institution: Mapped[str | None] = mapped_column(
        String(200)
    )  # school / board / university
    stream: Mapped[str | None] = mapped_column(String(100))
    year_of_passing: Mapped[int | None] = mapped_column(SmallInteger)
    percentage: Mapped[float | None] = mapped_column(Numeric(5, 2))
    cgpa: Mapped[float | None] = mapped_column(Numeric(4, 2))

    student: Mapped["Student"] = relationship(back_populates="academics")
