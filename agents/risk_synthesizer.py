"""RiskSynthesizer — aggregates sub-scores into final 300-850 credit score."""
from typing import List, Dict, Any


SCORE_RECOMMENDATIONS = {
    (300, 579): "High risk. Loan not recommended at this time. Suggest financial counseling.",
    (580, 669): "Fair risk. Small secured loans may be considered with collateral.",
    (670, 739): "Good creditworthiness. Eligible for standard loan products.",
    (740, 799): "Very good. Eligible for competitive interest rates.",
    (800, 850): "Exceptional. Best rates and highest loan limits available.",
}


def synthesize(agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Combine agent sub-scores into a final credit score.
    
    Formula: final_score = 300 + (weighted_avg / 100) * 550
    Range: 300 (worst) → 850 (best)
    """
    if not agent_results:
        return {"final_score": 300, "recommendation": "Insufficient data for scoring."}

    # Normalize weights (in case admin config doesn't sum exactly to 1.0)
    total_weight = sum(r["weight"] for r in agent_results)
    if total_weight == 0:
        return {"final_score": 300, "recommendation": "No weighted scores available."}

    weighted_sum = sum(r["sub_score"] * r["weight"] for r in agent_results)
    weighted_avg = weighted_sum / total_weight

    final_score = int(round(300 + (weighted_avg / 100) * 550))
    final_score = max(300, min(850, final_score))

    recommendation = _get_recommendation(final_score)

    return {
        "final_score": final_score,
        "weighted_avg": round(weighted_avg, 2),
        "recommendation": recommendation,
    }


def _get_recommendation(score: int) -> str:
    for (low, high), rec in SCORE_RECOMMENDATIONS.items():
        if low <= score <= high:
            return rec
    return "Score out of range."
