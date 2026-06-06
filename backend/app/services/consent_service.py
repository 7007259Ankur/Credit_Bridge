from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.consent import SourceType
from app.repositories import consent_repo, audit_repo
from app.schemas.consent import ConsentStatus, ConsentStatusResponse


def grant(db: Session, user_id: int, source_type: SourceType) -> ConsentStatus:
    consent = consent_repo.grant_consent(db, user_id, source_type)
    audit_repo.log(db, "consent.granted", user_id=user_id,
                   metadata={"source_type": source_type.value if hasattr(source_type, 'value') else source_type})
    return ConsentStatus(
        source_type=source_type,
        granted=True,
        granted_at=consent.granted_at,
    )


def revoke(db: Session, user_id: int, source_type: SourceType) -> ConsentStatus:
    consent = consent_repo.revoke_consent(db, user_id, source_type)
    if not consent:
        raise HTTPException(status_code=404, detail="No active consent found")
    audit_repo.log(db, "consent.revoked", user_id=user_id,
                   metadata={"source_type": source_type.value if hasattr(source_type, 'value') else source_type})
    return ConsentStatus(
        source_type=source_type,
        granted=False,
        granted_at=consent.granted_at,
        revoked_at=consent.revoked_at,
    )


def get_status(db: Session, user_id: int) -> ConsentStatusResponse:
    all_consents = consent_repo.get_all_consents(db, user_id)
    granted_types = {c.source_type for c in all_consents if c.is_active}

    statuses = []
    for st in SourceType:
        c = next((x for x in all_consents if x.source_type == st), None)
        statuses.append(ConsentStatus(
            source_type=st,
            granted=st in granted_types,
            granted_at=c.granted_at if c else None,
            revoked_at=c.revoked_at if c else None,
        ))
    return ConsentStatusResponse(consents=statuses)
