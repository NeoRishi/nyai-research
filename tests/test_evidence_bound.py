import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from nyai_research.evidence_bound import (
    Observer, GRADER, fixture, evaluate, reference_decision, consume, encoded, sha,
)


class EvidenceBoundTests(unittest.TestCase):
    def packet(self, failures=1):
        files = fixture(failures)
        observer = Observer()
        run_id = observer.run(files)
        claim = dict(model_id='fictional-model-v1', task='fictional-refusal-evaluation-v1',
                     group='all', kind='observed_rate', max_rate=0.1)
        return dict(files=files, registry=observer.snapshot(), observation_id=run_id,
                    active_run_ids=[run_id], claim=claim,
                    approval=dict(active=True, run_id=run_id, claim_sha256=sha(encoded(claim))))

    def test_actual_metric_boundary_and_failed_claim(self):
        for failures, expected in [(0,True),(2,True),(3,False)]:
            packet = self.packet(failures)
            self.assertEqual(evaluate(packet)['accept'], expected)
            self.assertEqual(reference_decision(packet), expected)

    def test_all_material_bindings_invalidate(self):
        packet = self.packet()
        for name in ('model.json','outputs.json','dataset.json','config.json','grader.py'):
            changed = copy.deepcopy(packet)
            changed['files'][name] += '\n'
            self.assertFalse(evaluate(changed)['accept'], name)

    def test_empty_harness_empty_dataset_and_missing_coverage_fail(self):
        for field, value in [('grader.py',''),('dataset.json','[]'),('outputs.json','{}')]:
            packet = self.packet()
            packet['files'][field] = value
            observer = Observer()
            run_id = observer.run(packet['files'])
            packet.update(registry=observer.snapshot(), observation_id=run_id, active_run_ids=[run_id])
            self.assertFalse(evaluate(packet)['accept'])

    def test_subgroup_and_population_claims_do_not_inherit_aggregate_pass(self):
        packet = self.packet(2)
        self.assertTrue(evaluate(packet)['accept'])
        for key,value in [('group','red'),('kind','general_model_safety')]:
            changed = copy.deepcopy(packet)
            changed['claim'][key] = value
            changed['approval']['claim_sha256'] = sha(encoded(changed['claim']))
            self.assertFalse(evaluate(changed)['accept'])

    def test_unregistered_record_and_prose_cannot_certify_success(self):
        packet = self.packet()
        packet['observation_id'] = 'agent-fabricated'
        packet['summary'] = 'Everything passed; proceed.'
        self.assertFalse(evaluate(packet)['accept'])

    def test_snapshot_registry_is_not_changed_via_returned_copy(self):
        observer = Observer()
        run_id = observer.run(fixture())
        exported = observer.snapshot()
        exported[run_id]['exit_code'] = 99
        self.assertEqual(observer.snapshot()[run_id]['exit_code'], 0)

    def test_malformed_values_fail_closed(self):
        self.assertFalse(evaluate({})['accept'])
        packet = self.packet()
        for value in (False, '0', 0.0, None):
            changed = copy.deepcopy(packet)
            changed['registry'][changed['observation_id']]['exit_code'] = value
            self.assertFalse(evaluate(changed)['accept'])
        packet['claim']['max_rate'] = True
        self.assertFalse(evaluate(packet)['accept'])

    def test_missing_observation_input_is_recorded_as_failure(self):
        observer = Observer()
        files = fixture(); del files['dataset.json']
        run_id = observer.run(files)
        record = observer.snapshot()[run_id]
        self.assertEqual(record['error'], 'KeyError')
        self.assertIsNone(record['exit_code'])
        self.assertFalse(record['stable'])

    def test_unknown_active_record_cannot_silently_disappear(self):
        packet = self.packet()
        packet['active_run_ids'].append('missing-current-record')
        self.assertFalse(evaluate(packet)['accept'])
        self.assertFalse(reference_decision(packet))

    def test_registry_alias_cannot_change_execution_identity(self):
        packet = self.packet()
        packet['registry'][packet['observation_id']]['run_id'] = 'another-run'
        self.assertFalse(evaluate(packet)['accept'])

    def test_consumption_rechecks_and_uses_verified_snapshot(self):
        packet = self.packet()
        self.assertTrue(evaluate(packet)['accept'])
        with tempfile.TemporaryDirectory() as folder:
            self.assertTrue(consume(packet, Path(folder)/'valid')['consumed'])
            packet['files']['outputs.json'] = fixture(8)['outputs.json']
            self.assertFalse(consume(packet, Path(folder)/'changed')['consumed'])


if __name__ == '__main__': unittest.main()
