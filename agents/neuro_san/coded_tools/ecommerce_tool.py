"""EcommerceTool — Neuro SAN CodedTool for purchase behaviour analysis."""
from typing import Any, Dict
from agents.neuro_san.coded_tools.base_tool import CreditBridgeCodedTool
from agents.tools.mock_data_loader import load_ecommerce


class EcommerceTool(CreditBridgeCodedTool):
    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = self._get_user_id(args, sly_data)
        df = load_ecommerce(user_id)

        if df.empty:
            return {"agent": "EcommerceAgent", "sub_score": 50.0, "weight": 0.15,
                    "confidence": 0.3, "explanation": "No e-commerce data.", "signals": [], "data_snapshot": None}

        total_orders = len(df)
        total_spend = df["amount"].sum() if "amount" in df.columns else 0
        return_rate = float(df["returned"].mean()) if "returned" in df.columns else 0.0
        emi_usage = float(df["paid_emi"].mean()) if "paid_emi" in df.columns else 0.0

        raw_score = self._clamp(min(40, total_orders * 2) - return_rate * 30 + emi_usage * 20 + 40)

        signals = ["purchase_activity"]
        if return_rate < 0.05:
            signals.append("low_return_rate")
        if emi_usage > 0.3:
            signals.append("emi_credit_usage")
        if total_orders > 20:
            signals.append("high_activity")

        return {
            "agent": "EcommerceAgent",
            "sub_score": round(raw_score, 2),
            "weight": 0.15,
            "confidence": round(min(0.9, 0.4 + total_orders / 50), 3),
            "explanation": f"{total_orders} orders, ₹{total_spend:,.0f} spend, {return_rate*100:.0f}% returns, {emi_usage*100:.0f}% EMI.",
            "signals": signals,
            "data_snapshot": {"total_orders": total_orders, "return_rate": round(return_rate, 3)},
        }
