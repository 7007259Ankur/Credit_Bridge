import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Integer, String, Boolean
from app.core.database import Base


class UserRole(str, enum.Enum):
    applicant = "applicant"
    bank_officer = "bank_officer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email_encrypted = Column(String, unique=True, nullable=False)  # AES-256 encrypted
    email_hash = Column(String, unique=True, nullable=False)       # SHA-256 for lookup
    password_hash = Column(String, nullable=False)
    full_name_encrypted = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.applicant)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
