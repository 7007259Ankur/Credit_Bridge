"""GeolocationAgent — location stability and residence consistency."""
from agents.base_agent import BaseAgent, AgentResult
from agents.tools.mock_data_loader import load_geolocation


class GeolocationAgent(BaseAgent):
    name = "GeolocationAgent"
    default_weight = 0.10

    def score(self, user_id: int, **kwargs) -> AgentResult:
        df = load_geolocation(user_id)

        if df.empty:
            return AgentResult(
                agent=self.name, sub_score=50, weight=self.weight,
                explanation="No geolocation data available.",
                signals=[], confidence=0.3,
            )

        # Expected columns: timestamp, city, pincode, location_type (home/work/other)
        unique_cities = df["city"].nunique() if "city" in df.columns else 1
        unique_pincodes = df["pincode"].nunique() if "pincode" in df.columns else 1
        months = df["timestamp"].nunique() if "timestamp" in df.columns else 1

        # Stability = fewer unique locations over time
        stability_score = max(0, 80 - (unique_cities - 1) * 10 - (unique_pincodes - 1) * 5)
        raw_score = self._clamp(stability_score + 20)

        signals = ["location_stability"]
        if unique_cities == 1:
            signals.append("single_city_residence")
        if unique_cities > 3:
            signals.append("frequent_relocation")

        explanation = (
            f"Detected {unique_cities} unique cities, {unique_pincodes} pincodes "
            f"over {months} data points."
        )

        return AgentResult(
            agent=self.name,
            sub_score=raw_score,
            weight=self.weight,
            explanation=explanation,
            signals=signals,
            confidence=0.7,
            data_snapshot={"unique_cities": unique_cities, "unique_pincodes": unique_pincodes},
        )
