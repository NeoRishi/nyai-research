"""Offline regression tests for hybrid gating, evidence scope and accounting."""
import copy
import unittest
from unittest.mock import patch

from scripts import run_assurance_dag_model_monitor as monitor


class HybridMonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Stage-1 construction must never consult the deterministic semantic detector.
        with patch('nyai_research.assurance_dag.inspect_semantic_slice_ast',
                   side_effect=AssertionError('Stage-2 AST labels leaked into gating')):
            cls.decisions, cls.tasks, cls.references = monitor.build_evaluation()

    def test_only_stage1_passes_construct_api_requests(self):
        rejected = {d['case_id'][:3] for d in self.decisions if not d['stage1']['permit']}
        self.assertEqual(rejected, {f'T{i:02d}' for i in range(1, 11)})
        self.assertEqual({t['case_id'][:3] for t in self.tasks}, {f'T{i:02d}' for i in range(11, 17)})
        self.assertEqual(len(self.tasks), 6)
        for task in self.tasks:
            text = task['request_body']['input']
            self.assertNotIn(task['case_id'], text)
            for forbidden in ('expected_permit', 'design_rationale', 'has_semantic_hack_in_window',
                              'intervention', 'regime', 'stage2_semantic_hack'):
                self.assertNotIn(forbidden, text)

    def test_workspace_observations_and_logs_are_all_pruned(self):
        by_case = {d['case_id']: d for d in self.decisions}
        for ref in self.references:
            ancestors = by_case[ref['case_id']]['stage1']['causal_slice']
            full, sliced = ref['full_workspace'], ref['causal_slice']
            expected_files = set(ancestors['active_artifact_names']) & set(full['workspace'])
            self.assertEqual(set(sliced['workspace']), expected_files)
            self.assertLess(set(sliced['workspace']), set(full['workspace']))
            expected_ids = set(ancestors['active_step_ids'])
            self.assertEqual(sliced['observations'], [o for o in full['observations']
                                                     if o['step_id'] in expected_ids])
            self.assertEqual(sliced['transcript'], [s for s in full['transcript']
                                                   if s['step_id'] in expected_ids])
            for name in sliced['workspace']:
                self.assertEqual(sliced['workspace'][name], full['workspace'][name])
            if ref['case_id'].startswith('T14'):
                self.assertIn('dead_branch_experiment.py', full['workspace'])
                self.assertNotIn('dead_branch_experiment.py', sliced['workspace'])
                self.assertTrue(any(o['exit_code'] != 0 for o in full['observations']))
                self.assertTrue(all(o['exit_code'] == 0 for o in sliced['observations']))

    def test_end_to_end_gating_and_model_error_accounting(self):
        calls = []
        for task in self.tasks:
            permit = int(task['case_id'][1:3]) >= 13
            calls.append(dict(task, parsed={'permit': permit, 'reason': 'Mock semantic verdict',
                                            'flagged_steps': []},
                              response={'model': 'mock', 'usage': {'input_tokens': 100, 'output_tokens': 10}}))
        summary, final = monitor.aggregate(self.decisions, calls)
        hybrid = summary['arms'][monitor.HYBRID]
        self.assertEqual(summary['status'], 'COMPLETE')
        self.assertEqual(hybrid['design_agreement'], 16)
        self.assertEqual((hybrid['stage1_withholds'], hybrid['stage2_eligible'], hybrid['llm_calls']), (10, 6, 6))
        self.assertEqual(hybrid['input_tokens'], 600)
        self.assertTrue(all(not r['llm_called'] and r['permit'] is False
                            for r in final if not r['stage1']['permit']))
        prior = summary['arms']['standalone_full_unpruned_transcript']
        self.assertEqual((prior['design_agreement'], prior['input_tokens']), (13, 61494))
        incomplete, _ = monitor.aggregate(self.decisions, calls[:-1])
        self.assertEqual(incomplete['status'], 'INCOMPLETE')
        self.assertEqual(incomplete['arms'][monitor.HYBRID]['errors_or_invalid'], 1)

    def test_replay_rejects_duplicate_or_altered_requests(self):
        row = dict(self.tasks[0], parsed={'permit': False})
        with self.assertRaises(ValueError):
            monitor.checked_records([row, row], self.tasks)
        altered = copy.deepcopy(row)
        altered['request_body']['input'] = '{}'
        with self.assertRaises(ValueError):
            monitor.checked_records([altered], self.tasks)
        self.assertFalse(monitor.checked_records([row], self.tasks))


if __name__ == '__main__':
    unittest.main()
