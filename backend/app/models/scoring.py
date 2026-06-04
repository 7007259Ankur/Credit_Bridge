import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, JSON
from app.core.database import Base


class RunStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class ScoreBand(str, enum.Enum):
    poor = "poor"           # 300-579
    fair = "fair"           # 580-669
    good = "good"           # 670-739
    very_good = "very_good" # 740-799
    exceptional = "exceptional"  # 800-850


class ScoringRun(Base):
    __tablename__ = "scoring_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    celery_task_id = Column(String, nullable=True)
    status = Column(Enum(RunStatus), default=RunStatus.pending)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)


class AgentScore(Base):
    __tablename__ = "agent_scores"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("scoring_runs.id"), nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    raw_score = Column(Float, nullable=False)       # 0-100
    weight = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(String, nullable=False)
    signals = Column(JSON, nullable=True)
    data_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CreditScore(Base):
    __tablename__ = "credit_scores"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("scoring_runs.id"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    final_score = Column(Integer, nullable=False)   # 300-850
    score_band = Column(Enum(ScoreBand), nullable=False)
    recommendation = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
