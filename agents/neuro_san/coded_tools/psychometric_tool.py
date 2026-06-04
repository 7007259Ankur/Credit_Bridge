"""PsychometricTool — Neuro SAN CodedTool for behavioural questionnaire scoring."""
from typing import Any, Dict
from agents.neuro_san.coded_tools.base_tool import CreditBridgeCodedTool
from agents.tools.mock_data_loader import load_psychometric

DIMENSIONS = {
    "payment_intent":    [1, 4, 14, 20],
    "financial_planning":[3, 7, 10, 19],
    "risk_awareness":    [8, 11, 13, 18],
    "financial_stability":[2, 5, 9, 17],
    "optimism":          [15, 16],
    "responsibility":    [6, 12],
}


class PsychometricTool(CreditBridgeCodedTool):
    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = self._get_user_id(args, sly_data)
        answers = load_psychometric(user_id)

        if not answers:
            return {"agent": "PsychometricAgent", "sub_score": 50.0, "weight": 0.15,
                    "confidence": 0.2, "explanation": "No psychometric answers.", "signals": [], "data_snapshot": None}

        dim_scores = {}
        for dim, q_ids in DIMENSIONS.items():
            vals = [int(answers.get(str(qid), 3)) for qid in q_ids]
            dim_scores[dim] = round((sum(vals) / (len(vals) * 5)) * 100, 1)

        raw_score = self._clamp(sum(dim_scores.values()) / len(dim_scores))

        signals = []
        if dim_scores.get("payment_intent", 0) > 70:
            signals.append("high_payment_intent")
        if dim_scores.get("financial_planning", 0) > 70:
            signals.append("strong_financial_planning")
        if dim_scores.get("risk_awareness", 0) < 50:
            signals.append("low_risk_awareness")

        return {
            "agent": "PsychometricAgent",
            "sub_score": round(raw_score, 2),
            "weight": 0.15,
            "confidence": 0.75,
            "explanation": (
                f"Psychometric score from {len(answers)} answers. "
                f"Payment intent: {dim_scores.get('payment_intent',0):.0f}/100, "
                f"Planning: {dim_scores.get('financial_planning',0):.0f}/100."
            ),
            "signals": signals,
            "data_snapshot": dim_scores,
        }
