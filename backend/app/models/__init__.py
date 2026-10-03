"""Import every model here so Alembic autogenerate can discover all tables."""

from app.models.audit import AuditLog  # noqa: F401
from app.models.file import File  # noqa: F401
from app.models.import_job import ImportJob, ImportJobError  # noqa: F401
from app.models.master import Batch, Course, Specialization  # noqa: F401
from app.models.student import Student, StudentAcademic  # noqa: F401
from app.models.user import PasswordResetToken, RefreshToken, User  # noqa: F401
