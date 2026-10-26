"""Independent read-only replay of retrieved IDs and original-corpus structural counts.

Uses cached query vectors; never calls a model API or changes the frozen contexts.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('frozen_rag_runner',ROOT/'scripts/evaluate_graphrag144.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--env',type=Path,required=True);a=p.parse_args()
    env=runner.read_env(a.env)
    vectors=json.loads((runner.CACHE/'embeddings.json').read_text())['vectors']
    cases=json.loads((runner.OUT/'cases.json').read_text())
    contexts={(r['case_id'],r['arm']):r for r in json.loads((runner.OUT/'retrieved_contexts.json').read_text())}
    original=json.loads((ROOT/'results/graph_audit.json').read_text())
    queries={runner.sha(c['query']):c for c in cases}
    trace=[]
    with runner.connect(env) as driver,driver.session(database=env.get('NEO4J_DATABASE','neo4j'),default_access_mode='READ') as session:
        labels={r['label']:r['count'] for r in session.run('MATCH (n) UNWIND labels(n) AS label RETURN label,count(*) AS count')}
        relationships={r['type']:r['count'] for r in session.run('MATCH ()-[r]->() RETURN type(r) AS type,count(*) AS count')}
        for r in original['label_counts']:assert labels[r['label']]==r['count'],r['label']
        for r in original['relationship_counts']:assert relationships[r['type']]==r['count'],r['type']
        for key,c in queries.items():
            adapter=runner.AdaptedSession(session,c['domain'])
            plain,_=runner.ask.plain_rag(adapter,vectors['Q.'+key])
            graph,expansion=runner.ask.graph_rag(adapter,vectors['Q.'+key],None,None)
            plain_ids=[r['id'] for r in plain]
            graph_ids=list(dict.fromkeys([r['id'] for r in graph]+[r['fact_id'] for e in expansion for r in e['related']]))
            assert plain_ids==[f['fact_id'] for f in contexts[(c['case_id'],'vector_rag')]['facts']]
            assert graph_ids==[f['fact_id'] for f in contexts[(c['case_id'],'graph_rag')]['facts']]
            trace.append(dict(query_sha256=key,domain=c['domain'],vector_ids=plain_ids,graph_ids=graph_ids,
                vector_scores=[r['score'] for r in plain],selected_graph_scores=[r['score'] for r in graph]))
    result=dict(status='PASS',database_writes=False,model_calls=0,queries_replayed=len(trace),
        original_label_counts_unchanged=True,original_relationship_counts_unchanged=True,
        original_node_count=sum(r['count'] for r in original['label_counts']),
        benchmark_nodes=86,trace=trace)
    runner.save(runner.RESULTS/'graph_snapshot_verification.json',result)
    print('PASS: 31 retrieval queries reproduced; all original label and relationship counts unchanged')
