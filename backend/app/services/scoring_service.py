from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.scoring import RunStatus
from app.repositories import scoring_repo, audit_repo
from app.schemas.scoring import ScoringInitiateResponse, RunStatusResponse, ScoringResultResponse


def initiate(db: Session, user_id: int) -> ScoringInitiateResponse:
    run = scoring_repo.create_run(db, user_id)
    audit_repo.log(db, "scoring.initiated", user_id=user_id, metadata={"run_id": run.id})

    # Import here to avoid circular imports
    from app.tasks.scoring_task import run_scoring_pipeline
    task = run_scoring_pipeline.delay(run.id, user_id)

    scoring_repo.update_run_status(db, run.id, RunStatus.running, celery_task_id=task.id)
    return ScoringInitiateResponse(run_id=run.id, status=RunStatus.running)


def get_run_status(db: Session, run_id: int, user_id: int) -> RunStatusResponse:
    run = scoring_repo.get_run(db, run_id)
    if not run or run.user_id != user_id:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunStatusResponse(
        run_id=run.id,
        status=run.status,
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


def get_result(db: Session, run_id: int, user_id: int) -> ScoringResultResponse:
    run = scoring_repo.get_run(db, run_id)
    if not run or run.user_id != user_id:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status != RunStatus.completed:
        raise HTTPException(status_code=202, detail="Scoring not completed yet")

    cs, agent_scores = scoring_repo.get_result(db, run_id)
    if not cs:
        raise HTTPException(status_code=404, detail="Score not found")

    return ScoringResultResponse(
        run_id=run_id,
        final_score=cs.final_score,
        score_band=cs.score_band,
        recommendation=cs.recommendation,
        agent_scores=agent_scores,
        created_at=cs.created_at,
    )
