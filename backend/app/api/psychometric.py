from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.psychometric import PsychometricSubmission

router = APIRouter(prefix="/psychometric", tags=["psychometric"])

# 20 psychometric questions
QUESTIONS = [
    {"id": 1, "text": "I always pay my bills on time even when finances are tight."},
    {"id": 2, "text": "I prefer to save money rather than spend on immediate desires."},
    {"id": 3, "text": "I plan my expenses at least a month in advance."},
    {"id": 4, "text": "I avoid borrowing money from friends or family."},
    {"id": 5, "text": "I track my daily expenses carefully."},
    {"id": 6, "text": "I feel anxious when I have any unpaid debt."},
    {"id": 7, "text": "I have a clear financial goal for the next 3 years."},
    {"id": 8, "text": "I prefer stable income over high-risk high-reward opportunities."},
    {"id": 9, "text": "I compare prices before making significant purchases."},
    {"id": 10, "text": "I maintain an emergency fund for unexpected expenses."},
    {"id": 11, "text": "I am willing to take calculated risks for better returns."},
    {"id": 12, "text": "I feel responsible for the financial wellbeing of my family."},
    {"id": 13, "text": "I research thoroughly before making investment decisions."},
    {"id": 14, "text": "I would prioritize loan repayment over personal luxuries."},
    {"id": 15, "text": "I believe my financial situation will improve in the next year."},
    {"id": 16, "text": "I communicate openly about financial difficulties."},
    {"id": 17, "text": "I have a consistent spending pattern month to month."},
    {"id": 18, "text": "I understand the interest terms of any loan before accepting."},
    {"id": 19, "text": "I have successfully saved for a major purchase in the past."},
    {"id": 20, "text": "I take financial commitments very seriously."},
]


@router.get("/questions")
def get_questions():
    return {"questions": QUESTIONS}


@router.post("/submit")
def submit_answers(
    submission: PsychometricSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Store answers in Redis or DB for the agent to consume
    import redis as redis_lib
    from app.core.config import settings
    import json

    r = redis_lib.from_url(settings.REDIS_URL)
    key = f"psychometric:{current_user.id}"
    answers = {str(a.question_id): a.answer for a in submission.answers}
    r.setex(key, 86400, json.dumps(answers))  # 24hr TTL

    return {"message": "Answers submitted", "question_count": len(submission.answers)}
