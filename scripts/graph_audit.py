"""Read-only schema/count probe. No note text, embeddings, creation or deletion."""
import argparse,datetime,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor/graphrag'))
from import_wiki import read_env,parse_wiki


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--env',type=Path,required=True)
    p.add_argument('--wiki',type=Path);a=p.parse_args()
    from neo4j import GraphDatabase,READ_ACCESS
    e=read_env(a.env)
    assert '8ed83df4' in e['NEO4J_URI']
    out=dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),database_writes=False,instance_id='8ed83df4')
    with GraphDatabase.driver(e['NEO4J_URI'],auth=(e['NEO4J_USERNAME'],e['NEO4J_PASSWORD']),connection_timeout=15) as d:
        d.verify_connectivity()
        with d.session(database=e.get('NEO4J_DATABASE','neo4j'),default_access_mode=READ_ACCESS) as s:
            out['label_counts']=[dict(r) for r in s.run('MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS count ORDER BY label')]
            out['relationship_counts']=[dict(r) for r in s.run('MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count ORDER BY type')]
            out['indexes']=[dict(r) for r in s.run('SHOW INDEXES YIELD name,type,state,populationPercent,labelsOrTypes,properties RETURN name,type,state,populationPercent,labelsOrTypes,properties')]
    if a.wiki:
        notes,index,stubs,unreadable=parse_wiki(a.wiki)
        out['local_wiki_parse']=dict(notes=len(notes),index_nodes=len(index),stubs=len(stubs),
            unreadable=len(unreadable),links=sum(len(n['links']) for n in notes),
            citations=sum(len(n['sources']) for n in notes))
    (ROOT/'results/graph_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
