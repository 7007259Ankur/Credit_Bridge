from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.scoring import ScoringRun, AgentScore, CreditScore, RunStatus, ScoreBand


def create_run(db: Session, user_id: int) -> ScoringRun:
    run = ScoringRun(user_id=user_id)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def update_run_status(db: Session, run_id: int, status: RunStatus,
                       celery_task_id: str = None) -> ScoringRun:
    run = db.query(ScoringRun).filter(ScoringRun.id == run_id).first()
    run.status = status
    if celery_task_id:
        run.celery_task_id = celery_task_id
    if status in (RunStatus.completed, RunStatus.failed):
        run.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run


def get_run(db: Session, run_id: int) -> Optional[ScoringRun]:
    return db.query(ScoringRun).filter(ScoringRun.id == run_id).first()


def save_agent_score(db: Session, run_id: int, agent_data: dict) -> AgentScore:
    score = AgentScore(run_id=run_id, **agent_data)
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


def save_credit_score(db: Session, run_id: int, user_id: int,
                       final_score: int, recommendation: str) -> CreditScore:
    band = _get_band(final_score)
    cs = CreditScore(
        run_id=run_id,
        user_id=user_id,
        final_score=final_score,
        score_band=band,
        recommendation=recommendation,
    )
    db.add(cs)
    db.commit()
    db.refresh(cs)
    return cs


def get_result(db: Session, run_id: int):
    cs = db.query(CreditScore).filter(CreditScore.run_id == run_id).first()
    agent_scores = db.query(AgentScore).filter(AgentScore.run_id == run_id).all()
    return cs, agent_scores


def _get_band(score: int) -> ScoreBand:
    if score < 580:
        return ScoreBand.poor
    elif score < 670:
        return ScoreBand.fair
    elif score < 740:
        return ScoreBand.good
    elif score < 800:
        return ScoreBand.very_good
    return ScoreBand.exceptional
