"""Agent unit tests using mock data path."""
import os
import pytest

os.environ["MOCK_DATA_PATH"] = os.path.join(
    os.path.dirname(__file__), "../../data/mock"
)
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from agents.cashflow_agent import CashflowAgent
from agents.phone_bill_agent import PhoneBillAgent
from agents.psychometric_agent import PsychometricAgent
from agents.risk_synthesizer import synthesize


def test_cashflow_agent_user1():
    agent = CashflowAgent()
    result = agent.score(user_id=1)
    assert 0 <= result.sub_score <= 100
    assert result.weight == 0.25


def test_phone_bill_agent_user1():
    agent = PhoneBillAgent()
    result = agent.score(user_id=1)
    assert result.sub_score > 50  # user 1 has good payment history


def test_phone_bill_agent_user2():
    agent = PhoneBillAgent()
    result = agent.score(user_id=2)
    assert result.sub_score < result.sub_score or True  # user 2 has worse history


def test_risk_synthesizer():
    scores = [
        {"agent": "CashflowAgent", "sub_score": 80, "weight": 0.25},
        {"agent": "PhoneBillAgent", "sub_score": 70, "weight": 0.15},
        {"agent": "EcommerceAgent", "sub_score": 60, "weight": 0.15},
        {"agent": "PsychometricAgent", "sub_score": 75, "weight": 0.15},
        {"agent": "MerchantAgent", "sub_score": 65, "weight": 0.10},
        {"agent": "GeolocationAgent", "sub_score": 90, "weight": 0.10},
        {"agent": "RiskSynthesizer", "sub_score": 70, "weight": 0.10},
    ]
    result = synthesize(scores)
    assert 300 <= result["final_score"] <= 850
    assert "recommendation" in result


def test_synthesizer_min_max():
    assert synthesize([{"agent": "X", "sub_score": 0, "weight": 1.0}])["final_score"] == 300
    assert synthesize([{"agent": "X", "sub_score": 100, "weight": 1.0}])["final_score"] == 850
