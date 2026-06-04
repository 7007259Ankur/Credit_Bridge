"""CashflowTool — Neuro SAN CodedTool for bank cashflow analysis."""
from typing import Any, Dict
from agents.neuro_san.coded_tools.base_tool import CreditBridgeCodedTool
from agents.tools.mock_data_loader import load_bank_transactions


class CashflowTool(CreditBridgeCodedTool):
    """
    Deterministic cashflow scoring from bank transaction CSV.
    Called by CashflowAgent in the Neuro SAN network.
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = self._get_user_id(args, sly_data)
        df = load_bank_transactions(user_id)

        if df.empty:
            return self._neutral("No bank transaction data available.", user_id)

        credits = df[df["type"] == "credit"]["amount"] if "type" in df.columns else df["amount"]
        debits = df[df["type"] == "debit"]["amount"] if "type" in df.columns else df["amount"]

        monthly_income = credits.sum() / max(1, df["date"].nunique() / 30) if "date" in df.columns else credits.sum()
        monthly_expense = debits.sum() / max(1, df["date"].nunique() / 30) if "date" in df.columns else debits.sum()
        savings_ratio = max(0, (monthly_income - monthly_expense) / monthly_income) if monthly_income > 0 else 0

        balance_trend = 0
        if "balance" in df.columns and df["balance"].notna().any():
            first = df["balance"].iloc[0]
            last = df["balance"].iloc[-1]
            balance_trend = (last - first) / max(1, abs(first))

        savings_score = savings_ratio * 50
        stability_score = min(30, balance_trend * 100) if balance_trend > 0 else 0
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

        return {
            "agent": "CashflowAgent",
            "sub_score": round(raw_score, 2),
            "weight": 0.25,
            "confidence": round(min(0.92, 0.5 + len(df) / 200), 3),
            "explanation": (
                f"Monthly income ~₹{monthly_income:,.0f}, "
                f"expenses ~₹{monthly_expense:,.0f}, "
                f"savings ratio {savings_ratio*100:.0f}%."
            ),
            "signals": signals,
            "data_snapshot": {
                "monthly_income": round(monthly_income, 2),
                "monthly_expense": round(monthly_expense, 2),
                "savings_ratio": round(savings_ratio, 3),
            },
        }

    def _neutral(self, reason: str, user_id: int) -> Dict[str, Any]:
        return {
            "agent": "CashflowAgent",
            "sub_score": 50.0,
            "weight": 0.25,
            "confidence": 0.3,
            "explanation": reason,
            "signals": [],
            "data_snapshot": None,
        }
