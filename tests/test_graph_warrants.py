import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from nyai_research.graph_warrants import audit_retrieval


class RetrievalWarrantTests(unittest.TestCase):
    def setUp(self):
        self.passages = [dict(id='chunk_1', slug='note_a', heading='Evidence', text='Fictional passage.')]
        self.expansion = [dict(slug='note_a', sources=['fictional_source.md'])]

    def test_provenance_does_not_establish_entailment(self):
        r = audit_retrieval(self.passages, self.expansion, ['P1'])
        self.assertEqual(r['trace_status'], 'inspectable')
        self.assertFalse(r['validated_answer_permitted'])
        self.assertEqual(next(c['status'] for c in r['checks'] if c['rule_id'] == 'entailment'), 'unknown')

    def test_fabricated_citation_invalidates_trace(self):
        r = audit_retrieval(self.passages, self.expansion, ['P99'])
        self.assertEqual(r['trace_status'], 'invalid')

    def test_duplicate_chunk_cannot_look_like_distinct_evidence(self):
        r = audit_retrieval(self.passages * 2, self.expansion, ['P1', 'P2'])
        self.assertEqual(r['trace_status'], 'invalid')

    def test_unprovided_expansion_is_unknown_not_a_claim_that_sources_do_not_exist(self):
        r = audit_retrieval(self.passages, [], ['P1'])
        self.assertEqual(next(c['status'] for c in r['checks'] if c['rule_id'] == 'source_lineage'), 'unknown')

    def test_empty_retrieval_cannot_validate_answer(self):
        r = audit_retrieval([], [], ['P1'])
        self.assertEqual(r['trace_status'], 'invalid')
        self.assertFalse(r['validated_answer_permitted'])
