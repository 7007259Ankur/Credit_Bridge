"""CashflowAgent — bank statement pattern analysis (highest weight: 0.25)."""
import numpy as np
from agents.base_agent import BaseAgent, AgentResult
from agents.tools.mock_data_loader import load_bank_transactions


class CashflowAgent(BaseAgent):
    name = "CashflowAgent"
    default_weight = 0.25

    def score(self, user_id: int, **kwargs) -> AgentResult:
        df = load_bank_transactions(user_id)

        if df.empty:
            return AgentResult(
                agent=self.name, sub_score=50, weight=self.weight,
                explanation="No bank transaction data available.",
                signals=[], confidence=0.3,
            )

        # Expected columns: date, amount, type (credit/debit), category, balance
        credits = df[df["type"] == "credit"]["amount"] if "type" in df.columns else df["amount"]
        debits = df[df["type"] == "debit"]["amount"] if "type" in df.columns else df["amount"]

        monthly_income = credits.sum() / max(1, df["date"].nunique() / 30) if "date" in df.columns else credits.sum()
        monthly_expense = debits.sum() / max(1, df["date"].nunique() / 30) if "date" in df.columns else debits.sum()
        savings_ratio = max(0, (monthly_income - monthly_expense) / monthly_income) if monthly_income > 0 else 0

        # Balance trend (positive = improving)
        has_balance = "balance" in df.columns and df["balance"].notna().any()
        balance_trend = 0
        if has_balance:
            balance_trend = (df["balance"].iloc[-1] - df["balance"].iloc[0]) / max(1, abs(df["balance"].iloc[0]))

        savings_score = savings_ratio * 50
        stability_score = min(30, abs(balance_trend) * 100) if balance_trend > 0 else 0
        income_score = min(20, monthly_income / 10000 * 5)
        raw_score = self._clamp(savings_score + stability_score + income_score + 20)

        signals = ["cashflow_analysis"]
        if savings_ratio > 0.2:
            signals.append("healthy_savings_rate")
        if savings_ratio < 0.05:
            signals.append("low_savings_rate")
        if balance_trend > 0:
            signals.append("positive_balance_trend")
        if monthly_income > 0:
            signals.append("regular_income_detected")

        explanation = (
            f"Monthly income ~₹{monthly_income:,.0f}, expenses ~₹{monthly_expense:,.0f}, "
            f"savings ratio {savings_ratio*100:.0f}%."
        )

        return AgentResult(
            agent=self.name,
            sub_score=raw_score,
            weight=self.weight,
            explanation=explanation,
            signals=signals,
            confidence=min(0.92, 0.5 + len(df) / 200),
            data_snapshot={
                "monthly_income": round(monthly_income, 2),
                "monthly_expense": round(monthly_expense, 2),
                "savings_ratio": round(savings_ratio, 3),
            },
        )
