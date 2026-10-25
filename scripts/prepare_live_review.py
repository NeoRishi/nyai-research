"""Blind review worksheet for actual model outputs; no template labels copied."""
import csv,json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

if __name__=='__main__':
    cases={r['case_id']:r for r in [json.loads(s) for s in (ROOT/'data/fixtures/24_agentic_contract_cases.jsonl').read_text().splitlines()]}
    responses=[json.loads(s) for s in (ROOT/'results/agentic_model_responses.jsonl').read_text().splitlines()]
    random.Random(20261027).shuffle(responses)
    path=ROOT/'data/annotations/live_output_review.csv'
    with path.open('w') as f:
        fields=['review_id','source_policy','runtime_facts','actual_candidate_response','reviewed_label','reviewer_id','review_notes']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for i,r in enumerate(responses,1):
            c=cases[r['case_id']]
            w.writerow(dict(review_id=f'LIVE-{i:03}',source_policy=c['policy'],runtime_facts=json.dumps(c['state']),
                actual_candidate_response=r.get('raw_text',''),reviewed_label='',reviewer_id='',review_notes=''))
    # Key is an analysis aid; do not give it to reviewers before annotation.
    (ROOT/'data/annotations/live_review_key.json').write_text(json.dumps({f'LIVE-{i:03}':r['case_id'] for i,r in enumerate(responses,1)},indent=2)+'\n')
    print('24 actual outputs queued; human-reviewed labels remain empty')
