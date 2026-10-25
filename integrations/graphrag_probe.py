"""Read-only probe using the EXISTING GraphRAG Neo4j pipeline.
Requires ../vedic-graphrag with its local .env; reads only. Never writes Neo4j.
"""
import argparse,sys,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('question');p.add_argument('--repo',default='../vedic-graphrag');p.add_argument('--dosha');p.add_argument('--module');a=p.parse_args()
root=Path(a.repo).resolve()
if not (root/'ask.py').exists():raise SystemExit('Missing Vedic GraphRAG repo: '+str(root))
sys.path.insert(0,str(root))
from kb_common import load_env,connect_neo4j,openai_client,embed
from ask import plain_rag,graph_rag,build_context
settings=load_env();client=openai_client(settings);driver,db=connect_neo4j(settings)
try:
 v=embed(client,[a.question])[0]
 with driver.session(database=db) as s:
  plain,_=plain_rag(s,v)
  graph,exp=graph_rag(s,v,a.dosha,a.module)
 for mode,rows in [('plain',plain),('graph',graph)]:
  print(json.dumps({'mode':mode,'n':len(rows),'passage_ids':[x['id'] for x in rows],
    'source_slugs':[x['slug'] for x in rows]},indent=2))
 print('Graph expanded sources:',[x.get('sources') for x in exp])
finally:driver.close()
