"""Offline integrity checks for recorded evidence and independently recomputed metrics."""
import csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return [json.loads(s) for s in (ROOT/path).read_text().splitlines() if s.strip()]


if __name__=='__main__':
    cases=read('data/fixtures/120_synthetic_cases.jsonl')
    assert len(cases)==120 and all(c['review_status']=='unreviewed' for c in cases)
    original=json.loads((ROOT/'experiments/protocol_freeze.json').read_text())
    amendment=json.loads((ROOT/'experiments/protocol_amendment_01.json').read_text())
    hashes={**original['hashes'],**amendment['hashes']}
    for p,expected in hashes.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==expected,p
    rows=read('results/template_pilot.jsonl')
    assert len(rows)==360 and len({(r['case_id'],r['condition']) for r in rows})==360
    assert Counter(r['condition'] for r in rows)==dict(baseline=120,checklist=120,structured=120)
    for r in rows:
        payload=json.loads(r['messages'][1]['content'])
        assert set(payload)=={'case_id','scenario','reference_requirement','reference_boundary','candidate_response'}
        assert 'gold_label' not in payload
        assert hashlib.sha256(r['messages'][0]['content'].encode()).hexdigest()==r['prompt_sha256']
        assert hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()==r['payload_sha256']
        assert r['returned_model']=='gpt-6-luna' and r.get('response_id')
    # Rescore from exported CSV, without using the scorer's implementation.
    csv_rows=list(csv.DictReader((ROOT/'results/template_predictions.csv').open()))
    summary=json.loads((ROOT/'results/template_pilot_summary.json').read_text())
    for arm in ['baseline','checklist','structured']:
        selected=[r for r in csv_rows if r['condition']==arm]
        matches=len([r for r in selected if r['model_label']==r['unreviewed_template_label']])
        assert matches==summary['scores'][arm]['template_matches']
        assert sum(not r['model_label'] for r in selected)==summary['scores'][arm]['error_count']
    assert all(r.get('finish_reason')=='length' for r in rows if r.get('error_type'))
    assert len(read('results/failed_temperature0_template_pilot.jsonl'))==360
    assert len(read('results/failed_temperature0_agentic_model_responses.jsonl'))==24
    generated=read('results/agentic_model_responses.jsonl')
    assert len(generated)==24 and len({r['case_id'] for r in generated})==24
    assert all(r.get('generated_from')=='model_api' and 'gold_label' not in r for r in generated)
    reviewed=json.loads((ROOT/'results/human_verified_metrics.json').read_text())
    assert reviewed['n_verified_annotations']==0 and reviewed['scores']=={}
    assert len(list(csv.DictReader((ROOT/'data/annotations/live_output_review.csv').open())))==24
    source=json.loads((ROOT/'results/vcim_source_check.json').read_text())
    assert len(source['registry_rows'])==18 and all(r['matches'] for r in source['registry_rows'])
    assert len(source['fixture_reference_checks'])==120 and all(r['reference_text_matches'] for r in source['fixture_reference_checks'])
    assert json.loads((ROOT/'results/graph_audit.json').read_text())['database_writes'] is False
    out=dict(status='PASS',checks=['protocol and amended source hashes','360 unique audit records',
        'no label fields in model input','raw response identities','independent CSV metric tally',
        'failed requests and truncations retained','24 generated decisions distinct from templates',
        'human-reviewed metrics empty','source transcription only','read-only database audit'])
    (ROOT/'results/artifact_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
