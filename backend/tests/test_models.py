from sqlalchemy.orm import configure_mappers

import app.models  # noqa: F401
from app.core.db import Base

EXPECTED_TABLES = {
    "users",
    "password_reset_tokens",
    "refresh_tokens",
    "courses",
    "specializations",
    "batches",
    "students",
    "student_academics",
    "files",
    "import_jobs",
    "import_job_errors",
    "audit_logs",
}


def test_expected_tables_are_registered():
    assert EXPECTED_TABLES <= set(Base.metadata.tables)


def test_relationships_configure_without_errors():
    configure_mappers()
