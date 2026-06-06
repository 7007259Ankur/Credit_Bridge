from typing import Optional
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log(db: Session, action: str, user_id: Optional[int] = None, metadata: dict = None):
    entry = AuditLog(user_id=user_id, action=action, audit_metadata=metadata or {})
    db.add(entry)
    db.commit()
