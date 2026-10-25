"""Descriptive fixture agreement; intentionally separate from human-verified metrics."""
import csv,json,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nyai_research.evaluate import read_jsonl


def summarize(cases,rows):
    ids={c['case_id']:c for c in cases}
    groups=defaultdict(dict)
    for r in rows:
        if r['case_id'] in groups[r['condition']]:raise ValueError('Duplicate case-condition')
        groups[r['condition']][r['case_id']]=r
    result={}
    for arm,records in groups.items():
        confusion=Counter();toks=Counter();latencies=[]
        for cid,c in ids.items():
            r=records.get(cid,{})
            prediction=r.get('label') or 'ERROR'
            confusion[(c['gold_label'],prediction)]+=1
            for k in ['prompt_tokens','completion_tokens','total_tokens']:toks[k]+=r.get('usage',{}).get(k,0)
            if 'latency_seconds' in r:latencies.append(r['latency_seconds'])
        n=len(cases)
        violations=sum(c['gold_label']=='violation' for c in cases)
        tp=confusion[('violation','violation')]
        fp=sum(v for (truth,pred),v in confusion.items() if truth!='violation' and pred=='violation')
        matches=sum(v for (truth,pred),v in confusion.items() if truth==pred)
        result[arm]=dict(n_cases=n,n_records=len(records),template_matches=matches,
            template_agreement=matches/n,violation_recall_vs_template=tp/violations,
            violation_false_positive_rate_vs_template=fp/(n-violations),
            violation_precision_vs_template=tp/(tp+fp) if tp+fp else None,
            error_count=sum(v for (truth,pred),v in confusion.items() if pred=='ERROR'),
            confusion=[dict(template_label=t,prediction=p,n=v) for (t,p),v in sorted(confusion.items())],
            tokens=dict(toks),median_request_seconds=statistics.median(latencies) if latencies else None)
    return result


if __name__=='__main__':
    cases=list(read_jsonl(ROOT/'data/fixtures/120_synthetic_cases.jsonl'))
    rows=list(read_jsonl(ROOT/'results/template_pilot.jsonl'))
    out=dict(status='UNREVIEWED SYNTHETIC TEMPLATE AGREEMENT; NOT VERIFIED ACCURACY',
        human_verified_cases=0,scores=summarize(cases,rows),
        by_original_split={s:summarize([c for c in cases if c['split']==s],[r for r in rows if r['split']==s]) for s in ['development','heldout']},
        limitations=['Templates share policy wording; effective sample size is not 120 independent cases.',
        'No improvement in human oversight is tested.', 'Prompt structure, instruction length and checklist content are confounded.',
        'Model judgments and rule-derived labels can share biases. No independent human annotation.',
        'Actual API outputs are distinct from their synthetic candidate inputs.',
        'No inferential intervals: correlated, unreviewed design labels do not support population inference.'])
    by={(r['case_id'],r['condition']):r for r in rows}
    disagreements=[]
    for c in cases:
        preds={a:by.get((c['case_id'],a),{}).get('label') for a in ['baseline','checklist','structured']}
        if len(set(preds.values()))>1 or any(p!=c['gold_label'] for p in preds.values()):
            disagreements.append(dict(case_id=c['case_id'],unreviewed_template_label=c['gold_label'],predictions=preds))
    out['disagreements']=disagreements
    paired={}
    for comparator in ['baseline','checklist']:
        counts=Counter()
        for c in cases:
            a=by.get((c['case_id'],'structured'),{}).get('label')==c['gold_label']
            b=by.get((c['case_id'],comparator),{}).get('label')==c['gold_label']
            counts['both_match' if a and b else 'structured_only_matches' if a else 'comparator_only_matches' if b else 'neither_matches']+=1
        paired['structured_vs_'+comparator]=dict(counts)
    out['paired_template_matches']=paired
    (ROOT/'results/template_pilot_summary.json').write_text(json.dumps(out,indent=2)+'\n')
    with (ROOT/'results/template_predictions.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['case_id','condition','unreviewed_template_label','model_label'])
        for r in sorted(rows,key=lambda x:(x['case_id'],x['condition'])):
            w.writerow([r['case_id'],r['condition'],next(c['gold_label'] for c in cases if c['case_id']==r['case_id']),r.get('label')])
    print(json.dumps(dict(status=out['status'],scores=out['scores'],n_disagreements=len(disagreements)),indent=2))
