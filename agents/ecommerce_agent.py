"""EcommerceAgent — purchase behavior and creditworthiness signals."""
import numpy as np
from agents.base_agent import BaseAgent, AgentResult
from agents.tools.mock_data_loader import load_ecommerce


class EcommerceAgent(BaseAgent):
    name = "EcommerceAgent"
    default_weight = 0.15

    def score(self, user_id: int, **kwargs) -> AgentResult:
        df = load_ecommerce(user_id)

        if df.empty:
            return AgentResult(
                agent=self.name, sub_score=50, weight=self.weight,
                explanation="No e-commerce data available.",
                signals=[], confidence=0.3,
            )

        # Expected columns: order_date, amount, category, returned (bool), paid_emi (bool)
        total_orders = len(df)
        total_spend = df["amount"].sum() if "amount" in df.columns else 0
        return_rate = df["returned"].mean() if "returned" in df.columns else 0
        emi_usage = df["paid_emi"].mean() if "paid_emi" in df.columns else 0

        # Higher spend with low returns = good signal
        activity_score = min(40, total_orders * 2)
        return_penalty = return_rate * 30
        emi_bonus = emi_usage * 20  # responsible credit use
        raw_score = self._clamp(activity_score - return_penalty + emi_bonus + 40)

        signals = ["purchase_activity"]
        if return_rate < 0.05:
            signals.append("low_return_rate")
        if emi_usage > 0.3:
            signals.append("emi_credit_usage")
        if total_orders > 20:
            signals.append("high_activity")

        explanation = (
            f"{total_orders} orders, ₹{total_spend:,.0f} total spend, "
            f"{return_rate*100:.0f}% return rate, {emi_usage*100:.0f}% EMI usage."
        )

        return AgentResult(
            agent=self.name,
            sub_score=raw_score,
            weight=self.weight,
            explanation=explanation,
            signals=signals,
            confidence=min(0.9, 0.4 + total_orders / 50),
            data_snapshot={"total_orders": total_orders, "return_rate": round(return_rate, 3)},
        )
