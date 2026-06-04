from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.consent import SourceType


class ConsentStatus(BaseModel):
    source_type: SourceType
    granted: bool
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConsentStatusResponse(BaseModel):
    consents: list[ConsentStatus]
