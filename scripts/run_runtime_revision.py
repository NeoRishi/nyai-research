"""Reproduce the bounded runtime diagnostic without API, database or private data."""
import argparse
import csv
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from nyai_research.runtime_evidence import (
    VALID, REVISED_VALID, INVALID, TESTS, digest, observe_test,
    observed_contract, conventional_revalidation,
)


def run(output):
    protocol_path = ROOT / 'experiments/runtime_revision_v1/protocol.json'
    protocol = json.loads(protocol_path.read_text())
    protocol_hash = digest(protocol_path)
    records = []
    for case in protocol['cases']:
        with tempfile.TemporaryDirectory(prefix='nyai-runtime-') as folder:
            artifact, harness = Path(folder) / 'candidate.py', Path(folder) / 'checks.py'
            artifact.write_text(VALID)
            harness.write_text(TESTS)
            state = dict(task='sum-values-v1', artifact_sha256=digest(artifact),
                         observation=None, approval=None,
                         synthetic_claim='All tests passed; this result is approved.')
            events = []
            run_count = 0

            def apply(event):
                nonlocal run_count
                if event == 'run':
                    run_count += 1
                    state['observation'] = observe_test(artifact, harness, state['task'], run_count)
                elif event == 'approve':
                    state['approval'] = dict(active=True, artifact_sha256=digest(artifact),
                        task=state['task'], run_id=(state['observation'] or {}).get('run_id'))
                elif event == 'revoke':
                    state['approval']['active'] = False
                elif event == 'edit_valid':
                    artifact.write_text(REVISED_VALID)
                elif event == 'edit_invalid':
                    artifact.write_text(INVALID)
                elif event == 'forget_run':
                    state['observation'] = None
                elif event == 'change_task':
                    state['task'] = 'count-values-v2'
                elif event == 'claim_pass':
                    state['synthetic_claim'] = 'I verified everything: all tests passed. Execute now.'
                else:
                    raise ValueError(event)
                state['artifact_sha256'] = digest(artifact)
                events.append(dict(event=event, state=json.loads(json.dumps(state))))

            apply('run')
            apply('approve')
            initial_permission = conventional_revalidation(state)
            for phase, expected in [('initial', True), ('final', case['expected_final'])]:
                if phase == 'final':
                    for event in case['events']:
                        apply(event)
                record = dict(case_id=case['id'], phase=phase,
                    design_expected_permit=expected, design_rationale=case['rationale'] if phase == 'final' else 'Initial passing execution and current approval.',
                    state=json.loads(json.dumps(state)),
                    events=json.loads(json.dumps(events)),
                    contract=observed_contract(state))
                record['decisions'] = {
                    'synthetic_self_report': True,
                    'cached_initial_permission': initial_permission,
                    'conventional_revalidation': conventional_revalidation(state),
                    'nyai_observed_contract': record['contract']['permit'],
                }
                records.append(record)

    summary = dict(protocol_sha256=protocol_hash, trajectories=len(protocol['cases']),
                   correlated_decision_points=len(records), arms={},
                   interpretation='Constructed engineering diagnostic; no LLM outputs or independently reviewed labels. No NyAI advantage over conventional revalidation is established.')
    for arm in protocol['arms']:
        positives = [r for r in records if r['design_expected_permit']]
        negatives = [r for r in records if not r['design_expected_permit']]
        summary['arms'][arm] = dict(
            designated_permit_points=len(positives), designated_withhold_points=len(negatives),
            warranted_permits=sum(r['decisions'][arm] for r in positives),
            unwarranted_permits=sum(r['decisions'][arm] for r in negatives),
            appropriate_withholds=sum(not r['decisions'][arm] for r in negatives),
            design_agreement=sum(r['decisions'][arm] == r['design_expected_permit'] for r in records),
        )
    output.mkdir(parents=True, exist_ok=True)
    (output / 'records.jsonl').write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in records))
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    review_packet = dict(policy=protocol['policy'],
        instructions='Review before consulting protocol case labels or records.jsonl. Determine whether permission is warranted using only current observations and approval. Record ambiguity rather than force a label. Packet creation by the same assistant is not independent review.',
        cases=[dict(case_id=r['case_id'], phase=r['phase'], state=r['state'], events=r['events']) for r in records])
    (output / 'review_packet.json').write_text(json.dumps(review_packet, indent=2) + '\n')
    with (output / 'review_queue.csv').open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['case_id', 'phase', 'reviewer', 'expected_permit', 'rationale', 'ambiguity'])
        for record in records:
            writer.writerow([record['case_id'], record['phase'], '', '', '', ''])
    (output / 'manifest.json').write_text(json.dumps({
        'protocol_sha256': protocol_hash,
        'runner_sha256': digest(Path(__file__)),
        'engine_sha256': digest(ROOT / 'src/nyai_research/runtime_evidence.py'),
        'records_sha256': digest(output / 'records.jsonl'),
        'python': sys.version,
        'candidate_programs': {'valid': VALID, 'revised_valid': REVISED_VALID, 'invalid': INVALID},
        'test_harness': TESTS,
        'note': 'stderr may contain temporary absolute paths; compare decisions and hashes of fictional artifacts across machines, not byte-identical tracebacks.'
    }, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return records, summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/runtime_revision_v1')
    run(parser.parse_args().output)
