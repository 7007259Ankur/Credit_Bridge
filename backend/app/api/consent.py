from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.consent import SourceType
from app.services import consent_service
from app.schemas.consent import ConsentStatus, ConsentStatusResponse

router = APIRouter(prefix="/consent", tags=["consent"])


@router.post("/{source_type}", response_model=ConsentStatus)
def grant_consent(
    source_type: SourceType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return consent_service.grant(db, current_user.id, source_type)


@router.delete("/{source_type}", response_model=ConsentStatus)
def revoke_consent(
    source_type: SourceType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return consent_service.revoke(db, current_user.id, source_type)


@router.get("/status", response_model=ConsentStatusResponse)
def consent_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return consent_service.get_status(db, current_user.id)
