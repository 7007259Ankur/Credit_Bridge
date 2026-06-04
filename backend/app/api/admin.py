import json
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_role
from app.models.user import User, UserRole
from app.schemas.scoring import WeightsConfig
from app.repositories import scoring_repo

router = APIRouter(prefix="/admin", tags=["admin"])

WEIGHTS_FILE = "weights.json"

DEFAULT_WEIGHTS = WeightsConfig()


def _load_weights() -> WeightsConfig:
    if os.path.exists(WEIGHTS_FILE):
        with open(WEIGHTS_FILE) as f:
            return WeightsConfig(**json.load(f))
    return DEFAULT_WEIGHTS


def _save_weights(w: WeightsConfig):
    with open(WEIGHTS_FILE, "w") as f:
        json.dump(w.model_dump(), f, indent=2)


@router.get("/weights", response_model=WeightsConfig)
def get_weights(current_user: User = Depends(require_role(UserRole.admin))):
    return _load_weights()


@router.put("/weights", response_model=WeightsConfig)
def update_weights(
    weights: WeightsConfig,
    current_user: User = Depends(require_role(UserRole.admin)),
):
    total = sum(weights.model_dump().values())
    if abs(total - 1.0) > 0.01:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Weights must sum to 1.0, got {total:.3f}")
    _save_weights(weights)
    return weights


@router.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    from sqlalchemy import func
    from app.models.scoring import ScoringRun, CreditScore, RunStatus

    total_runs = db.query(func.count(ScoringRun.id)).scalar()
    completed = db.query(func.count(ScoringRun.id)).filter(
        ScoringRun.status == RunStatus.completed
    ).scalar()
    avg_score = db.query(func.avg(CreditScore.final_score)).scalar()

    return {
        "total_runs": total_runs,
        "completed_runs": completed,
        "average_score": round(avg_score, 1) if avg_score else None,
    }
