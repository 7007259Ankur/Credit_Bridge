from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from app.models.scoring import RunStatus, ScoreBand


class ScoringInitiateResponse(BaseModel):
    run_id: int
    status: RunStatus


class RunStatusResponse(BaseModel):
    run_id: int
    status: RunStatus
    created_at: datetime
    completed_at: Optional[datetime] = None


class AgentScoreOut(BaseModel):
    agent_name: str
    raw_score: float
    weight: float
    confidence: float
    explanation: str
    signals: Optional[List[str]] = None

    class Config:
        from_attributes = True


class ScoringResultResponse(BaseModel):
    run_id: int
    final_score: int
    score_band: ScoreBand
    recommendation: str
    agent_scores: List[AgentScoreOut]
    created_at: datetime


class WeightsConfig(BaseModel):
    cashflow: float = 0.25
    phone_bill: float = 0.15
    ecommerce: float = 0.15
    psychometric: float = 0.15
    merchant: float = 0.10
    geolocation: float = 0.10
    risk_synthesizer: float = 0.10
