from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.consent import Consent, SourceType


def get_consent(db: Session, user_id: int, source_type: SourceType) -> Optional[Consent]:
    return (
        db.query(Consent)
        .filter(Consent.user_id == user_id, Consent.source_type == source_type)
        .order_by(Consent.granted_at.desc())
        .first()
    )


def get_all_consents(db: Session, user_id: int) -> List[Consent]:
    # Return the latest consent record per source type
    results = []
    for st in SourceType:
        c = get_consent(db, user_id, st)
        results.append(c)
    return [c for c in results if c is not None]


def grant_consent(db: Session, user_id: int, source_type: SourceType) -> Consent:
    # Revoke existing first
    existing = get_consent(db, user_id, source_type)
    if existing and existing.is_active:
        return existing  # already granted

    consent = Consent(user_id=user_id, source_type=source_type)
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent


def revoke_consent(db: Session, user_id: int, source_type: SourceType) -> Optional[Consent]:
    consent = get_consent(db, user_id, source_type)
    if consent and consent.is_active:
        consent.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(consent)
    return consent


def has_active_consent(db: Session, user_id: int, source_type: SourceType) -> bool:
    c = get_consent(db, user_id, source_type)
    return c is not None and c.is_active
