import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nyai_research.rag_benchmark import ARMS, model_payload, render_facts, sources_from_registries, queries_and_cases


class RAGBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.sources=json.loads((ROOT/'experiments/graphrag_144_v1/sources.json').read_text())
        self.cases=json.loads((ROOT/'experiments/graphrag_144_v1/cases.json').read_text())

    def test_source_graph_has_no_candidate_or_label_records(self):
        self.assertEqual(len(self.sources),19)
        facts=[f for s in self.sources for f in s['facts']]
        self.assertEqual(len(facts),48)
        self.assertEqual(len({f['fact_id'] for f in facts}),48)
        forbidden={'candidate_response','design_label','design_expected_execute','reviewed_label'}
        for source in self.sources:
            self.assertFalse(forbidden & set(source))
            for fact in source['facts']:self.assertEqual(set(fact),{'fact_id','text'})

    def test_labels_and_gold_policy_ids_do_not_leak_into_payload_fields(self):
        self.assertEqual(len(self.cases),144)
        for c in self.cases:
            payload=model_payload(c,[])
            self.assertNotIn('design_label',payload)
            self.assertNotIn('target_source_id',payload)
            self.assertNotIn('target_fact_ids',payload)
            self.assertNotEqual(payload['case_key'],c['case_id'])
            if c['domain']=='action_contract':
                self.assertNotIn('policy',payload)

    def test_query_construction_does_not_use_candidate_text_or_labels(self):
        p=[json.loads(x) for x in (ROOT/'data/fixtures/120_synthetic_cases.jsonl').read_text().splitlines()]
        a=[json.loads(x) for x in (ROOT/'data/fixtures/24_agentic_contract_cases.jsonl').read_text().splitlines()]
        original=queries_and_cases(p,a)
        for c in p:c['candidate_response']='changed adversarial answer';c['gold_label']='changed'
        updated=queries_and_cases(p,a)
        self.assertEqual([c['query'] for c in original],[c['query'] for c in updated])

    def test_context_budget_never_splits_a_fact_or_duplicates_it(self):
        f=dict(fact_id='a',source_id='s',text='x'*40)
        self.assertEqual(len(render_facts([f,f])),1)
        self.assertEqual(render_facts([f],max_chars=5),[])


if __name__=='__main__':unittest.main()
