import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import promptaria_cross_segment as interconnection

class CrossSegmentInterconnectionTests(unittest.TestCase):
    def test_links_share_procedure_but_not_identity(self):
        registry={"instruments":[
          {"id":"continuous-a","category":"continuous_automation","path":"a.md","functions":["prepare request"],"operations":["prepare"],"keywords":[],"ui":{"node_id":"instrument:continuous-a"},"activation":{"enabled":True}},
          {"id":"demand-b","category":"recoverable_on_demand","path":"b.md","functions":["prepare request","recover content"],"operations":["recover"],"keywords":[],"ui":{"node_id":"instrument:demand-b"},"activation":{"enabled":True}}]}
        result=interconnection.build_interconnection(registry,["demand-b"],"req-001")
        self.assertEqual(result["summary"]["interconnection_count"],1)
        link=result["links"][0]
        self.assertEqual(link["pair_id"],"cross-segment:continuous-a:demand-b")
        self.assertEqual(link["shared_node_id"],"coordination:cross-segment:continuous-a:demand-b")
        self.assertFalse(link["identity_merge"])
        self.assertEqual(link["instrument_count_delta"],0)
        self.assertEqual(link["phase_status"]["on_demand_recovery"],"selected_for_request")
        self.assertEqual(link["continuous_instrument"]["path"],"a.md")
        self.assertEqual(link["on_demand_instrument"]["path"],"b.md")
    def test_no_link_without_shared_function_operation_or_two_keywords(self):
        registry={"instruments":[
          {"id":"c","category":"continuous_automation","functions":["prepare"],"operations":["prepare"],"keywords":[],"activation":{"enabled":True}},
          {"id":"d","category":"recoverable_on_demand","functions":["render"],"operations":["render"],"keywords":[],"activation":{"enabled":True}}]}
        self.assertEqual(interconnection.build_interconnection(registry)["links"],[])
if __name__=="__main__": unittest.main()
