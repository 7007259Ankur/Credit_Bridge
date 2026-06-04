"""Base class for all CreditBridge scoring agents."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class AgentResult:
    def __init__(self, agent: str, sub_score: float, weight: float,
                 explanation: str, signals: list, confidence: float,
                 data_snapshot: Optional[Dict] = None):
        self.agent = agent
        self.sub_score = round(sub_score, 2)
        self.weight = weight
        self.explanation = explanation
        self.signals = signals
        self.confidence = round(confidence, 3)
        self.data_snapshot = data_snapshot

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "sub_score": self.sub_score,
            "weight": self.weight,
            "explanation": self.explanation,
            "signals": self.signals,
            "confidence": self.confidence,
            "data_snapshot": self.data_snapshot,
        }


class BaseAgent(ABC):
    name: str
    default_weight: float

    def __init__(self, weight: Optional[float] = None):
        self.weight = weight if weight is not None else self.default_weight

    @abstractmethod
    def score(self, user_id: int, **kwargs) -> AgentResult:
        """Run scoring logic and return AgentResult."""
        pass

    def _clamp(self, val: float, lo: float = 0, hi: float = 100) -> float:
        return max(lo, min(hi, val))
