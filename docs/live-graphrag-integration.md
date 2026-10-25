# Live GraphRAG and NyAI integration

## Correction to the earlier scope

Before this integration, Aura had only been inspected for connectivity, counts and schema. GraphRAG parsing helpers had been reused, but the 120-case prompt pilot and 24-case action-contract study did not retrieve from Neo4j. Their results remain unchanged and must not be described as GraphRAG results. The earlier work sample describes that historical scope accurately.

The applicant requested actual reuse of both systems. `integrations/graph_nyai.py` now runs a live, read-only evidence path:

1. Embed a generic query using the upstream embedding helper, or use a stored chunk vector as a diagnostic seed.
2. Run the upstream plain-RAG and GraphRAG vector retrieval functions against the existing Aura instance.
3. For GraphRAG, apply the original reranking/diversity logic and expand selected notes through graph links and CITES relationships.
4. Construct context using the upstream formatter, keeping private content local.
5. Pass the actual retrieved passages to the original NyAI v1 engine as testimony and audit their citation/provenance structure separately.
6. Derive a brief external decision record, retaining unknown semantic warrants rather than treating citation presence as claim truth.

The constructed probe claim is that retrieved passages suffice to validate an answer. It is explicitly not a newly generated AI answer. No answer-generation API is called. This adapter does not yet evaluate a model answer against independently reviewed source evidence.

## Recorded live query run

The run at 17:37 UTC on 25 October 2026 used a generic query about evidence and warranted inference. Its aggregate record is `results/graph_nyai_integration.json`; private passages, source names and full traces remain in ignored `private_audit/` files.

| Observation | Plain RAG | GraphRAG |
|---|---|---|
| Retrieved passages | 6 | 6 |
| Selected notes | 2 | 4 |
| Maximum passages from one note | 5 | 2 |
| Expanded notes | 0 | 4 |
| Source-file references supplied to this trace | 0 | 12 |
| Original NyAI v1 verdict | uncertain | uncertain |
| Source-lineage check | unknown: expansion not supplied | passed: CITES references provided |
| Entailment, applicability, currentness | unknown | unknown |
| Validated answer permitted | no | no |

Plain RAG's zero supplied source references does not mean those references are absent from the database. That mode does not perform graph expansion. Note-level BRIDGE/CONTRADICTION markers are review cues; their relevance to a particular claim has not been established.

The run executed five graph queries, all with zero update counters. The node count before and after was 2,297. No private passages were sent to a model. The optional query embedding sent only the generic question to the embedding provider. Vector-index calls, graph reranking, expansion and context construction are actual reused upstream code, not mock outputs.

## Why the database does not visibly change

Retrieving evidence reads existing nodes and relationships. It does not require importing notes again or writing research cases into the source graph. Re-running the upstream importer or chunk builder simply to create visible changes would be unnecessary and could change the populated graph. This integration keeps research outputs in versioned files and private traces locally. A later decision to persist research runs in separate graph labels would require a specific storage design, not a cosmetic write.

## Run it

Install the recorded live dependencies in a local environment, then use your existing credentials file:

```bash
python3 integrations/graph_nyai.py --env /path/to/local.env \
  --query "How does Nyaya distinguish evidence sources and warranted inference?"
```

For a diagnostic using an existing embedded note, without any embedding or generation API:

```bash
python3 integrations/graph_nyai.py --env /path/to/local.env --seed-note YOUR_NOTE_SLUG
```

`--dosha` and `--module` expose the upstream retrieval filters/boosts. They are heuristic retrieval inputs, not clinically validated personalization. The graph instance is checked before connecting. The adapter rejects mutation statements and records query update counters. Credentials, raw passages and source identities are not written to the aggregate result.

## Interpretation and next validation

The original NyAI engine receives testimony only. It does not get an invented second evidence type to pass its source-diversity gate. Its uncertain verdict is a real result of that mapping, not a general quality score for the graph. The new provenance audit checks resolvable passage labels, distinct chunk IDs, locators and supplied source lineage. It does not authenticate raw sources, establish semantic entailment or resolve all contrary evidence.

This is a live integration diagnostic. A meaningful retrieval/answer comparison still requires frozen questions, reviewed relevant sources, actual candidate answers and independent claim-level judgments. The public 24-case replay package does not reproduce private-corpus retrieval, and its allowlist has not been expanded to export private content.
