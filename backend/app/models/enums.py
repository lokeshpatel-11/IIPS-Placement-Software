from enum import StrEnum


class UserRole(StrEnum):
    STUDENT = "student"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class TokenPurpose(StrEnum):
    ACTIVATE = "activate"
    RESET = "reset"


class CourseLevel(StrEnum):
    UG = "UG"
    PG = "PG"
    DIPLOMA = "DIPLOMA"


class VerificationStatus(StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class AcademicLevel(StrEnum):
    TENTH = "10th"
    TWELFTH = "12th"
    DIPLOMA = "diploma"
    GRADUATION = "graduation"
    POST_GRADUATION = "post_graduation"


class ImportKind(StrEnum):
    STUDENTS = "students"
    RESULTS = "results"
    COMPANIES = "companies"


class ImportStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    STATUS_CHANGE = "status_change"
    OVERRIDE = "override"
    LOGIN = "login"
