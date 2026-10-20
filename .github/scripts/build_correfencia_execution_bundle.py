"""Build a traceable execution bundle without performing any instrument actions."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


_PLAN_KEYS = ("activated", "matched_instruments", "execution_plan", "matches")


def _is_active(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    if item.get("function_status") in {"ambiguous", "diverse"}:
        return False
    if item.get("activation_status") == "recognized_ambiguous_not_activated":
        return False
    if "activation" in item:
        return item.get("activation") is True
    # Legacy plans encoded activation through a recognized execution mode.
    return item.get("mode") == "preserve_own_function"


def build(result: dict[str, Any], request_id: str) -> dict[str, Any]:
    """Normalize resolver output while preserving original mentions and metadata."""
    if not isinstance(result, dict):
        raise ValueError("result must be an object")
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("request_id must be a non-empty string")

    source_count = result.get("matched_occurrences")
    if source_count is not None:
        if isinstance(source_count, bool) or not isinstance(source_count, int) or source_count < 0:
            raise ValueError("matched_occurrences must be a non-negative integer")

    source_key = next((key for key in _PLAN_KEYS if isinstance(result.get(key), list)), None)
    source_items = deepcopy(result.get(source_key, [])) if source_key else []
    if not isinstance(source_items, list):
        source_items = []
    active_items = [deepcopy(item) for item in source_items if _is_active(item)]

    bundle = deepcopy(result)
    bundle["schema_version"] = "2.1"
    bundle["request_id"] = request_id
    bundle["source_plan_key"] = source_key
    bundle["instruments"] = active_items
    if source_key == "matched_instruments":
        bundle["matched_instruments"] = deepcopy(source_items)
    if source_key == "activated":
        bundle["activated"] = deepcopy(source_items)
    if source_key == "execution_plan":
        # Keep legacy source plan for traceability; packaged instruments are filtered.
        bundle["execution_plan"] = deepcopy(source_items)
    if "matches" in result:
        bundle["matches"] = deepcopy(result["matches"])
    if "activated" in result and source_key != "activated":
        bundle["activated"] = deepcopy(result["activated"])
    if "matched_instruments" in result and source_key != "matched_instruments":
        bundle["matched_instruments"] = deepcopy(result["matched_instruments"])
    if "matched_occurrences" in result:
        bundle["source_matched_occurrences"] = source_count
        bundle["matched_occurrences"] = source_count
    else:
        bundle["source_matched_occurrences"] = len(source_items)
        bundle["matched_occurrences"] = len(source_items)
    bundle["packaged_instrument_occurrences"] = len(active_items)
    bundle["execution_performed"] = False
    return bundle
