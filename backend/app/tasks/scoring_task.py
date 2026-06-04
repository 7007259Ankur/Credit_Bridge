import sys
import os

# Ensure agents directory is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.scoring import RunStatus
from app.repositories import scoring_repo, audit_repo


@celery_app.task(bind=True, max_retries=3)
def run_scoring_pipeline(self, run_id: int, user_id: int):
    db = SessionLocal()
    try:
        scoring_repo.update_run_status(db, run_id, RunStatus.running)

        # Run the agent pipeline
        from agents.coordinator import run_pipeline
        result = run_pipeline(user_id=user_id, run_id=run_id, db=db)

        # Save agent sub-scores
        for agent_result in result["agent_results"]:
            scoring_repo.save_agent_score(db, run_id, {
                "agent_name": agent_result["agent"],
                "raw_score": agent_result["sub_score"],
                "weight": agent_result["weight"],
                "confidence": agent_result["confidence"],
                "explanation": agent_result["explanation"],
                "signals": agent_result.get("signals", []),
                "data_snapshot": agent_result.get("data_snapshot"),
            })

        # Save final credit score
        scoring_repo.save_credit_score(
            db,
            run_id=run_id,
            user_id=user_id,
            final_score=result["final_score"],
            recommendation=result["recommendation"],
        )
        scoring_repo.update_run_status(db, run_id, RunStatus.completed)
        audit_repo.log(db, "scoring.completed", user_id=user_id,
                       metadata={"run_id": run_id, "final_score": result["final_score"]})

        return {"run_id": run_id, "final_score": result["final_score"]}

    except Exception as exc:
        scoring_repo.update_run_status(db, run_id, RunStatus.failed)
        audit_repo.log(db, "scoring.failed", user_id=user_id,
                       metadata={"run_id": run_id, "error": str(exc)})
        raise self.retry(exc=exc, countdown=5)
    finally:
        db.close()
