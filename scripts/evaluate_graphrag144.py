"""Prepare/import/retrieve/score a namespaced actual-Neo4j 144-case RAG experiment.

No private wellness passages are exported. The source graph contains only reference
policy excerpts already used in synthetic fixtures and the fictional action contract.
Import is additive/idempotent; no original Note/Chunk/Source nodes are changed.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'vendor/graphrag'))
from nyai_research.rag_benchmark import ARMS, BASE, STRUCTURED, sources_from_registries, queries_and_cases, render_facts, model_payload, sha
from import_wiki import read_env
import ask

OUT = ROOT / 'experiments/graphrag_144_v1'
RESULTS = ROOT / 'results/graphrag_144_v1'
CACHE = ROOT / 'private_audit/graphrag_144_v1'
NS = 'nyai_eval_20261026_v1'
INDEX = 'nyai_eval_20261026_embedding'
NOTE = 'NyAIEvalNote20261026'
CHUNK = 'NyAIEvalChunk20261026'
SOURCE = 'NyAIEvalSource20261026'


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def prepare():
    if (OUT / 'protocol.json').exists():
        raise SystemExit('Protocol exists; preserve this version')
    p = json.loads((ROOT / 'data/fixtures/vcim_policy_registry.json').read_text())['rows']
    e = json.loads((ROOT / 'data/fixtures/vcim_epistemics_registry.json').read_text())['rows']
    sources = sources_from_registries(p, e)
    cases = queries_and_cases(read_rows(ROOT / 'data/fixtures/120_synthetic_cases.jsonl'),
                              read_rows(ROOT / 'data/fixtures/24_agentic_contract_cases.jsonl'))
    save(OUT / 'sources.json', sources)
    save(OUT / 'cases.json', cases)
    paths = ['src/nyai_research/rag_benchmark.py', 'scripts/evaluate_graphrag144.py',
             'experiments/graphrag_144_v1/sources.json', 'experiments/graphrag_144_v1/cases.json']
    protocol = dict(frozen_at=datetime.now(timezone.utc).isoformat(), status='Local exploratory protocol freeze, not external preregistration',
        namespace=NS, cases=144, strata={'unreviewed_policy_candidates':120, 'synthetic_action_contracts':24},
        source_notes=len(sources), source_facts=sum(len(s['facts']) for s in sources), source_nodes=len(sources),
        namespace_nodes=2*len(sources)+sum(len(s['facts']) for s in sources),
        original_graph_mutation=False, candidate_answers_or_labels_in_graph=False,
        arms=ARMS, model='gpt-6-luna', temperature='provider default 1', max_completion_tokens=1024,
        generation_requests=144*len(ARMS), embedding_model='text-embedding-3-small',
        query_variants=len({c['query'] for c in cases}), retrieval_top_k=6, candidates=30,
        context_max_chars=8000, request_order_seed=20261026,
        algorithm='Unmodified upstream plain_rag/graph_rag selection with an adapter for isolated labels, domain filtering and parent-to-fact expansion',
        fairness='Same cases, model, response budget and context cap. Structured arm reuses exactly the graph_rag evidence. Realised context lengths may differ.',
        metrics=['Reference-fact recall','Reference-source hit rate','Unreviewed template-label agreement (120 only)',
                 'Explicit contract-oracle agreement (24 only)','Invalid outputs','Citation-ID resolution','Tokens and latency','Paired disagreements'],
        inference='Descriptive diagnostic; correlated templates, known source families, no independent human labels or safety claim',
        exclusions='None; errors count as nonmatches; no silent truncation retry',
        privacy='Only fixture-reference excerpts and fictional runtime facts go to model APIs; no private wellness passages',
        hashes={p:sha((ROOT/p).read_text()) for p in paths})
    save(OUT / 'protocol.json', protocol)
    print(json.dumps(protocol, indent=2))


def connect(env):
    from neo4j import GraphDatabase
    if '8ed83df4' not in env.get('NEO4J_URI', ''):
        raise ValueError('Unexpected Aura instance')
    return GraphDatabase.driver(env['NEO4J_URI'], auth=(env['NEO4J_USERNAME'], env['NEO4J_PASSWORD']), connection_timeout=15)


def coverage(env):
    sources = json.loads((OUT/'sources.json').read_text())
    rows = []
    with connect(env) as driver, driver.session(database=env.get('NEO4J_DATABASE', 'neo4j'), default_access_mode='READ') as session:
        for s in sources:
            needle = s['source_id'] if s['domain'] == 'policy_audit' else 'synthetic_action_contract_v1'
            count = session.run('MATCH (n:Note) WHERE toLower(coalesce(n.content,"")) CONTAINS toLower($needle) RETURN count(n) AS n', needle=needle).single()['n']
            rows.append(dict(source_id=s['source_id'], exact_reference_id_matches=count))
    result = dict(scope='Original Note corpus only; no benchmark namespace nodes', reference_id_coverage=rows,
        limitation='Zero ID matches are a coverage screen, not proof no semantically related passage exists.', database_writes=False)
    save(RESULTS/'original_graph_coverage.json', result)
    print(json.dumps(result, indent=2))


def embedding_cache(env):
    from openai import OpenAI
    sources = json.loads((OUT/'sources.json').read_text())
    cases = json.loads((OUT/'cases.json').read_text())
    texts = {f['fact_id']: s['title'] + ': ' + f['text'] for s in sources for f in s['facts']}
    texts.update({'Q.' + sha(c['query']): c['query'] for c in cases})
    path = CACHE/'embeddings.json'
    if path.exists():
        data = json.loads(path.read_text())
        if data['texts_sha256'] != sha(texts):
            raise ValueError('Embedding cache input mismatch')
        return data['vectors']
    ids = sorted(texts)
    response = OpenAI(api_key=env['OPENAI_API_KEY'], timeout=60, max_retries=1).embeddings.create(
        model='text-embedding-3-small', input=[texts[i] for i in ids])
    vectors = {ids[row.index]: row.embedding for row in response.data}
    save(path, dict(texts_sha256=sha(texts), vectors=vectors, usage=response.usage.model_dump()))
    save(RESULTS/'embedding_usage.json', dict(model=response.model, inputs=len(ids), usage=response.usage.model_dump()))
    return vectors


def import_graph(env):
    sources = json.loads((OUT/'sources.json').read_text())
    vectors = embedding_cache(env)
    with connect(env) as driver, driver.session(database=env.get('NEO4J_DATABASE', 'neo4j')) as session:
        before = session.run('MATCH (n:Note) RETURN count(n) AS n').single()['n']
        for label in [NOTE, CHUNK, SOURCE]:
            session.run(f'CREATE CONSTRAINT {label}_uid IF NOT EXISTS FOR (n:{label}) REQUIRE n.uid IS UNIQUE').consume()
        existing = list(session.run(f'MATCH (n:{NOTE}) WHERE n.namespace=$ns RETURN n.source_id AS id,n.content_hash AS hash', ns=NS))
        expected = {s['source_id']:sha(s) for s in sources}
        if any(expected.get(r['id']) != r['hash'] for r in existing):
            raise ValueError('Existing source bytes differ; refusing to overwrite')
        writes = 0
        for s in sources:
            q = f'''MERGE (n:{NOTE} {{uid:$uid}}) ON CREATE SET n.namespace=$ns,n.source_id=$id,n.title=$title,n.domain=$domain,n.content_hash=$hash
MERGE (p:{SOURCE} {{uid:$source_uid}}) ON CREATE SET p.namespace=$ns,p.reference=$reference
MERGE (n)-[:NYAI_EVAL_CITES]->(p)
WITH n UNWIND $facts AS f
MERGE (c:{CHUNK} {{uid:f.uid}}) ON CREATE SET c.namespace=$ns,c.fact_id=f.fact_id,c.text=f.text,c.domain=$domain,c.embedding=f.embedding
MERGE (n)-[:NYAI_EVAL_HAS_CHUNK]->(c)'''
            facts = [dict(**f, uid=NS+'.'+f['fact_id'], embedding=vectors[f['fact_id']]) for f in s['facts']]
            result = session.run(q, uid=NS+'.'+s['source_id'], source_uid=NS+'.source.'+s['source_id'],
                ns=NS, id=s['source_id'], title=s['title'], domain=s['domain'], hash=sha(s), reference=s['reference'], facts=facts)
            writes += result.consume().counters.nodes_created
        session.run(f'''CREATE VECTOR INDEX {INDEX} IF NOT EXISTS FOR (c:{CHUNK}) ON (c.embedding)
OPTIONS {{indexConfig: {{`vector.dimensions`:1536, `vector.similarity_function`:'cosine'}}}}''').consume()
        session.run('CALL db.awaitIndex($name,120)', name=INDEX).consume()
        after = session.run('MATCH (n:Note) RETURN count(n) AS n').single()['n']
        count = session.run(f'MATCH (n) WHERE n.namespace=$ns AND (n:{NOTE} OR n:{CHUNK} OR n:{SOURCE}) RETURN count(n) AS n', ns=NS).single()['n']
    assert before == after, 'Original Note count changed'
    assert count == 86, 'Unexpected evaluation namespace size'
    save(RESULTS/'graph_import.json', dict(namespace=NS, created_nodes=writes, namespace_nodes=count,
        original_notes_before=before, original_notes_after=after, original_labels_modified=False, index=INDEX))
    print('Benchmark graph ready:',count,'isolated nodes; original Notes unchanged:',after)


class AdaptedSession:
    def __init__(self, session, domain):
        self.session, self.domain = session, domain

    def run(self, query, **parameters):
        if query == ask.VECTOR_Q:
            q = f'''CALL db.index.vector.queryNodes($index,48,$vec) YIELD node AS c,score
MATCH (n:{NOTE})-[:NYAI_EVAL_HAS_CHUNK]->(c)
WHERE c.namespace=$ns AND c.domain=$domain
RETURN c.fact_id AS id,c.fact_id AS heading,c.text AS text,score,n.source_id AS slug,n.title AS title,[] AS doshas,[] AS modules
ORDER BY score DESC,c.fact_id LIMIT $k'''
            return self.session.run(q, index=INDEX, ns=NS, domain=self.domain, **parameters)
        if query == ask.EXPAND_Q:
            q = f'''UNWIND $slugs AS slug MATCH (n:{NOTE} {{namespace:$ns,source_id:slug}})-[:NYAI_EVAL_HAS_CHUNK]->(c:{CHUNK})
WITH n,c ORDER BY c.fact_id
RETURN n.source_id AS slug,n.title AS title,collect({{fact_id:c.fact_id,title:c.fact_id,summary:c.text}}) AS related,
[] AS sources,'' AS content'''
            return self.session.run(q, ns=NS, **parameters)
        raise ValueError('Unexpected upstream query')


def retrieve(env):
    sources = json.loads((OUT/'sources.json').read_text())
    facts_by_id = {f['fact_id']:dict(**f, source_id=s['source_id']) for s in sources for f in s['facts']}
    vectors = embedding_cache(env)
    cases = json.loads((OUT/'cases.json').read_text())
    cached = {}
    with connect(env) as driver, driver.session(database=env.get('NEO4J_DATABASE','neo4j'), default_access_mode='READ') as session:
        for c in cases:
            key = sha(c['query'])
            if key in cached:
                continue
            adapter = AdaptedSession(session, c['domain'])
            vector = vectors['Q.'+key]
            plain, _ = ask.plain_rag(adapter, vector)
            graph, expansion = ask.graph_rag(adapter, vector, None, None)
            for passage in plain + graph:
                frozen=facts_by_id[passage['id']]
                assert passage['text']==frozen['text'] and passage['slug']==frozen['source_id'], 'Neo4j passage snapshot mismatch'
            for expanded in expansion:
                for related in expanded['related']:
                    frozen=facts_by_id[related['fact_id']]
                    assert related['summary']==frozen['text'] and expanded['slug']==frozen['source_id'], 'Neo4j expansion snapshot mismatch'
            raw_graph_ids = [p['id'] for p in graph] + [r['fact_id'] for e in expansion for r in e['related']]
            cached[key] = dict(vector_rag=render_facts([facts_by_id[p['id']] for p in plain]),
                               graph_rag=render_facts([facts_by_id[i] for i in raw_graph_ids]))
    output = []
    for c in cases:
        context = cached[sha(c['query'])]
        full = render_facts([f for f in facts_by_id.values() if f['source_id'] == c['target_source_id']])
        for arm in ARMS:
            facts = full if arm == 'full_reference' else context['graph_rag' if arm.endswith('structured') else arm]
            output.append(dict(case_id=c['case_id'], arm=arm, facts=facts, context_sha256=sha(facts),
                target_fact_recall=len(set(c['target_fact_ids']) & {f['fact_id'] for f in facts})/len(c['target_fact_ids']),
                target_source_hit=any(f['source_id']==c['target_source_id'] for f in facts)))
    save(OUT/'retrieved_contexts.json',output)
    print('Actual Neo4j contexts recorded:',len(output),'over',len(cached),'unique query vectors')


def request(client, model, case, context):
    payload = model_payload(case, context['facts'])
    prompt = STRUCTURED if context['arm'] == 'graph_rag_structured' else BASE
    messages = [dict(role='system',content=prompt),dict(role='user',content=json.dumps(payload,ensure_ascii=False))]
    row = dict(case_id=case['case_id'], arm=context['arm'], domain=case['domain'],
        messages=messages, prompt_sha256=sha(prompt), payload_sha256=sha(payload),
        context_sha256=context['context_sha256'], requested_model=model,
        started_at=datetime.now(timezone.utc).isoformat())
    start=time.monotonic()
    try:
        r=client.chat.completions.create(model=model,messages=messages,max_completion_tokens=1024,response_format={'type':'json_object'})
        row.update(response_id=r.id, returned_model=r.model, usage=r.usage.model_dump(), raw_text=r.choices[0].message.content,
                   finish_reason=r.choices[0].finish_reason)
        parsed=json.loads(row['raw_text'])
        if case['domain']=='policy_audit':
            if parsed.get('label') not in {'compliant','violation','insufficient'}:raise ValueError('Invalid label')
        elif type(parsed.get('execute')) is not bool or parsed.get('action') != case['state']['action']:
            raise ValueError('Invalid action decision')
        if not isinstance(parsed.get('cited_fact_ids'),list):raise ValueError('Missing citation list')
        row['parsed']=parsed
    except Exception as e:
        row.update(error_type=type(e).__name__,status_code=getattr(e,'status_code',None))
    row['latency_seconds']=round(time.monotonic()-start,4)
    return row


def run(env):
    from openai import OpenAI
    cases={c['case_id']:c for c in json.loads((OUT/'cases.json').read_text())}
    contexts=json.loads((OUT/'retrieved_contexts.json').read_text())
    path=RESULTS/'model_responses.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
    existing=read_rows(path) if path.exists() else []
    done={(r['case_id'],r['arm']) for r in existing}
    todo=[c for c in contexts if (c['case_id'],c['arm']) not in done]
    random.Random(20261026).shuffle(todo)
    client=OpenAI(api_key=env['OPENAI_API_KEY'],timeout=75,max_retries=1)
    assert env.get('OPENAI_CHAT_MODEL','gpt-6-luna')=='gpt-6-luna', 'Configured model differs from frozen protocol'
    print('Model requests remaining:',len(todo),flush=True)
    # Confirm provider settings on one actual task before queueing the batch.
    with path.open('a') as output:
        if todo:
            first=todo.pop(0);row=request(client,env.get('OPENAI_CHAT_MODEL','gpt-6-luna'),cases[first['case_id']],first)
            output.write(json.dumps(row,ensure_ascii=False)+'\n');output.flush()
            if row.get('status_code'):raise SystemExit('API configuration failed; inspect before continuing')
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(request,client,env.get('OPENAI_CHAT_MODEL','gpt-6-luna'),cases[c['case_id']],c) for c in todo]
            for i,f in enumerate(as_completed(futures),1):
                output.write(json.dumps(f.result(),ensure_ascii=False)+'\n');output.flush()
                if i%24==0 or i==len(futures):print(i+1,'requests recorded in this run',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['prepare','coverage','import','retrieve','run'])
    p.add_argument('--env',type=Path);a=p.parse_args()
    if a.phase=='prepare':prepare()
    else:
        if not a.env:p.error('--env is required')
        env=read_env(a.env)
        {'coverage':coverage,'import':import_graph,'retrieve':retrieve,'run':run}[a.phase](env)
