"""GeolocationTool — Neuro SAN CodedTool for location stability analysis."""
from typing import Any, Dict
from agents.neuro_san.coded_tools.base_tool import CreditBridgeCodedTool
from agents.tools.mock_data_loader import load_geolocation


class GeolocationTool(CreditBridgeCodedTool):
    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = self._get_user_id(args, sly_data)
        df = load_geolocation(user_id)

        if df.empty:
            return {"agent": "GeolocationAgent", "sub_score": 50.0, "weight": 0.10,
                    "confidence": 0.3, "explanation": "No geolocation data.", "signals": [], "data_snapshot": None}

        unique_cities = df["city"].nunique() if "city" in df.columns else 1
        unique_pincodes = df["pincode"].nunique() if "pincode" in df.columns else 1
        months = len(df)

        stability_score = max(0, 80 - (unique_cities - 1) * 10 - (unique_pincodes - 1) * 5)
        raw_score = self._clamp(stability_score + 20)

        signals = ["location_stability"]
        if unique_cities == 1:
            signals.append("single_city_residence")
        if unique_cities > 3:
            signals.append("frequent_relocation")

        return {
            "agent": "GeolocationAgent",
            "sub_score": round(raw_score, 2),
            "weight": 0.10,
            "confidence": 0.70,
            "explanation": f"Detected {unique_cities} cities, {unique_pincodes} pincodes over {months} data points.",
            "signals": signals,
            "data_snapshot": {"unique_cities": unique_cities, "unique_pincodes": unique_pincodes},
        }
