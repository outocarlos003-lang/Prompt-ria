#!/usr/bin/env python3
"""Route Promptária requests by cumulative contextual evidence and canonical instrument identity."""
from __future__ import annotations
import json, re, unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_IDS = ["github-operational", "nocturna-arquitetura-necessidade-identidade-sistemica", "protocol-update-integrity"]
MANIFEST = ROOT / "tests" / "manifest.json"
REGISTRY = ROOT / "config" / "instrument-registry.json"
SEGMENT_POLICY = ROOT / "config" / "segment-integration-policy.json"
RULES = [
 {"task":"repository_update","patterns":[r"\b(?:adicion\w*|implement\w*|atualiz\w*|modific\w*|alter\w*|corrig\w*|integr\w*|crie?\w*|editar|edit\w*|update\w*)\b",r"\b(?:repositorio|arquivo|codigo|workflow|teste|pull request|github|sistema)\b"],"instrument_ids":["master-execution","coordinator"],"description":"A demanda solicita uma mudança operacional em artefatos ou no sistema."},
 {"task":"future_preconfiguration","patterns":[r"\b(?:preconfigur\w*|automatiz\w*|automacao|automatica|automatico|demandas futuras|futuras demandas|future demand)\b"],"instrument_ids":["future-demand-preconfiguration"],"description":"A demanda trata de pré-configuração reutilizável ou de demandas futuras."},
 {"task":"traceability_integrity","patterns":[r"\b(?:rastreabil\w*|rastreio|no(?:s|d)|relac(?:ao|oes)|correspondenc\w*|func(?:ao|oes)|arquivos|destino|origem|evidenc\w*|provenienc\w*|validac\w*)\b"],"instrument_ids":["coordinator","master-execution"],"description":"A demanda exige correspondência entre termos, nós, funções, arquivos, destinos, procedência e evidências."},
 {"task":"functional_correference","patterns":[r"\b(?:correferencia|correferenciar|correspondencia por titulo|titulos dos instrumentos|funcional por titulo|resolucao de referencias)\b"],"instrument_ids":["functional-correference-architecture"],"description":"A demanda requer correspondência funcional ou resolução de referências por título."},
 {"task":"catalog_navigation","patterns":[r"\b(?:catalogo|sitemap|mapa do site|navegacao|manifesto|indice)\b"],"instrument_ids":["catalog-sitemap-preconfiguration"],"description":"A demanda envolve catálogo, manifesto, índice ou navegação."},
 {"task":"master_protocol_activation","patterns":[r"\b(?:protocolo mestre|protocolo master|acionamento mestre|ativar o protocolo|protocolo de execucao)\b"],"instrument_ids":["master-activation"],"description":"A demanda evoca a ativação ou aplicação do protocolo-mestre."},
 {"task":"demand_envelope","patterns":[r"\b(?:schema|schema_version|request_id|demanda estruturada|envelope da demanda|campos estruturados)\b"],"instrument_ids":["github-operational"],"description":"A demanda pede estruturação ou preservação do envelope de solicitação."},
]


def load_segment_policy() -> dict:
 return json.loads(SEGMENT_POLICY.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
 value = unicodedata.normalize("NFKD", value)
 value = "".join(c for c in value if not unicodedata.combining(c)).casefold()
 value = re.sub(r"[\u200b-\u200f\ufeff]", "", value)
 return re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE).replace("-", " ").strip()


def tokens(value: str) -> set[str]:
 return {token for token in normalize(value).split() if len(token) >= 3}


def flatten(value: Any, prefix: str = "") -> list[tuple[str, str]]:
 output = []
 if isinstance(value, dict):
  for key, child in value.items():
   path = (prefix + "." + str(key)) if prefix else str(key)
   output.extend(flatten(child, path))
 elif isinstance(value, list):
  for index, child in enumerate(value):
   output.extend(flatten(child, prefix + "[" + str(index) + "]"))
 elif isinstance(value, (str, int, float, bool)) and value is not None:
  output.append((prefix or "$", str(value)))
 return output


def registry_matches(request_text: str, registry: dict) -> list[dict]:
 normalized_request = normalize(request_text)
 matches = []
 for item in registry.get("instruments", []):
  if item.get("activation", {}).get("enabled") is not True:
   continue
  candidates = [("title", item.get("title", ""))]
  candidates.extend(("alias", value) for value in item.get("aliases", []))
  best = None
  for kind, value in candidates:
   candidate = normalize(value) if isinstance(value, str) else ""
   if not candidate:
    continue
   occurrences = list(re.finditer(r"(?<!\w)" + re.escape(candidate) + r"(?!\w)", normalized_request, flags=re.UNICODE))
   if occurrences:
    score = 1000 + len(candidate)
    if best is None or score > best["score"]:
     best = {
      "kind": kind,
      "matched": value,
      "overlap": sorted(tokens(value)),
      "score": score,
      "match_type": "complete_normalized_title_or_registered_alias",
      "match_spans": [[match.start(), match.end()] for match in occurrences],
     }
  if best:
   matches.append({"instrument_id": item["id"], "title": item["title"], "path": item["path"], "evidence": best})
 safe_matches = []
 for item in matches:
  term = normalize(item["evidence"]["matched"])
  collisions = [
   other for other in matches
   if other["instrument_id"] != item["instrument_id"]
   and normalize(other["evidence"]["matched"]) == term
  ]
  explicit = any(re.search(r"(?<![\w-])" + re.escape(value) + r"(?![\w-])", request_text, flags=re.IGNORECASE | re.UNICODE) for value in (item["instrument_id"], item["path"]))
  item_spans = item["evidence"].get("match_spans", [])
  fully_shadowed = bool(item_spans) and all(
   any(
    other["instrument_id"] != item["instrument_id"]
    and len(normalize(other["evidence"]["matched"])) > len(term)
    and any(
     other_span[0] <= span[0] and other_span[1] >= span[1]
     and (other_span[0], other_span[1]) != (span[0], span[1])
     for other_span in other["evidence"].get("match_spans", [])
    )
    for other in matches
   )
   for span in item_spans
  )
  if (not collisions or explicit) and (not fully_shadowed or explicit):
   safe_matches.append(item)

 safe_matches.sort(key=lambda item: (-item["evidence"]["score"], item["instrument_id"]))
 return safe_matches


def resolve_segment_exceptions(request: Any, registry: dict) -> tuple[list[str], list[dict]]:
 """Resolve only explicit or need-justified requests to add instruments to protected segments."""
 if not isinstance(request, dict):
  return [], []
 entries = []
 for field, basis in (("segment_integration_request", "explicit_user_request"), ("segment_integration_need", "specific_need")):
  raw = request.get(field, [])
  if isinstance(raw, (str, dict)):
   raw = [raw]
  if not isinstance(raw, list):
   continue
  for value in raw:
   if isinstance(value, str) and value.strip():
    entries.append((value, "", basis))
   elif isinstance(value, dict):
    reference = value.get("instrument") or value.get("instrument_id") or value.get("title") or value.get("path")
    reason = value.get("reason", "")
    if isinstance(reference, str) and reference.strip():
     entries.append((reference, reason if isinstance(reason, str) else "", basis))
 resolved, evidence = [], []
 for reference, reason, basis in entries:
  ref = normalize(reference)
  if basis == "specific_need" and not normalize(reason):
   continue
  candidates = []
  for item in registry.get("instruments", []):
   values = [item.get("id", ""), item.get("path", ""), item.get("title", ""), *item.get("aliases", [])]
   if any(isinstance(value, str) and normalize(value) == ref for value in values):
    candidates.append(item)
  if len(candidates) != 1:
   continue
  item = candidates[0]
  resolved.append(item["id"])
  evidence.append({"instrument_id": item["id"], "reference": reference, "reason": reason, "basis": basis})
 return list(dict.fromkeys(resolved)), evidence


def analyze(request: Any, manifest: dict | None = None, registry: dict | None = None) -> dict:
 if manifest is None:
  manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
 if registry is None:
  registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
 policy = load_segment_policy()
 default_integrated = list(policy["default_integrated_instrument_ids"])
 enabled_ids = {
  item.get("id") for item in registry.get("instruments", [])
  if isinstance(item, dict) and isinstance(item.get("id"), str)
  and item.get("activation", {}).get("enabled") is True
 }
 fields = flatten(request)
 request_text = "\n".join(path + ": " + value for path, value in fields)
 normalized = normalize(request_text)
 evidence, selected = [], []
 for rule in RULES:
  hits = []
  for pattern in rule["patterns"]:
   match = re.search(pattern, normalized, flags=re.UNICODE)
   if match:
    hits.append({"pattern": pattern, "matched_evidence": match.group(0)})
  if rule["task"] == "repository_update":
   action_hit = any(re.search(rule["patterns"][0], normalize(value)) for _, value in fields)
   target_hit = any(re.search(rule["patterns"][1], normalize(value)) for _, value in fields)
   if not (action_hit and target_hit):
    continue
  if hits:
   configured_ids = list(rule["instrument_ids"])
   enabled_rule_ids = [item_id for item_id in configured_ids if item_id in enabled_ids]
   blocked_inactive_ids = [item_id for item_id in configured_ids if item_id not in enabled_ids]
   evidence.append({
    "task":rule["task"],
    "description":rule["description"],
    "evidence":hits,
    "selected_instrument_ids":enabled_rule_ids,
    "blocked_inactive_instrument_ids":blocked_inactive_ids,
    "status":"contextual_candidate" if enabled_rule_ids else "blocked_inactive_registry"
   })
   selected.extend(enabled_rule_ids)

 for match in registry_matches(request_text, registry):
  selected.append(match["instrument_id"])
  evidence.append({
   "task":"canonical_instrument_match",
   "description":"Título canônico ou alias explícito de um instrumento habilitado corresponde à demanda.",
   "evidence":[match["evidence"]],
   "selected_instrument_ids":[match["instrument_id"]],
   "status":"registry_match"
  })

 exception_ids, exception_evidence = resolve_segment_exceptions(request, registry)
 additional_integrated = [item_id for item_id in exception_ids if item_id not in default_integrated]
 catalog_ids = {item.get("id") for item in manifest.get("instruments", []) if isinstance(item, dict)}
 if evidence:
  selected = [item_id for item_id in BASE_IDS if item_id in enabled_ids] + selected
 selected = list(dict.fromkeys(selected))
 unknown = [item_id for item_id in selected if item_id not in catalog_ids]
 if unknown:
  raise ValueError("Context router references IDs absent from canonical manifest: " + ", ".join(unknown))

 segment_integration_ids = list(dict.fromkeys(default_integrated + additional_integrated))
 blocked_automatic = [
  item_id for item_id in selected
  if item_id not in segment_integration_ids
 ]
 return {
  "schema_version":3,"analysis_mode":"cumulative_contextual_evidence_plus_canonical_registry","request_context_preserved":True,
  "context_fields":[{"path":path,"value":value} for path,value in fields],
  "base_instrument_ids":default_integrated,"task_candidates":evidence,"selected_instrument_ids":selected,
  "segment_integration":{
   "mode":policy["integration_policy"]["mode"],
   "protected_segments":policy["protected_segments"],
   "default_integrated_instrument_ids":default_integrated,
   "additional_integrated_instrument_ids":additional_integrated,
   "integration_instrument_ids":segment_integration_ids,
   "integration_evidence":exception_evidence,
   "blocked_automatic_integrations":blocked_automatic,
   "activation_remains_independent":True,
   "selection_is_not_integration":True
  },
  "selection_policy":"union of evidence-supported task rules and exact normalized canonical-title or registered-alias matches; any enabled instrument may be activated for its own registered function, while protected-segment integration is closed by default",
  "integration_policy":"Only github-operational and functional-correference-architecture are integrated automatically into the three protected segments. Other instruments remain independently activatable and are integrated into those segments only when segment_integration_need contains an instrument reference plus a reason, or segment_integration_request explicitly names the instrument.",
  "evidence_chain":[
   {"stage":"protected_segment_base","basis":"config/segment-integration-policy.json","instrument_ids":default_integrated},
   {"stage":"request_customization","basis":"complete request and structured-field values with their source paths","field_count":len(fields)},
   {"stage":"contextual_interpretation","basis":"all matching task rules retained cumulatively","task_count":len(evidence)},
   {"stage":"canonical_identity","basis":"instrument-registry.json title, aliases and keywords","registry_match_count":sum(1 for item in evidence if item["task"] == "canonical_instrument_match")},
   {"stage":"handler_selection","basis":"union of contextual and canonical registry handlers","instrument_ids":selected},
   {"stage":"segment_integration_gate","basis":"closed-by-default policy; only explicit request or reasoned specific need can add an instrument","integrated_instrument_ids":segment_integration_ids},
   {"stage":"traceability_contract","basis":"canonical instrument metadata connects identity, function, files, operations and interface node","enabled":True}],
  "unresolved_context":[] if evidence else ["No specialized task rule or canonical registry match had sufficient evidence; no additional protected-segment integration is inferred."],
  "external_side_effects_authorized":False}


def main() -> None:
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--request",required=True,type=Path)
 parser.add_argument("--output",required=True,type=Path)
 args=parser.parse_args()
 payload=json.loads(args.request.read_text(encoding="utf-8"))
 result=analyze(payload)
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":"context_analyzed","task_candidates":[x["task"] for x in result["task_candidates"]],"selected_instrument_ids":result["selected_instrument_ids"],"segment_integration":result["segment_integration"]},ensure_ascii=False))
if __name__=="__main__": main()
