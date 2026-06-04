"""PhoneBillAgent — payment consistency scoring via telecom data."""
import numpy as np
from agents.base_agent import BaseAgent, AgentResult
from agents.tools.mock_data_loader import load_phone_bills


class PhoneBillAgent(BaseAgent):
    name = "PhoneBillAgent"
    default_weight = 0.15

    def score(self, user_id: int, **kwargs) -> AgentResult:
        df = load_phone_bills(user_id)

        if df.empty:
            return AgentResult(
                agent=self.name, sub_score=50, weight=self.weight,
                explanation="No phone bill data available, using neutral score.",
                signals=[], confidence=0.3,
            )

        # Expect columns: month, paid_on_time (bool), days_late (int), amount
        total = len(df)
        on_time = df["paid_on_time"].sum() if "paid_on_time" in df.columns else total
        avg_days_late = df["days_late"].mean() if "days_late" in df.columns else 0

        on_time_ratio = on_time / total
        consistency_score = on_time_ratio * 80
        punctuality_bonus = max(0, 20 - avg_days_late * 2)
        raw_score = self._clamp(consistency_score + punctuality_bonus)

        signals = ["payment_consistency", "bill_regularity"]
        if on_time_ratio == 1.0:
            signals.append("perfect_payment_record")
        if avg_days_late > 10:
            signals.append("frequent_late_payments")

        explanation = (
            f"{int(on_time)} of {total} months paid on time "
            f"({on_time_ratio*100:.0f}%), avg {avg_days_late:.1f} days late."
        )

        return AgentResult(
            agent=self.name,
            sub_score=raw_score,
            weight=self.weight,
            explanation=explanation,
            signals=signals,
            confidence=min(0.95, 0.5 + total / 24),
            data_snapshot={"total_months": total, "on_time": int(on_time)},
        )
