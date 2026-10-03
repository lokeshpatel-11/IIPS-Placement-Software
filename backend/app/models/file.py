from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.base import CreatedAtMixin


class File(CreatedAtMixin, Base):
    """Metadata for every upload (resumes, marksheets, offer letters, import files)."""

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Random generated name/path; never trust the user's filename for storage.
    storage_key: Mapped[str] = mapped_column(String(255), unique=True)
    original_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
