import importlib.util
import contextlib
import io
import tempfile
import unittest
import copy
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runtime_runner', ROOT / 'scripts/run_runtime_revision.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
from nyai_research.runtime_evidence import (
    VALID, TESTS, digest, observe_test, observed_contract, conventional_revalidation,
)


class RuntimeEvidenceTests(unittest.TestCase):
    def make_state(self, folder):
        artifact, harness = Path(folder) / 'candidate.py', Path(folder) / 'checks.py'
        artifact.write_text(VALID)
        harness.write_text(TESTS)
        run = observe_test(artifact, harness, 'sum-values-v1', 1)
        state = dict(artifact_sha256=digest(artifact), harness_sha256=digest(harness),
                     task='sum-values-v1', observation=run,
                     approval=dict(active=True, artifact_sha256=digest(artifact),
                                   task='sum-values-v1', run_id=1))
        return state, artifact, harness

    def test_real_execution_revision_and_strong_baseline(self):
        with tempfile.TemporaryDirectory() as output, contextlib.redirect_stdout(io.StringIO()):
            records, summary = runner.run(Path(output))
        final = {r['case_id']: r for r in records if r['phase'] == 'final'}
        # Integration assertions target the observed failure/correction and lost authority,
        # not merely agreement between two policy implementations.
        self.assertNotEqual(final['fabricated_passing_claim']['state']['observation']['exit_code'], 0)
        self.assertFalse(final['fabricated_passing_claim']['contract']['permit'])
        self.assertEqual(final['failure_corrected']['state']['observation']['exit_code'], 0)
        self.assertTrue(final['failure_corrected']['contract']['permit'])
        self.assertIn('approval_current_execution', final['retest_without_reapproval']['contract']['unmet'])
        self.assertIn('current_artifact_tested', final['mutation_after_approval']['contract']['unmet'])
        self.assertIn('approval_active', final['approval_revoked']['contract']['unmet'])
        self.assertEqual(summary['arms']['nyai_observed_contract']['unwarranted_permits'], 0)
        self.assertEqual(summary['arms']['nyai_observed_contract'], summary['arms']['conventional_revalidation'])
        self.assertEqual(summary['arms']['synthetic_self_report']['unwarranted_permits'], 8)

    def test_malformed_runtime_records_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            original, _, _ = self.make_state(folder)
            self.assertTrue(observed_contract(original)['permit'])
            for bad in (None, [], {}, {'observation': []}):
                self.assertFalse(observed_contract(bad)['permit'])
                self.assertFalse(conventional_revalidation(bad))
            for key in original:
                state = copy.deepcopy(original)
                del state[key]
                with self.subTest(missing=key):
                    self.assertFalse(observed_contract(state)['permit'])
                    self.assertFalse(conventional_revalidation(state))
            for invalid_id in (None, '', ' ', 0, False, [], 1.0):
                state = copy.deepcopy(original)
                state['observation']['run_id'] = invalid_id
                state['approval']['run_id'] = invalid_id
                with self.subTest(run_id=invalid_id):
                    self.assertFalse(observed_contract(state)['permit'])
                    self.assertFalse(conventional_revalidation(state))
            state = copy.deepcopy(original)
            state['observation']['exit_code'] = False
            del state['observation']['run_id']
            del state['approval']['run_id']
            self.assertFalse(observed_contract(state)['permit'])
            self.assertFalse(conventional_revalidation(state))

    def test_changed_empty_harness_does_not_satisfy_expected_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            state, artifact, harness = self.make_state(folder)
            harness.write_text('')
            state['observation'] = observe_test(artifact, harness, state['task'], 2)
            state['approval']['run_id'] = 2
            self.assertEqual(state['observation']['exit_code'], 0)
            self.assertIn('expected_harness_used', observed_contract(state)['unmet'])
            self.assertFalse(conventional_revalidation(state))

    def test_timeout_and_launch_failure_become_withheld_observations(self):
        with tempfile.TemporaryDirectory() as folder:
            state, artifact, harness = self.make_state(folder)
            harness.write_text('import time\ntime.sleep(1)\n')
            state['harness_sha256'] = digest(harness)
            state['observation'] = observe_test(artifact, harness, state['task'], 1, timeout=0.02)
            self.assertEqual(state['observation']['error'], 'timeout')
            self.assertIsNone(state['observation']['exit_code'])
            self.assertFalse(observed_contract(state)['permit'])
            self.assertFalse(conventional_revalidation(state))
            with patch('nyai_research.runtime_evidence.subprocess.run', side_effect=OSError('unavailable')):
                state['observation'] = observe_test(artifact, harness, state['task'], 1)
            self.assertIn('launch_error', state['observation']['error'])
            self.assertFalse(observed_contract(state)['permit'])

    def test_harness_mutation_during_execution_is_recorded(self):
        with tempfile.TemporaryDirectory() as folder:
            state, artifact, harness = self.make_state(folder)
            def mutate(*args, **kwargs):
                harness.write_text('')
                from subprocess import CompletedProcess
                return CompletedProcess(args[0], 0, 'claimed pass', '')
            with patch('nyai_research.runtime_evidence.subprocess.run', side_effect=mutate):
                state['observation'] = observe_test(artifact, harness, state['task'], 1)
            self.assertFalse(state['observation']['harness_stable'])
            self.assertFalse(observed_contract(state)['permit'])
            self.assertFalse(conventional_revalidation(state))


if __name__ == '__main__':
    unittest.main()
