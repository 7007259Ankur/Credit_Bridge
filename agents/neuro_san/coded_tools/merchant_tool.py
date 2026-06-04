"""MerchantTool — Neuro SAN CodedTool for merchant transaction analysis."""
from typing import Any, Dict
from agents.neuro_san.coded_tools.base_tool import CreditBridgeCodedTool
from agents.tools.mock_data_loader import load_merchant


class MerchantTool(CreditBridgeCodedTool):
    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = self._get_user_id(args, sly_data)
        df = load_merchant(user_id)

        if df.empty:
            return {"agent": "MerchantAgent", "sub_score": 50.0, "weight": 0.10,
                    "confidence": 0.3, "explanation": "No merchant data.", "signals": [], "data_snapshot": None}

        total_txn = len(df)
        dispute_rate = float(df["disputed"].mean()) if "disputed" in df.columns else 0.0
        unique_merchants = df["merchant_name"].nunique() if "merchant_name" in df.columns else 1
        total_amount = df["amount"].sum() if "amount" in df.columns else 0

        raw_score = self._clamp(min(50, total_txn) - dispute_rate * 40 + min(20, unique_merchants * 2) + 30)

        signals = ["merchant_activity"]
        if dispute_rate < 0.02:
            signals.append("low_dispute_rate")
        if unique_merchants > 10:
            signals.append("diverse_merchant_usage")
        if dispute_rate > 0.1:
            signals.append("high_dispute_rate")

        return {
            "agent": "MerchantAgent",
            "sub_score": round(raw_score, 2),
            "weight": 0.10,
            "confidence": round(min(0.85, 0.4 + total_txn / 100), 3),
            "explanation": f"{total_txn} txns across {unique_merchants} merchants, {dispute_rate*100:.1f}% disputed.",
            "signals": signals,
            "data_snapshot": {"total_txn": total_txn, "dispute_rate": round(dispute_rate, 3)},
        }
