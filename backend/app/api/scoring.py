from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.services import scoring_service
from app.schemas.scoring import ScoringInitiateResponse, RunStatusResponse, ScoringResultResponse
from app.repositories import scoring_repo

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/initiate", response_model=ScoringInitiateResponse, status_code=202)
def initiate_scoring(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return scoring_service.initiate(db, current_user.id)


@router.get("/{run_id}/status", response_model=RunStatusResponse)
def run_status(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return scoring_service.get_run_status(db, run_id, current_user.id)


@router.get("/{run_id}/result", response_model=ScoringResultResponse)
def run_result(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return scoring_service.get_result(db, run_id, current_user.id)


@router.get("/user/{user_id}/latest")
def get_user_latest_score(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.bank_officer, UserRole.admin)),
):
    """Bank officer: get latest credit score for an applicant."""
    from app.models.scoring import CreditScore, ScoringRun, AgentScore
    cs = (
        db.query(CreditScore)
        .filter(CreditScore.user_id == user_id)
        .order_by(CreditScore.created_at.desc())
        .first()
    )
    if not cs:
        raise HTTPException(status_code=404, detail="No scores found for user")

    agent_scores = db.query(AgentScore).filter(AgentScore.run_id == cs.run_id).all()
    return {
        "run_id": cs.run_id,
        "final_score": cs.final_score,
        "score_band": cs.score_band,
        "recommendation": cs.recommendation,
        "agent_scores": [
            {
                "agent_name": a.agent_name,
                "raw_score": a.raw_score,
                "weight": a.weight,
                "confidence": a.confidence,
                "explanation": a.explanation,
                "signals": a.signals,
            }
            for a in agent_scores
        ],
        "created_at": cs.created_at,
    }
