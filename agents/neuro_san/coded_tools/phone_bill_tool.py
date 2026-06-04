"""PhoneBillTool — Neuro SAN CodedTool for telecom payment analysis."""
from typing import Any, Dict
from agents.neuro_san.coded_tools.base_tool import CreditBridgeCodedTool
from agents.tools.mock_data_loader import load_phone_bills


class PhoneBillTool(CreditBridgeCodedTool):
    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = self._get_user_id(args, sly_data)
        df = load_phone_bills(user_id)

        if df.empty:
            return {"agent": "PhoneBillAgent", "sub_score": 50.0, "weight": 0.15,
                    "confidence": 0.3, "explanation": "No phone bill data.", "signals": [], "data_snapshot": None}

        total = len(df)
        on_time = int(df["paid_on_time"].sum()) if "paid_on_time" in df.columns else total
        avg_days_late = df["days_late"].mean() if "days_late" in df.columns else 0

        on_time_ratio = on_time / total
        raw_score = self._clamp(on_time_ratio * 80 + max(0, 20 - avg_days_late * 2))

        signals = ["payment_consistency", "bill_regularity"]
        if on_time_ratio == 1.0:
            signals.append("perfect_payment_record")
        if avg_days_late > 10:
            signals.append("frequent_late_payments")

        return {
            "agent": "PhoneBillAgent",
            "sub_score": round(raw_score, 2),
            "weight": 0.15,
            "confidence": round(min(0.95, 0.5 + total / 24), 3),
            "explanation": f"{on_time} of {total} months paid on time ({on_time_ratio*100:.0f}%), avg {avg_days_late:.1f} days late.",
            "signals": signals,
            "data_snapshot": {"total_months": total, "on_time": on_time},
        }
