"""Prepare, execute or verify the private bounded research-artifact study."""
import argparse
import copy
import csv
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from nyai_research.evidence_bound import (
    Observer, bindings, encoded, evaluate, fixture, reference_decision, sha,
)

STUDY = ROOT/'experiments/evidence_bound_v1'
ARMS = ['report_only_control', 'execution_integrity_only', 'lineage_selective',
        'complete_revalidation', 'complete_revalidation_with_records']
# Scenarios contain transformations, not expected labels. No arm sees this list.
CASES = [
    ('valid_current', []), ('valid_threshold_boundary', ['boundary']),
    ('observed_rate_fails', ['high_rate']), ('no_execution', ['no_run']),
    ('empty_evaluation', ['empty']), ('unregistered_success_record', ['forged']),
    ('outputs_changed', ['outputs_changed']), ('dataset_changed', ['dataset_changed']),
    ('harness_changed', ['harness_changed']), ('configuration_changed', ['config_changed']),
    ('model_version_changed', ['model_changed']), ('population_safety_overclaim', ['overclaim']),
    ('subgroup_failure_hidden_by_aggregate', ['red_scope']), ('stricter_claim_unsupported', ['strict_claim']),
    ('incomplete_output_coverage', ['missing_output']), ('active_contrary_rerun', ['contrary']),
    ('contrary_run_retired_by_authority', ['contrary', 'retire_contrary']),
    ('supporting_run_retracted', ['retract']), ('permission_revoked', ['revoke']),
    ('approval_for_another_run', ['wrong_approval']), ('benign_unrelated_note', ['note']),
    ('failure_corrected_and_reapproved', ['high_rate', 'repair']),
    ('missing_dataset_dependency_edge', ['omit_dataset_edge', 'dataset_changed']),
    ('missing_counterevidence_dependency_edge', ['omit_active_edge', 'contrary']),
]


def file_hash(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze_sources():
    names = ['experiments/evidence_bound_v1/protocol.json',
             'experiments/evidence_bound_v1/cases.json',
             'src/nyai_research/evidence_bound.py', 'scripts/run_evidence_bound.py']
    return {name: file_hash(ROOT/name) for name in names}


def prepare():
    if (STUDY/'freeze.json').exists():
        raise RuntimeError('Freeze exists; do not silently replace it. Use an explicit amendment/new study.')
    (STUDY/'cases.json').write_text(json.dumps([dict(case_id=k, operations=v) for k,v in CASES], indent=2)+'\n')
    (STUDY/'freeze.json').write_text(json.dumps(dict(source_hashes=freeze_sources(),
        created_before_first_run=True, external_preregistration=False,
        interpretation='Local prospective source freeze only; author has seen all transformations.'), indent=2)+'\n')
    print('Prepared protocol/cases/source freeze; no benchmark execution performed.')


def check_freeze():
    amendments = sorted(STUDY.glob('amendment_*.json'))
    amendment = amendments[-1] if amendments else STUDY/'freeze.json'
    frozen = json.loads((amendment if amendment.exists() else STUDY/'freeze.json').read_text())['source_hashes']
    if frozen != freeze_sources():
        raise RuntimeError('Frozen source changed. Preserve results and create a documented amendment.')


def make_case(spec):
    observer = Observer()
    files = fixture()
    claim = dict(model_id='fictional-model-v1', task='fictional-refusal-evaluation-v1',
                 group='all', kind='observed_rate', max_rate=0.1)
    run_id = observer.run(files)
    packet = dict(files=files, registry=observer.snapshot(), observation_id=run_id,
        active_run_ids=[run_id], claim=claim,
        approval=dict(active=True, run_id=run_id, claim_sha256=sha(encoded(claim))))
    dependencies = list(bindings(files))+['claim', 'active_run_ids', 'approval', 'observation_id']
    initial_packet = copy.deepcopy(packet)
    initial_accept = evaluate(packet)['accept']
    events = []

    def run_current():
        new_id = observer.run(files)
        packet['observation_id'] = new_id
        packet['active_run_ids'] = [new_id]
        packet['registry'] = observer.snapshot()
        packet['approval'] = dict(active=True, run_id=new_id, claim_sha256=sha(encoded(claim)))

    for op in spec['operations']:
        if op == 'boundary':
            files['outputs.json'] = fixture(2)['outputs.json']; run_current()
        elif op == 'high_rate':
            files['outputs.json'] = fixture(6)['outputs.json']; run_current()
        elif op == 'no_run':
            packet['registry'] = {}; packet['observation_id'] = 'absent'
        elif op == 'empty':
            files['dataset.json'] = '[]'; files['outputs.json'] = '{}'; run_current()
        elif op == 'forged':
            packet['observation_id'] = 'unregistered-agent-written-success'
        elif op == 'outputs_changed':
            files['outputs.json'] = fixture(5)['outputs.json']
        elif op == 'dataset_changed':
            data = json.loads(files['dataset.json']); data[0]['group'] = 'revised'; files['dataset.json'] = encoded(data)
        elif op == 'harness_changed':
            files['grader.py'] = '# An empty harness would exit zero.\n'
        elif op == 'config_changed':
            config = json.loads(files['config.json']); config['max_rate'] = 0.01; files['config.json'] = encoded(config)
        elif op == 'model_changed':
            files['model.json'] = encoded({'model_id': 'fictional-model-v2'})
        elif op == 'overclaim':
            claim['kind'] = 'general_model_safety'; packet['approval']['claim_sha256'] = sha(encoded(claim))
        elif op == 'red_scope':
            claim['group'] = 'red'; packet['approval']['claim_sha256'] = sha(encoded(claim))
        elif op == 'strict_claim':
            claim['max_rate'] = 0.0; packet['approval']['claim_sha256'] = sha(encoded(claim))
        elif op == 'missing_output':
            value = json.loads(files['outputs.json']); value.pop('p00'); files['outputs.json'] = encoded(value); run_current()
        elif op == 'contrary':
            other = copy.deepcopy(files); other['outputs.json'] = fixture(8)['outputs.json']
            contrary_id = observer.run(other); packet['registry'] = observer.snapshot(); packet['active_run_ids'].append(contrary_id)
        elif op == 'retire_contrary':
            packet['active_run_ids'] = [packet['observation_id']]
        elif op == 'retract':
            packet['active_run_ids'] = []
        elif op == 'revoke':
            packet['approval']['active'] = False
        elif op == 'wrong_approval':
            packet['approval']['run_id'] = 'different-execution'
        elif op == 'note':
            files['notes.txt'] += 'A harmless annotation was edited.\n'
        elif op == 'repair':
            files['outputs.json'] = fixture()['outputs.json']; run_current()
        elif op == 'omit_dataset_edge':
            dependencies.remove('dataset.json')
        elif op == 'omit_active_edge':
            dependencies.remove('active_run_ids')
        else:
            raise ValueError(op)
        events.append(dict(event=op, bound_hashes=bindings(files), observation_id=packet['observation_id'],
                           active_run_ids=list(packet['active_run_ids']), approval=copy.deepcopy(packet['approval'])))
    changed = [name for name in bindings(files) if bindings(files)[name] != bindings(initial_packet['files'])[name]]
    changed += [key for key in ('claim', 'active_run_ids', 'approval', 'observation_id') if packet[key] != initial_packet[key]]
    # Adding a run to a host registry does not itself notify a claim cache; active
    # evidence is a distinct dependency that a declaration can wrongly omit.
    rechecked = bool(set(changed) & set(dependencies))
    result = evaluate(packet)
    return dict(case_id=spec['case_id'], packet=packet, execution_log=observer.snapshot(), events=events,
        declared_dependencies=dependencies, changed_dependencies=changed,
        initial_accept=initial_accept, lineage_rechecked=rechecked,
        reference_accept=reference_decision(packet), record=result,
        decisions=dict(report_only_control=True,
            execution_integrity_only=result['integrity_accept'],
            lineage_selective=result['accept'] if rechecked else initial_accept,
            complete_revalidation=result['accept'],
            complete_revalidation_with_records=result['accept']))


def summarize(records):
    yes = [r for r in records if r['reference_accept']]
    no = [r for r in records if not r['reference_accept']]
    arms = {}
    for arm in ARMS:
        arms[arm] = dict(reference_accepts=len(yes), reference_withholds=len(no),
            correct_accepts=sum(r['decisions'][arm] for r in yes),
            unwarranted_accepts=sum(r['decisions'][arm] for r in no),
            appropriate_withholds=sum(not r['decisions'][arm] for r in no),
            false_withholds=sum(not r['decisions'][arm] for r in yes),
            matches=sum(r['decisions'][arm] == r['reference_accept'] for r in records))
    # Keep all host executions even when the evidence-access fixture removes a
    # run from the reviewer's registry. Older archives lacked this separate log.
    observations = [v for r in records for v in r.get('execution_log', r['packet']['registry']).values()]
    return dict(scenarios=len(records), arms=arms, execution_runs=len(observations),
        execution_errors=sum(v['exit_code'] != 0 for v in observations),
        model_calls=0, model_tokens=0, api_cost=0,
        lineage_rechecks=sum(r['lineage_rechecked'] for r in records),
        full_contract_checks_per_case=records[0]['record']['checks_performed'],
        recorded_vs_complete_disagreements=[r['case_id'] for r in records if r['decisions']['complete_revalidation'] != r['decisions']['complete_revalidation_with_records']],
        selective_vs_complete_disagreements=[r['case_id'] for r in records if r['decisions']['lineage_selective'] != r['decisions']['complete_revalidation']],
        interpretation='Specification-derived engineering results. No independent human labels, LLM reviewer outcomes or NyAI decision superiority. Timings are process observations, not end-to-end comparative overhead.')


def execute(output):
    check_freeze()
    if output.exists():
        raise RuntimeError('Output exists; choose a new path to preserve raw records.')
    specs = json.loads((STUDY/'cases.json').read_text())
    records = [make_case(spec) for spec in specs]
    output.mkdir(parents=True)
    (output/'records.jsonl').write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in records))
    summary = summarize(records)
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    (output/'review_packet.json').write_text(json.dumps(dict(
        instructions='Review raw artifacts/current state before consulting summary or records. Apply the frozen policy and record ambiguity. This is not independent review until a person actually supplies judgments.',
        cases=[dict(case_id=r['case_id'], packet=r['packet'], events=r['events']) for r in records]), indent=2)+'\n')
    with (output/'review_queue.csv').open('w', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(['case_id','reviewer','accept','rationale','ambiguity'])
        for r in records: writer.writerow([r['case_id'],'','','',''])
    (output/'manifest.json').write_text(json.dumps(dict(source_hashes=freeze_sources(),
        records_sha256=file_hash(output/'records.jsonl'), summary_sha256=file_hash(output/'summary.json'),
        python=sys.version, platform=platform.platform(),
        total_observed_execution_seconds=sum(v['elapsed_seconds'] for r in records for v in r['execution_log'].values()),
        agent_responses='None: behavioral strings and success claims are fictional fixtures.'), indent=2)+'\n')
    print(json.dumps(summary, indent=2))


def verify(output):
    check_freeze()
    records = [json.loads(line) for line in (output/'records.jsonl').read_text().splitlines()]
    manifest = json.loads((output/'manifest.json').read_text())
    approved = [json.loads((STUDY/'freeze.json').read_text())['source_hashes']]
    for amendment in sorted(STUDY.glob('amendment_*.json')):
        approved.append(json.loads(amendment.read_text())['source_hashes'])
    assert manifest['source_hashes'] in approved
    assert manifest['records_sha256'] == file_hash(output/'records.jsonl')
    assert manifest['summary_sha256'] == file_hash(output/'summary.json')
    assert len({r['case_id'] for r in records}) == len(records)
    for r in records:
        assert r['reference_accept'] == reference_decision(r['packet'])
        assert r['record'] == evaluate(r['packet'])
        assert r['decisions']['complete_revalidation'] == r['record']['accept']
        assert r['decisions']['complete_revalidation_with_records'] == r['record']['accept']
    assert summarize(records) == json.loads((output/'summary.json').read_text())
    print('PASS: frozen sources, raw record hashes, reference recomputation and arm counts; not independent scientific validation.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare','run','verify'], required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'results/evidence_bound_v1')
    args = parser.parse_args()
    if args.phase == 'prepare': prepare()
    elif args.phase == 'run': execute(args.output)
    else: verify(args.output)
