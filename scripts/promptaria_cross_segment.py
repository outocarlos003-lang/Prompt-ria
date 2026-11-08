#!/usr/bin/env python3
"""Build non-destructive, traceable links between continuous and on-demand instruments."""
from __future__ import annotations
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "cross-segment-interconnection.json"

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).casefold()
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value.replace("-", " ")).strip()

def _values(item: dict, field: str) -> set[str]:
    raw = item.get(field, [])
    if not isinstance(raw, list):
        return set()
    return {normalize(v) for v in raw if isinstance(v, str) and normalize(v)}

def _pair_evidence(left: dict, right: dict, policy: dict):
    functions = sorted(_values(left, "functions") & _values(right, "functions"))
    operations = sorted(_values(left, "operations") & _values(right, "operations"))
    keywords = sorted(_values(left, "keywords") & _values(right, "keywords"))
    qualifies = bool(functions or operations or len(keywords) >= 2)
    if not qualifies:
        return None
    weights = policy["matching"]["weights"]
    return {"shared_functions": functions, "shared_operations": operations,
            "shared_keywords": keywords,
            "evidence_score": weights["function"]*len(functions) +
                              weights["operation"]*len(operations) +
                              weights["keyword"]*len(keywords)}

def build_interconnection(registry: dict, selected_on_demand_ids=None, request_id=None) -> dict:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    items = registry.get("instruments", [])
    continuous = [x for x in items if isinstance(x, dict)
                  and x.get("category") == "continuous_automation"
                  and x.get("activation", {}).get("enabled") is True]
    on_demand = [x for x in items if isinstance(x, dict)
                 and x.get("category") == "recoverable_on_demand"
                 and x.get("activation", {}).get("enabled") is True]
    selected = set(selected_on_demand_ids or [])
    links = []
    for left in continuous:
        for right in on_demand:
            evidence = _pair_evidence(left, right, policy)
            if evidence is None:
                continue
            lid, rid = left["id"], right["id"]
            links.append({
                "pair_id": f"cross-segment:{lid}:{rid}",
                "shared_node_id": f"coordination:cross-segment:{lid}:{rid}",
                "request_id": request_id,
                "continuous_instrument": {"id":lid,"node_id":left.get("ui",{}).get("node_id"),
                    "path":left.get("path"),"title":left.get("title"),
                    "functions_preserved":list(left.get("functions",[]))},
                "on_demand_instrument": {"id":rid,"node_id":right.get("ui",{}).get("node_id"),
                    "path":right.get("path"),"title":right.get("title"),
                    "functions_preserved":list(right.get("functions",[]))},
                "evidence":evidence,
                "relations":[
                    {"from":f"instrument:{lid}","to":f"instrument:{rid}","type":"continuous_to_on_demand"},
                    {"from":f"instrument:{rid}","to":f"instrument:{lid}","type":"on_demand_to_continuous"},
                    {"from":"phase:continuous_preconfiguration","to":"phase:on_demand_recovery","type":"phase_1_precedes_phase_2"},
                    {"from":f"instrument:{lid}","to":f"instrument:{rid}","type":"preserves_independent_identity"}],
                "phase_status":{"continuous_preconfiguration":"context_preconfigured_not_executed",
                    "on_demand_recovery":"selected_for_request" if rid in selected else "candidate_not_selected"},
                "interconnection_status":"interconnected_for_request" if rid in selected else "catalogue_relation_only",
                "identity_merge":False,"instrument_count_delta":0})
    links.sort(key=lambda x:(-x["evidence"]["evidence_score"],x["pair_id"]))
    return {"schema_version":1,"policy_id":policy["id"],"request_id":request_id,
        "phase_order":["continuous_preconfiguration","on_demand_recovery"],
        "independent_instrument_count_preserved":True,"independent_ids_and_paths_preserved":True,
        "independent_functions_preserved":True,"links":links,
        "summary":{"continuous_instrument_count":len(continuous),"on_demand_instrument_count":len(on_demand),
            "interconnection_count":len(links),
            "selected_interconnection_count":sum(x["interconnection_status"]=="interconnected_for_request" for x in links)},
        "side_effects_authorized":False,"matching_activates_instruments":False}
