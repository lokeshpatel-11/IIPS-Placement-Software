from sqlalchemy import Boolean, ForeignKey, SmallInteger, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, enum_check
from app.models.enums import CourseLevel


class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    __table_args__ = (enum_check("level", CourseLevel, "level"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)  # e.g. "MBA"
    name: Mapped[str] = mapped_column(String(150))
    level: Mapped[str] = mapped_column(String(20))
    duration_years: Mapped[int | None] = mapped_column(SmallInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))

    specializations: Mapped[list["Specialization"]] = relationship(
        back_populates="course"
    )


class Specialization(TimestampMixin, Base):
    __tablename__ = "specializations"
    __table_args__ = (UniqueConstraint("course_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))

    course: Mapped["Course"] = relationship(back_populates="specializations")


class Batch(TimestampMixin, Base):
    """Academic batch, a first-class entity (not a free-text field on students)."""

    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(20), unique=True)  # e.g. "2024-26"
    passing_year: Mapped[int] = mapped_column(SmallInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
