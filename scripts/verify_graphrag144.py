"""Offline audit of the complete 144-case RAG experiment and its rendered evidence."""
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nyai_research.rag_benchmark import ARMS, sha, model_payload, BASE, STRUCTURED
OUT=ROOT/'experiments/graphrag_144_v1'
RESULTS=ROOT/'results/graphrag_144_v1'


if __name__=='__main__':
    protocol=json.loads((OUT/'protocol.json').read_text())
    amendment=json.loads((OUT/'pre_execution_amendment.json').read_text())
    for path,digest in {**protocol['hashes'],**amendment['hashes']}.items():
        assert sha((ROOT/path).read_text())==digest,path
    cases={c['case_id']:c for c in json.loads((OUT/'cases.json').read_text())}
    contexts={(c['case_id'],c['arm']):c for c in json.loads((OUT/'retrieved_contexts.json').read_text())}
    raw=[json.loads(line) for line in (RESULTS/'model_responses.jsonl').read_text().splitlines()]
    assert len(cases)==144 and len(contexts)==576 and len(raw)==576
    assert len({(r['case_id'],r['arm']) for r in raw})==576
    for case in cases.values():
        assert contexts[(case['case_id'],'graph_rag')]['facts']==contexts[(case['case_id'],'graph_rag_structured')]['facts']
    for row in raw:
        case=cases[row['case_id']];context=contexts[(row['case_id'],row['arm'])]
        payload=json.loads(row['messages'][1]['content'])
        assert payload==model_payload(case,context['facts'])
        assert row['context_sha256']==sha(context['facts'])==context['context_sha256']
        assert row['payload_sha256']==sha(payload)
        prompt=STRUCTURED if row['arm']=='graph_rag_structured' else BASE
        assert row['messages'][0]['content']==prompt and row['prompt_sha256']==sha(prompt)
        assert not {'design_label','target_source_id','target_fact_ids','review_status'} & set(payload)
        if row.get('response_id'):
            assert row['returned_model']=='gpt-6-luna'
        else:
            assert row.get('error_type') and 'parsed' not in row
        if 'parsed' in row:assert row['parsed']==json.loads(row['raw_text'])
        assert len(json.dumps(context['facts'],ensure_ascii=False))<=8000
    sources=json.loads((OUT/'sources.json').read_text())
    assert len(sources)==19 and sum(len(s['facts']) for s in sources)==48
    for source in sources:
        assert not {'candidate_response','design_label','design_expected_execute'} & set(source)
    imported=json.loads((RESULTS/'graph_import.json').read_text())
    assert imported['namespace_nodes']==86 and imported['original_notes_before']==imported['original_notes_after']==100
    flat=list(csv.DictReader((RESULTS/'predictions.csv').open()))
    summary=json.loads((RESULTS/'summary.json').read_text())
    for domain in ['policy_audit','action_contract']:
        for arm in ARMS:
            selected=[r for r in flat if r['domain']==domain and r['arm']==arm]
            expected=summary['scores'][domain][arm]
            assert len(selected)==expected['n_cases']
            assert sum(r['match']=='True' for r in selected)==expected['matches']
            assert sum(bool(r['error_type']) for r in selected)==expected['invalid_outputs']
    result=dict(status='PASS',model_request_records=576,
        actual_api_responses=sum(bool(r.get('response_id')) for r in raw),case_arm_uniqueness=True,
        no_label_fields_in_payload=True,structured_arm_evidence_identical=True,
        frozen_source_and_code_hashes_match=True,independent_csv_tally_matches=True,
        namespace_nodes=86,original_note_count_unchanged=True,
        limits='Integrity/replay checks only; no independent human verification or scientific efficacy certification')
    (RESULTS/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
