"""Descriptive results for source-reference retrieval and actual RAG judgments.

No unreviewed policy label becomes verified truth. Contract checks use a separately
coded same-author oracle. Correlated cases do not justify IID significance claims.
"""
from collections import Counter
import csv
import importlib.util
import json
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nyai_research.rag_benchmark import ARMS, sha
OUT=ROOT/'experiments/graphrag_144_v1'
RESULTS=ROOT/'results/graphrag_144_v1'


def load_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


if __name__=='__main__':
    cases={c['case_id']:c for c in json.loads((OUT/'cases.json').read_text())}
    contexts={(c['case_id'],c['arm']):c for c in json.loads((OUT/'retrieved_contexts.json').read_text())}
    rows=load_rows(RESULTS/'model_responses.jsonl')
    assert len(rows)==576 and len({(r['case_id'],r['arm']) for r in rows})==576, 'Incomplete or duplicate run'
    protocol=json.loads((OUT/'protocol.json').read_text())
    hashes=dict(protocol['hashes'])
    amendment=OUT/'pre_execution_amendment.json'
    if amendment.exists():hashes.update(json.loads(amendment.read_text())['hashes'])
    for p,digest in hashes.items():
        assert sha((ROOT/p).read_text())==digest, p
    spec=importlib.util.spec_from_file_location('separate_oracle',ROOT/'scripts/verify_agentic.py')
    oracle_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle_module)
    for c in cases.values():
        if c['domain']=='action_contract':assert oracle_module.oracle(c['state'])==c['design_label']
    by={(r['case_id'],r['arm']):r for r in rows}
    predictions=[];scores={}
    for domain in ['policy_audit','action_contract']:
        scores[domain]={}
        selected=[c for c in cases.values() if c['domain']==domain]
        for arm in ARMS:
            matches=errors=tp=fp=fn=tn=invalid_citations=total_citations=empty_citations=0
            tokens=Counter();latencies=[];confusion=Counter()
            for c in selected:
                r=by[(c['case_id'],arm)];context=contexts[(c['case_id'],arm)]
                parsed=r.get('parsed',{})
                pred=parsed.get('label') if domain=='policy_audit' else parsed.get('execute')
                if 'error_type' in r:pred=None
                expected=c['design_label'];match=pred is not None and pred==expected
                matches+=match;errors+=pred is None
                confusion[(str(expected),str(pred))]+=1
                positive=(expected=='violation') if domain=='policy_audit' else expected is False
                flagged=(pred=='violation') if domain=='policy_audit' else pred is False
                tp+=positive and flagged;fp+=not positive and flagged
                fn+=positive and not flagged;tn+=not positive and not flagged
                citations=parsed.get('cited_fact_ids',[])
                ids={f['fact_id'] for f in context['facts']}
                if isinstance(citations,list):
                    total_citations+=len(citations)
                    invalid_citations+=sum(type(v) is not str or v not in ids for v in citations)
                    empty_citations+=bool(parsed) and not citations
                for field in ['prompt_tokens','completion_tokens','total_tokens']:
                    tokens[field]+=r.get('usage',{}).get(field,0)
                latencies.append(r['latency_seconds'])
                predictions.append(dict(case_id=c['case_id'],domain=domain,arm=arm,
                    reference_kind='unreviewed_design_label' if domain=='policy_audit' else 'automated_contract_oracle',
                    expected=expected,prediction=pred,match=match,error_type=r.get('error_type','')))
            cts=[contexts[(c['case_id'],arm)] for c in selected]
            unique_cts={sha(c['query']):contexts[(c['case_id'],arm)] for c in selected}
            scores[domain][arm]=dict(n_cases=len(selected),matches=matches,agreement=matches/len(selected),
                reference_fact_recall_mean_per_case=statistics.mean(c['target_fact_recall'] for c in cts),
                unique_retrieval_queries=len(unique_cts),
                reference_fact_recall_mean_per_unique_query=statistics.mean(c['target_fact_recall'] for c in unique_cts.values()),
                reference_source_hit_rate=sum(c['target_source_hit'] for c in cts)/len(cts),
                violation_or_defeat_recall=tp/(tp+fn) if tp+fn else None,
                violation_or_defeat_false_positive_rate=fp/(fp+tn) if fp+tn else None,
                invalid_outputs=errors,unresolvable_cited_fact_ids=invalid_citations,cited_fact_ids=total_citations,
                parsed_outputs_without_citations=empty_citations,
                tokens=dict(tokens),median_request_seconds=statistics.median(latencies),
                confusion=[dict(expected=a,prediction=b,n=n) for (a,b),n in sorted(confusion.items())])
    paired={}
    for domain in scores:
        paired[domain]={}
        for left,right in [('graph_rag','vector_rag'),('graph_rag_structured','graph_rag'),('graph_rag','full_reference')]:
            counts=Counter()
            for c in cases.values():
                if c['domain']!=domain:continue
                def match(arm):
                    row=by[(c['case_id'],arm)];p=row.get('parsed',{})
                    pred=p.get('label') if domain=='policy_audit' else p.get('execute')
                    return 'error_type' not in row and pred is not None and pred==c['design_label']
                a,b=match(left),match(right)
                counts['both_match' if a and b else 'left_only' if a else 'right_only' if b else 'neither']+=1
            paired[domain][left+'_vs_'+right]=dict(counts)
    result=dict(status='CONTROLLED ACTUAL-NEO4J POLICY-RETRIEVAL PILOT; NO HUMAN OVERSIGHT CLAIM',
        model_request_records=len(rows),actual_api_responses=sum(bool(r.get('response_id')) for r in rows),
        requests_without_api_response=sum(not r.get('response_id') for r in rows),
        unique_retrieval_queries=protocol['query_variants'],
        scores=scores,paired=paired,
        limitations=['The source graph was created from reference policies for these same known cases; no source-family holdout.',
            'Graph expansion supplies sibling requirements; a gain can be due to evidence coverage and context length, not better reasoning.',
            'Policy labels remain unreviewed. Contract oracle and implementation share an AI author.',
            'Existing wellness knowledge graph does not contain the exact benchmark reference IDs; this is a separate evaluation namespace.',
            'The underlying cases remain synthetic even though retrieval and model calls are real.',
            'One mutable model alias and one stochastic response per arm; no human study or independent scientific validation.',
            'No IID confidence interval or significance claim for correlated design cases.'])
    (RESULTS/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    with (RESULTS/'predictions.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(predictions[0]),lineterminator='\n');w.writeheader();w.writerows(predictions)
    # Independent tally from the saved flat export, not the in-memory score totals.
    exported=list(csv.DictReader((RESULTS/'predictions.csv').open()))
    for domain in scores:
        for arm in ARMS:
            subset=[r for r in exported if r['domain']==domain and r['arm']==arm]
            assert sum(r['match']=='True' for r in subset)==scores[domain][arm]['matches']
    print(json.dumps(dict(model_request_records=len(rows),actual_api_responses=result['actual_api_responses'],scores={domain:{arm:{k:v for k,v in score.items() if k in
        ['n_cases','matches','agreement','reference_fact_recall_mean_per_case','invalid_outputs','unresolvable_cited_fact_ids']}
        for arm,score in arms.items()} for domain,arms in scores.items()}),indent=2))
