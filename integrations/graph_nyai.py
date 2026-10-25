"""Live Neo4j -> original GraphRAG retrieval -> NyAI v1 + provenance checks.

Only a user-supplied query is sent for embedding when --query is used. No private
passage goes to a model API. --seed-note reuses a stored vector without any API call.
Private text/IDs stay in ignored private_audit/. Stdout is an aggregate summary.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'vendor'))
sys.path.insert(0, str(ROOT / 'vendor/graphrag'))
from import_wiki import read_env
from ask import plain_rag, graph_rag, build_context, flags
from kb_common import embed, openai_client, EMBED_MODEL
from nyai_v1.pramana import Evidence, PramanaType
from nyai_v1.reasoning_agent import NyAIAgent
from nyai_research.graph_warrants import audit_retrieval


class ReadRows(list):
    def single(self):
        if len(self) != 1:
            raise ValueError('Expected one graph result')
        return self[0]


class ObservedReadSession:
    """Consume known read queries and verify their reported update counters."""
    def __init__(self, session):
        self.session = session
        self.observations = []

    def run(self, query, **parameters):
        if re.search(r'\b(CREATE|MERGE|SET|DELETE|DROP|REMOVE|LOAD\s+CSV)\b', query, re.I):
            raise ValueError('Mutation statement prohibited in this integration')
        result = self.session.run(query, **parameters)
        rows = ReadRows(dict(row) for row in result)
        summary = result.consume()
        if summary.counters.contains_updates:
            raise RuntimeError('Unexpected database update reported')
        self.observations.append(dict(query_sha256=hashlib.sha256(query.encode()).hexdigest(),
                                      rows=len(rows), contains_updates=False))
        return rows


def run_mode(name, passages, expansion):
    citations = [f'P{i}' for i in range(1, len(passages) + 1)]
    assessment = audit_retrieval(passages, expansion, citations)
    # Honest v1 mapping: retrieved text is testimony, not a direct observation of
    # scientific efficacy. Do not invent a second evidence kind to pass its gate.
    evidence = [Evidence(content=p['text'], pramana_type=PramanaType.SHABDA,
                         source=p['slug'], timestamp=datetime.now()) for p in passages]
    v1 = NyAIAgent().evaluate_claim(assessment['decision_record']['claim'], evidence)
    note_counts = Counter(p['slug'] for p in passages)
    source_entries = {source for e in expansion for source in e.get('sources', [])}
    cue_counts = {kind: sum(len(flags(e.get('content') or '', kind, limit=10000)) for e in expansion)
                  for kind in ['BRIDGE', 'CONTRADICTION']}
    context = build_context(passages, expansion)
    private = dict(mode=name, passages=passages, expansion=expansion, context=context,
                   constructed_candidate_citations=citations, nyai_v1=v1, provenance_assessment=assessment)
    public = dict(mode=name, passages=len(passages), selected_notes=len(note_counts),
                  max_passages_per_note=max(note_counts.values(), default=0),
                  expanded_notes=len(expansion), provided_source_file_refs=len(source_entries),
                  provided_review_cues=cue_counts,
                  context_sha256=hashlib.sha256(context.encode()).hexdigest(),
                  nyai_v1_verdict=v1['verdict'],
                  provenance_check_statuses={c['rule_id']: c['status'] for c in assessment['checks']},
                  validated_answer_permitted=assessment['validated_answer_permitted'])
    return private, public


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--query', help='Only this query text goes to the embedding provider')
    mode.add_argument('--seed-note', help='Stored-note vector diagnostic; no model API call')
    parser.add_argument('--dosha', choices=['vata', 'pitta', 'kapha'])
    parser.add_argument('--module')
    parser.add_argument('--output', type=Path, help='Optional aggregate JSON path; existing records are never overwritten')
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error('Output already exists; choose a new record path')
    from neo4j import GraphDatabase, READ_ACCESS
    settings = read_env(args.env)
    if '8ed83df4' not in settings.get('NEO4J_URI', ''):
        raise SystemExit('Unexpected Aura instance; no connection attempted')
    vector = None
    if args.query:
        vector = embed(openai_client(settings), [args.query])[0]
    with GraphDatabase.driver(settings['NEO4J_URI'], auth=(settings['NEO4J_USERNAME'], settings['NEO4J_PASSWORD']),
                              connection_timeout=15) as driver:
        driver.verify_connectivity()
        with driver.session(database=settings.get('NEO4J_DATABASE', 'neo4j'), default_access_mode=READ_ACCESS) as actual:
            session = ObservedReadSession(actual)
            before = session.run('MATCH (n) RETURN count(n) AS nodes').single()['nodes']
            if vector is None:
                rows = session.run('MATCH (n:Note {slug: $slug})-[:HAS_CHUNK]->(c:Chunk) '
                                   'WHERE c.embedding IS NOT NULL RETURN c.embedding AS embedding '
                                   'ORDER BY c.id LIMIT 1', slug=args.seed_note)
                if not rows:
                    raise SystemExit('Seed note with an embedding was not found')
                vector = rows[0]['embedding']
            plain, pexp = plain_rag(session, vector)
            graph, gexp = graph_rag(session, vector, args.dosha, args.module)
            after = session.run('MATCH (n) RETURN count(n) AS nodes').single()['nodes']
            observations = session.observations
    private_modes, aggregate_modes = [], []
    for name, passages, expansion in [('plain_rag', plain, pexp), ('graph_rag', graph, gexp)]:
        private, public = run_mode(name, passages, expansion)
        private_modes.append(private)
        aggregate_modes.append(public)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    private_path = ROOT / 'private_audit' / f'graph_nyai_{stamp}.json'
    private_path.parent.mkdir(exist_ok=True)
    private_path.write_text(json.dumps(dict(query=args.query, seed_note=args.seed_note, modes=private_modes), indent=2) + '\n')
    output = dict(run_at=datetime.now(timezone.utc).isoformat(),
                  status='LIVE RETRIEVAL INTEGRATION; NOT A RETRIEVAL-QUALITY OR HUMAN-OVERSIGHT EVALUATION',
                  retrieval_input='query_embedding' if args.query else 'stored_chunk_seed_vector',
                  embedding_model=EMBED_MODEL if args.query else None,
                  query_sha256=hashlib.sha256((args.query or args.seed_note).encode()).hexdigest(),
                  private_passages_sent_to_model=False, generation_api_calls=0,
                  database_writes=False, nodes_before=before, nodes_after=after,
                  executed_query_observations=observations, modes=aggregate_modes,
                  limits=['CITES entries and graph links are provenance, not entailment or source validation.',
                          'BRIDGE/CONTRADICTION markers are unreviewed cues; relevance is not established.',
                          'The candidate sufficiency claim/citations are constructed, not model-generated answers.',
                          'No accuracy gain or end-to-end generated-answer validation is measured.'])
    output_path = args.output or ROOT / 'results/graph_nyai_runs' / f'{stamp}.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))
