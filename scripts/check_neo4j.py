"""Read-only Aura connection/schema smoke test using local environment variables.
Never logs authentication secrets; does not create/delete graph data.
"""
import os,json,argparse
p=argparse.ArgumentParser();p.add_argument('--database',default=os.getenv('NEO4J_DATABASE','neo4j'));a=p.parse_args()
required=('NEO4J_URI','NEO4J_USERNAME','NEO4J_PASSWORD')
missing=[k for k in required if not os.getenv(k)]
if missing:raise SystemExit('Missing environment variables: '+', '.join(missing))
from neo4j import GraphDatabase
with GraphDatabase.driver(os.environ['NEO4J_URI'],auth=(os.environ['NEO4J_USERNAME'],os.environ['NEO4J_PASSWORD'])) as driver:
 driver.verify_connectivity()
 with driver.session(database=a.database) as session:
  labels=[r['label'] for r in session.run('CALL db.labels() YIELD label RETURN label ORDER BY label')]
  note_count=session.run('MATCH (n:Note) RETURN count(n) AS n').single()['n']
  chunk_count=session.run('MATCH (n:Chunk) RETURN count(n) AS n').single()['n']
  print(json.dumps({'connected':True,'database':a.database,'labels':labels,'notes':note_count,'chunks':chunk_count},indent=2))
