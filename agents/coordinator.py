"""
CreditCoordinator — uses Neuro SAN to orchestrate the multi-agent credit pipeline.

Neuro SAN runs the agent network defined in:
    agents/neuro_san/credit_scoring_network.hocon

The HOCON file declares a CreditCoordinator frontman agent that fans out to
6 specialist agents (each backed by a CodedTool), then calls RiskSynthesizerTool
to compute the final 300-850 score.

Falls back to direct Python execution if Neuro SAN is not installed / Ollama
is unavailable — useful for unit tests and CI.
"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

HOCON_PATH = os.path.join(os.path.dirname(__file__), "neuro_san", "credit_scoring_network.hocon")
WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), "../backend/weights.json")

DEFAULT_WEIGHTS = {
    "cashflow": 0.25,
    "phone_bill": 0.15,
    "ecommerce": 0.15,
    "psychometric": 0.15,
    "merchant": 0.10,
    "geolocation": 0.10,
}


# ── Neuro SAN pipeline ────────────────────────────────────────────────────────

def run_pipeline_neuro_san(user_id: int, run_id: int) -> Dict[str, Any]:
    """
    Run the credit scoring pipeline via Neuro SAN's agent network.
    
    Neuro SAN loads the HOCON network, spins up the CreditCoordinator frontman,
    which fans out to all 6 specialist agents (each calling a CodedTool),
    then aggregates via RiskSynthesizerTool.
    """
    try:
        from neuro_san.client.agent_session import AgentSession
        from neuro_san.internals.run_context import RunContext
    except ImportError:
        raise ImportError("neuro-san is not installed. Run: pip install neuro-san")

    # Boot the agent session from HOCON
    session = AgentSession.from_hocon(
        hocon_path=HOCON_PATH,
        agent_name="CreditCoordinator",
    )

    # sly_data carries user_id and run_id securely — never exposed to the LLM
    sly_data: Dict[str, Any] = {
        "user_id": user_id,
        "run_id": run_id,
        "agent_results": [],  # Coordinator fills this as sub-agents respond
    }

    prompt = (
        f"Please run a complete credit assessment for applicant with user_id={user_id}. "
        f"Call all six scoring agents, collect their results, then call RiskSynthesizerTool "
        f"to produce the final credit score."
    )

    response = session.invoke(prompt=prompt, sly_data=sly_data)

    # Extract results from sly_data (populated by CodedTools via the allow config)
    agent_results = sly_data.get("agent_results") or _extract_agent_results_from_response(response)
    final_score = sly_data.get("final_score") or _extract_final_score(response)
    recommendation = sly_data.get("recommendation") or _extract_recommendation(response)

    return {
        "agent_results": agent_results,
        "final_score": final_score,
        "recommendation": recommendation,
        "errors": [],
        "engine": "neuro_san",
    }


# ── Direct Python fallback (no LLM needed) ────────────────────────────────────

def run_pipeline_direct(user_id: int, run_id: int) -> Dict[str, Any]:
    """
    Fallback: run all CodedTools directly in parallel, skipping the LLM layer.
    Used in tests and when Ollama is unavailable.
    """
    from agents.neuro_san.coded_tools.cashflow_tool import CashflowTool
    from agents.neuro_san.coded_tools.phone_bill_tool import PhoneBillTool
    from agents.neuro_san.coded_tools.ecommerce_tool import EcommerceTool
    from agents.neuro_san.coded_tools.psychometric_tool import PsychometricTool
    from agents.neuro_san.coded_tools.merchant_tool import MerchantTool
    from agents.neuro_san.coded_tools.geolocation_tool import GeolocationTool
    from agents.neuro_san.coded_tools.risk_synthesizer_tool import RiskSynthesizerTool

    weights = _load_weights()
    tools = [
        (CashflowTool(), weights.get("cashflow", 0.25)),
        (PhoneBillTool(), weights.get("phone_bill", 0.15)),
        (EcommerceTool(), weights.get("ecommerce", 0.15)),
        (PsychometricTool(), weights.get("psychometric", 0.15)),
        (MerchantTool(), weights.get("merchant", 0.10)),
        (GeolocationTool(), weights.get("geolocation", 0.10)),
    ]

    sly_data = {"user_id": user_id, "run_id": run_id}
    agent_results = []
    errors = []

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(tool.invoke, {"user_id": user_id}, sly_data): (tool, w)
            for tool, w in tools
        }
        for future in as_completed(futures):
            tool, admin_weight = futures[future]
            try:
                result = future.result(timeout=30)
                # Override weight with admin-configured value
                result["weight"] = admin_weight
                agent_results.append(result)
            except Exception as exc:
                errors.append({"agent": type(tool).__name__, "error": str(exc)})
                agent_results.append({
                    "agent": type(tool).__name__,
                    "sub_score": 50.0,
                    "weight": admin_weight,
                    "confidence": 0.1,
                    "explanation": f"Agent failed: {exc}",
                    "signals": ["agent_error"],
                    "data_snapshot": None,
                })

    # Risk synthesis
    sly_data["agent_results"] = agent_results
    synthesis = RiskSynthesizerTool().invoke({"agent_results": agent_results}, sly_data)

    return {
        "agent_results": agent_results,
        "final_score": synthesis["final_score"],
        "recommendation": synthesis["recommendation"],
        "errors": errors,
        "engine": "direct_fallback",
    }


# ── Public entry point ────────────────────────────────────────────────────────

def run_pipeline(user_id: int, run_id: int, db=None) -> Dict[str, Any]:
    """
    Main entry point called by the Celery scoring task.
    
    Attempts Neuro SAN first (requires Ollama running locally).
    Falls back to direct CodedTool execution if Neuro SAN / Ollama unavailable.
    """
    try:
        result = run_pipeline_neuro_san(user_id, run_id)
        logger.info("Neuro SAN pipeline completed for user=%s run=%s score=%s",
                    user_id, run_id, result.get("final_score"))
        return result
    except Exception as e:
        logger.warning(
            "Neuro SAN pipeline failed (%s), falling back to direct execution.", e
        )
        result = run_pipeline_direct(user_id, run_id)
        logger.info("Direct pipeline completed for user=%s run=%s score=%s",
                    user_id, run_id, result.get("final_score"))
        return result


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_weights() -> Dict[str, float]:
    if os.path.exists(WEIGHTS_FILE):
        with open(WEIGHTS_FILE) as f:
            return json.load(f)
    return DEFAULT_WEIGHTS


def _extract_agent_results_from_response(response: Any) -> List[Dict]:
    """Best-effort extraction of agent results from Neuro SAN response text."""
    try:
        if isinstance(response, dict):
            return response.get("agent_results", [])
        if isinstance(response, str):
            data = json.loads(response)
            return data.get("agent_results", [])
    except Exception:
        pass
    return []


def _extract_final_score(response: Any) -> int:
    try:
        if isinstance(response, dict):
            return int(response.get("final_score", 500))
        if isinstance(response, str):
            data = json.loads(response)
            return int(data.get("final_score", 500))
    except Exception:
        pass
    return 500


def _extract_recommendation(response: Any) -> str:
    try:
        if isinstance(response, dict):
            return response.get("recommendation", "")
        if isinstance(response, str):
            data = json.loads(response)
            return data.get("recommendation", "")
    except Exception:
        pass
    return "Score computed via agent pipeline."
