"""Observed-evidence diagnostic. Host-owned observations are not agent assertions.

Only trusted, built-in fictional programs are executed by the companion runner.
This is not a sandbox for arbitrary code or a tamper-proof attestation system.
"""
import hashlib
import subprocess
import sys
from pathlib import Path


VALID = 'def score(values):\n    return sum(values)\n'
REVISED_VALID = VALID + '# A new artifact version with identical behaviour.\n'
INVALID = 'def score(values):\n    return 0\n'
TESTS = '''import runpy, sys
score = runpy.run_path(sys.argv[1])['score']
assert score([1, 2, 3]) == 6
assert score([-2, 2]) == 0
assert score([]) == 0
print('3 assertions passed')
'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def observe_test(artifact, harness, task, run_id):
    """Run fixed local tests; reject an artifact that changes during execution."""
    before = digest(artifact)
    completed = subprocess.run(
        [sys.executable, '-I', str(harness), str(artifact)],
        capture_output=True, text=True, timeout=5, check=False,
    )
    after = digest(artifact)
    return dict(run_id=run_id, task=task, artifact_sha256=before,
                artifact_stable=before == after, harness_sha256=digest(harness),
                exit_code=completed.returncode, stdout=completed.stdout,
                stderr=completed.stderr)


def observed_contract(state):
    """Explain the actual external gates; never consume the proposed explanation."""
    observation = state['observation'] or {}
    approval = state['approval'] or {}
    checks = {
        'execution_observed': bool(observation),
        'test_passed': observation.get('exit_code') == 0,
        'artifact_stable_during_run': observation.get('artifact_stable') is True,
        'current_artifact_tested': observation.get('artifact_sha256') == state['artifact_sha256'],
        'current_task_tested': observation.get('task') == state['task'],
        'approval_active': approval.get('active') is True,
        'approval_current_artifact': approval.get('artifact_sha256') == state['artifact_sha256'],
        'approval_current_task': approval.get('task') == state['task'],
        'approval_current_execution': bool(observation) and approval.get('run_id') == observation.get('run_id'),
    }
    return dict(permit=all(checks.values()), checks=checks,
                unmet=[key for key, value in checks.items() if not value])


def conventional_revalidation(state):
    """Strong baseline: ordinary execution/version/approval checks, same evidence.

    Intentionally expresses the same policy without NyAI explanation records.
    Equivalent outcomes would demonstrate no incremental decision benefit.
    """
    run, approval = state['observation'], state['approval']
    if not run or not approval or not approval['active']:
        return False
    if run['exit_code'] != 0 or not run['artifact_stable']:
        return False
    current = (state['artifact_sha256'], state['task'])
    return (run['artifact_sha256'], run['task']) == current and (
        approval['artifact_sha256'], approval['task']) == current and approval['run_id'] == run['run_id']
