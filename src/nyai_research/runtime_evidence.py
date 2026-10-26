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


def observe_test(artifact, harness, task, run_id, timeout=5):
    """Observe a fixed local test, including failed launches and timeouts.

    Before/after hashes detect some mutations, not swap-and-restore attacks.
    No claim of sandboxing or atomic downstream artifact consumption is made.
    """
    observation = dict(run_id=run_id, task=task, artifact_sha256=None,
                       harness_sha256=None, artifact_stable=False,
                       harness_stable=False, exit_code=None,
                       stdout='', stderr='', error=None)
    try:
        before, harness_before = digest(artifact), digest(harness)
        observation.update(artifact_sha256=before, harness_sha256=harness_before)
        completed = subprocess.run(
            [sys.executable, '-I', str(harness), str(artifact)],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        observation.update(exit_code=completed.returncode, stdout=completed.stdout,
                           stderr=completed.stderr)
    except subprocess.TimeoutExpired as error:
        observation['error'] = 'timeout'
        # TimeoutExpired may return bytes even when subprocess text=True.
        for field in ('stdout', 'stderr'):
            value = getattr(error, field, None) or ''
            observation[field] = value.decode(errors='replace') if isinstance(value, bytes) else value
    except OSError as error:
        observation['error'] = 'observation_or_launch_error:' + type(error).__name__
    finally:
        try:
            observation['artifact_stable'] = observation['artifact_sha256'] == digest(artifact)
            observation['harness_stable'] = observation['harness_sha256'] == digest(harness)
        except OSError:
            observation['error'] = observation['error'] or 'post_run_identity_unavailable'
    return observation


def _nonempty(value):
    return type(value) is str and bool(value.strip())


def _hash(value):
    return _nonempty(value) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _run_id(value):
    return (type(value) is int and value > 0) or _nonempty(value)


def _valid_state(state):
    """Shared strict schema validation, not a second scientific oracle."""
    if type(state) is not dict:
        return False
    run, approval = state.get('observation'), state.get('approval')
    if type(run) is not dict or type(approval) is not dict:
        return False
    return all([
        _hash(state.get('artifact_sha256')), _hash(state.get('harness_sha256')),
        _nonempty(state.get('task')), _run_id(run.get('run_id')),
        type(run.get('exit_code')) is int,
        type(run.get('artifact_stable')) is bool,
        type(run.get('harness_stable')) is bool,
        _hash(run.get('artifact_sha256')), _hash(run.get('harness_sha256')),
        _nonempty(run.get('task')), 'error' in run,
        run.get('error') is None or _nonempty(run.get('error')),
        type(approval.get('active')) is bool,
        _hash(approval.get('artifact_sha256')), _nonempty(approval.get('task')),
        _run_id(approval.get('run_id')),
    ])


def observed_contract(state):
    """Explain the actual external gates; never consume the proposed explanation."""
    valid = _valid_state(state)
    state = state if type(state) is dict else {}
    observation = state.get('observation') if type(state.get('observation')) is dict else {}
    approval = state.get('approval') if type(state.get('approval')) is dict else {}
    checks = {
        'runtime_schema_valid': valid,
        'execution_observed': bool(observation),
        'test_passed': type(observation.get('exit_code')) is int and observation.get('exit_code') == 0,
        'observation_completed': observation.get('error') is None and 'error' in observation,
        'artifact_stable_during_run': observation.get('artifact_stable') is True,
        'harness_stable_during_run': observation.get('harness_stable') is True,
        'expected_harness_used': _hash(state.get('harness_sha256')) and observation.get('harness_sha256') == state.get('harness_sha256'),
        'current_artifact_tested': _hash(state.get('artifact_sha256')) and observation.get('artifact_sha256') == state.get('artifact_sha256'),
        'current_task_tested': _nonempty(state.get('task')) and observation.get('task') == state.get('task'),
        'approval_active': approval.get('active') is True,
        'approval_current_artifact': _hash(state.get('artifact_sha256')) and approval.get('artifact_sha256') == state.get('artifact_sha256'),
        'approval_current_task': _nonempty(state.get('task')) and approval.get('task') == state.get('task'),
        'approval_current_execution': _run_id(observation.get('run_id')) and _run_id(approval.get('run_id')) and type(approval.get('run_id')) is type(observation.get('run_id')) and approval.get('run_id') == observation.get('run_id'),
    }
    return dict(permit=all(checks.values()), checks=checks,
                unmet=[key for key, value in checks.items() if not value])


def conventional_revalidation(state):
    """Strong baseline: ordinary execution/version/approval checks, same evidence.

    Intentionally expresses the same policy without NyAI explanation records.
    Equivalent outcomes would demonstrate no incremental decision benefit.
    """
    if not _valid_state(state):
        return False
    run, approval = state['observation'], state['approval']
    if not approval['active']:
        return False
    if run['exit_code'] != 0 or not run['artifact_stable'] or not run['harness_stable'] or run['error'] is not None:
        return False
    if run['harness_sha256'] != state['harness_sha256']:
        return False
    current = (state.get('artifact_sha256'), state.get('task'))
    return (run['artifact_sha256'], run['task']) == current and (
        approval['artifact_sha256'], approval['task']) == current and type(approval['run_id']) is type(run['run_id']) and approval['run_id'] == run['run_id']
