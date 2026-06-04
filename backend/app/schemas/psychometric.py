from pydantic import BaseModel
from typing import List


class PsychometricAnswer(BaseModel):
    question_id: int
    answer: int  # 1-5 Likert scale


class PsychometricSubmission(BaseModel):
    answers: List[PsychometricAnswer]
