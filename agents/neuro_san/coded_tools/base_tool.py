"""Base class for CreditBridge Neuro SAN CodedTools."""
from typing import Any, Dict


class CreditBridgeCodedTool:
    """
    Simplified CodedTool base compatible with neuro-san's CodedTool interface.
    Each subclass implements invoke(args, sly_data) -> Dict.
    
    Neuro SAN calls invoke() with:
      args:     dict of arguments the LLM agent passed to this tool
      sly_data: shared private data channel (user_id, run_id, etc.)
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.invoke(args, sly_data)

    def _get_user_id(self, args: Dict, sly_data: Dict) -> int:
        """Extract user_id from args or sly_data."""
        uid = args.get("user_id") or sly_data.get("user_id")
        if uid is None:
            raise ValueError("user_id is required but not provided in args or sly_data")
        return int(uid)

    def _clamp(self, val: float, lo: float = 0.0, hi: float = 100.0) -> float:
        return max(lo, min(hi, val))
