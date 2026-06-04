"""RiskSynthesizerTool — Neuro SAN CodedTool that aggregates all sub-scores → 300-850."""
from typing import Any, Dict, List
from agents.neuro_san.coded_tools.base_tool import CreditBridgeCodedTool

RECOMMENDATIONS = {
    (300, 579): "High risk. Loan not recommended. Suggest financial counseling.",
    (580, 669): "Fair risk. Small secured loans may be considered with collateral.",
    (670, 739): "Good creditworthiness. Eligible for standard loan products.",
    (740, 799): "Very good. Eligible for competitive interest rates.",
    (800, 850): "Exceptional. Best rates and highest loan limits available.",
}


class RiskSynthesizerTool(CreditBridgeCodedTool):
    """
    Receives all agent_results from sly_data (placed there by the CreditCoordinator)
    and computes the final 300-850 credit score.

    Formula: final_score = 300 + (weighted_avg / 100) * 550
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        # Agent results are collected by the Coordinator into sly_data
        agent_results: List[Dict] = args.get("agent_results") or sly_data.get("agent_results") or []

        if not agent_results:
            return {
                "final_score": 300,
                "recommendation": "Insufficient data — no agent results provided.",
                "weighted_avg": 0,
            }

        total_weight = sum(r.get("weight", 0) for r in agent_results)
        if total_weight == 0:
            return {"final_score": 300, "recommendation": "No weighted scores.", "weighted_avg": 0}

        weighted_sum = sum(r.get("sub_score", 50) * r.get("weight", 0) for r in agent_results)
        weighted_avg = weighted_sum / total_weight

        final_score = max(300, min(850, int(round(300 + (weighted_avg / 100) * 550))))
        recommendation = next(
            (rec for (lo, hi), rec in RECOMMENDATIONS.items() if lo <= final_score <= hi),
            "Score out of range."
        )

        # Write back to sly_data so Coordinator can propagate upstream
        sly_data["final_score"] = final_score
        sly_data["recommendation"] = recommendation

        return {
            "final_score": final_score,
            "weighted_avg": round(weighted_avg, 2),
            "recommendation": recommendation,
        }
