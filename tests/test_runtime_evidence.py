import importlib.util
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runtime_runner', ROOT / 'scripts/run_runtime_revision.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RuntimeEvidenceTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
