import sys, unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import promptaria_context_router as router
import promptaria_contextual_executor as contextual

class ContextRouterTests(unittest.TestCase):
 def test_customized_request_selects_multiple_tasks_cumulatively(self):
  result=router.analyze("Adicione uma préconfiguração de automação funcional ao repositório Promptária para correferência automática por título e análise contextual do protocolo-mestre.")
  tasks={item["task"] for item in result["task_candidates"]}
  self.assertIn("repository_update",tasks)
  self.assertIn("future_preconfiguration",tasks)
  self.assertIn("functional_correference",tasks)
  self.assertIn("master_protocol_activation",tasks)
  self.assertEqual(result["selected_instrument_ids"][:3],router.BASE_IDS)
  self.assertFalse(result["external_side_effects_authorized"])
 def test_registry_matching_requires_complete_title_or_registered_alias(self):
  registry={"instruments":[
   {"id":"alpha","title":"Arquitetura Unificada de Execução Segura","path":"instruments/alpha.md","aliases":["execução segura"],"activation":{"enabled":True}},
   {"id":"beta","title":"Arquitetura Unificada de Execução Semântica","path":"instruments/beta.md","aliases":["execução semântica"],"activation":{"enabled":True}}
  ]}
  exact=router.registry_matches("Aplicar execução segura agora.",registry)
  self.assertEqual([item["instrument_id"] for item in exact],["alpha"])
  partial=router.registry_matches("Arquitetura unificada",registry)
  embedded=router.registry_matches("xexecução segurax",registry)
  self.assertEqual(partial,[])
  self.assertEqual(embedded,[])
 def test_longer_canonical_title_shadows_embedded_short_title(self):
  registry={"instruments":[
   {"id":"alpha","title":"Arquitetura Unificada","path":"instruments/alpha.md","aliases":[],"activation":{"enabled":True}},
   {"id":"beta","title":"Arquitetura Unificada de Execução Semântica","path":"instruments/beta.md","aliases":[],"activation":{"enabled":True}}
  ]}
  self.assertEqual([item["instrument_id"] for item in router.registry_matches("Arquitetura Unificada de Execução Semântica",registry)],["beta"])
  both=router.registry_matches("Arquitetura Unificada; Arquitetura Unificada de Execução Semântica",registry)
  self.assertEqual({item["instrument_id"] for item in both},{"alpha","beta"})

 def test_registry_matching_fails_closed_on_duplicate_aliases_but_accepts_explicit_id(self):
  registry={"instruments":[
   {"id":"alpha","title":"Instrumento Alfa","path":"instruments/alpha.md","aliases":["execução segura"],"activation":{"enabled":True}},
   {"id":"beta","title":"Instrumento Beta","path":"instruments/beta.md","aliases":["execução segura"],"activation":{"enabled":True}}
  ]}
  self.assertEqual(router.registry_matches("executar execução segura",registry),[])
  explicit=router.registry_matches("executar execução segura alpha",registry)
  self.assertEqual([item["instrument_id"] for item in explicit],["alpha"])
  embedded_id=router.registry_matches("executar execução segura alphabet",registry)
  self.assertEqual(embedded_id,[])
 def test_registry_matching_does_not_select_inactive_instruments(self):
  registry={"instruments":[
   {"id":"inactive","title":"Instrumento Desativado","path":"instruments/inactive.md","aliases":["desativado"],"activation":{"enabled":False}}
  ]}
  self.assertEqual(router.registry_matches("Instrumento Desativado",registry),[])
 def test_structured_context_preserves_field_paths_and_values(self):
  result=router.analyze({"operation":"update","demand":"Pré-configurar demandas futuras","custom_field":{"destination":"artifacts/report.json","flag":True}})
  fields={(item["path"],item["value"]) for item in result["context_fields"]}
  self.assertIn(("custom_field.destination","artifacts/report.json"),fields)
  self.assertIn(("custom_field.flag","True"),fields)
  self.assertTrue(result["request_context_preserved"])
 def test_contextual_executor_never_implicitly_runs_inactive_instruments(self):
  result=contextual.execute({"request":"Adicione uma préconfiguração de automação ao repositório Promptária."})
  selected=set(result["selected_instrument_ids"])
  self.assertIn("github-operational",selected)
  self.assertTrue(selected)
  self.assertNotIn("future-demand-preconfiguration",selected)
  self.assertNotIn("master-execution",selected)
  self.assertIn("future-demand-preconfiguration",result["routing_evidence"]["blocked_inactive_instrument_ids"])
  self.assertIn("master-execution",result["routing_evidence"]["blocked_inactive_instrument_ids"])
  self.assertTrue(result["contextual_analysis"]["evidence_chain"])
  self.assertFalse(result["external_side_effects_performed"])

 def test_preflight_activation_flag_cannot_bypass_ambiguous_identity(self):
  empty_context = {
   "selected_instrument_ids": [],
   "task_candidates": [],
   "evidence_chain": [],
  }
  with patch.object(contextual.router, "analyze", return_value=empty_context):
   with self.assertRaisesRegex(SystemExit, "Correspondência ambígua bloqueada|Título ambíguo"):
    contextual.execute(
     {"request": "Uma demanda simples."},
     preflight={"matched_instruments": [
      {"id": "github-operational", "identity_status": "ambiguous_title_collision", "activation": True}
     ]},
    )

 def test_contextual_ranking_cannot_resolve_ambiguous_preflight_identity(self):
  contextual_match = {
   "selected_instrument_ids": ["github-operational"],
   "task_candidates": [],
   "evidence_chain": [{"source": "contextual-ranking", "instrument_id": "github-operational"}],
  }
  with patch.object(contextual.router, "analyze", return_value=contextual_match):
   with self.assertRaisesRegex(SystemExit, "Correspondência ambígua bloqueada"):
    contextual.execute(
     {"request": "Uma demanda simples."},
     preflight={"matched_instruments": [
      {"id": "github-operational", "identity_status": "ambiguous_title_collision", "activation": True}
     ]},
    )

 def test_contextual_preflight_cannot_activate_inactive_instrument(self):
  result=contextual.execute(
   {"request":"Uma demanda simples.","instrument_ids":["github-operational"]},
   preflight={"matched_instruments":[
    {"id":"master-execution","identity_status":"resolved","activation":True}
   ]},
  )
  self.assertNotIn("master-execution",result["selected_instrument_ids"])
  self.assertIn("master-execution",result["routing_evidence"]["blocked_inactive_instrument_ids"])

 def test_explicit_instrument_id_cannot_bypass_registry_activation(self):
  result=contextual.execute({
   "request":"Uma demanda simples.",
   "instrument_ids":["github-operational","master-execution"],
  })
  self.assertIn("github-operational",result["selected_instrument_ids"])
  self.assertNotIn("master-execution",result["selected_instrument_ids"])
  self.assertIn("master-execution",result["routing_evidence"]["blocked_inactive_instrument_ids"])

 def test_unknown_explicit_instrument_id_fails_closed(self):
  with self.assertRaisesRegex(SystemExit, "ausentes do registro canônico"):
   contextual.execute({
    "request":"Uma demanda simples.",
    "instrument_ids":["id-que-nao-existe"],
   })

if __name__=="__main__": unittest.main()
