"""PsychometricAgent — behavioral and attitudinal scoring."""
from agents.base_agent import BaseAgent, AgentResult
from agents.tools.mock_data_loader import load_psychometric


# Questions mapped to financial responsibility dimensions
DIMENSIONS = {
    "payment_intent": [1, 4, 14, 20],
    "financial_planning": [3, 7, 10, 19],
    "risk_awareness": [8, 11, 13, 18],
    "financial_stability": [2, 5, 9, 17],
    "optimism": [15, 16],
    "responsibility": [6, 12],
}


class PsychometricAgent(BaseAgent):
    name = "PsychometricAgent"
    default_weight = 0.15

    def score(self, user_id: int, **kwargs) -> AgentResult:
        answers = load_psychometric(user_id)

        if not answers:
            return AgentResult(
                agent=self.name, sub_score=50, weight=self.weight,
                explanation="No psychometric answers submitted.",
                signals=[], confidence=0.2,
            )

        # Score each dimension (1-5 Likert → normalize to 0-100)
        dimension_scores = {}
        for dim, q_ids in DIMENSIONS.items():
            vals = [int(answers.get(str(qid), 3)) for qid in q_ids]
            dim_score = (sum(vals) / (len(vals) * 5)) * 100
            dimension_scores[dim] = round(dim_score, 1)

        raw_score = self._clamp(sum(dimension_scores.values()) / len(dimension_scores))

        # Determine dominant signals
        signals = []
        if dimension_scores.get("payment_intent", 0) > 70:
            signals.append("high_payment_intent")
        if dimension_scores.get("financial_planning", 0) > 70:
            signals.append("strong_financial_planning")
        if dimension_scores.get("risk_awareness", 0) < 50:
            signals.append("low_risk_awareness")

        explanation = (
            f"Psychometric score based on {len(answers)} answers. "
            f"Payment intent: {dimension_scores.get('payment_intent', 0):.0f}/100, "
            f"Planning: {dimension_scores.get('financial_planning', 0):.0f}/100."
        )

        return AgentResult(
            agent=self.name,
            sub_score=raw_score,
            weight=self.weight,
            explanation=explanation,
            signals=signals,
            confidence=0.75,
            data_snapshot=dimension_scores,
        )
