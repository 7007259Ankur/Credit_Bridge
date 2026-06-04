"""MerchantAgent — business reputation and transaction consistency scoring."""
from agents.base_agent import BaseAgent, AgentResult
from agents.tools.mock_data_loader import load_merchant


class MerchantAgent(BaseAgent):
    name = "MerchantAgent"
    default_weight = 0.10

    def score(self, user_id: int, **kwargs) -> AgentResult:
        df = load_merchant(user_id)

        if df.empty:
            return AgentResult(
                agent=self.name, sub_score=50, weight=self.weight,
                explanation="No merchant transaction data available.",
                signals=[], confidence=0.3,
            )

        # Expected columns: transaction_date, merchant_name, amount, disputed (bool)
        total_txn = len(df)
        dispute_rate = df["disputed"].mean() if "disputed" in df.columns else 0
        unique_merchants = df["merchant_name"].nunique() if "merchant_name" in df.columns else 1
        total_amount = df["amount"].sum() if "amount" in df.columns else 0

        activity_score = min(50, total_txn)
        dispute_penalty = dispute_rate * 40
        diversity_bonus = min(20, unique_merchants * 2)
        raw_score = self._clamp(activity_score - dispute_penalty + diversity_bonus + 30)

        signals = ["merchant_activity"]
        if dispute_rate < 0.02:
            signals.append("low_dispute_rate")
        if unique_merchants > 10:
            signals.append("diverse_merchant_usage")
        if dispute_rate > 0.1:
            signals.append("high_dispute_rate")

        explanation = (
            f"{total_txn} transactions across {unique_merchants} merchants, "
            f"₹{total_amount:,.0f} total, {dispute_rate*100:.1f}% disputed."
        )

        return AgentResult(
            agent=self.name,
            sub_score=raw_score,
            weight=self.weight,
            explanation=explanation,
            signals=signals,
            confidence=min(0.85, 0.4 + total_txn / 100),
            data_snapshot={"total_txn": total_txn, "dispute_rate": round(dispute_rate, 3)},
        )
