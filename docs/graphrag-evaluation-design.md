# GraphRAG evaluation of the existing 144 cases

Protocol prepared on 26 October 2026. This document defines the controlled experiment; execution status is determined by its recorded artifacts, not by this design document.

## Why an isolated reference graph is necessary

The 120 policy candidates concern 18 VCIM reference rules; the 24 action decisions concern an explicit synthetic software contract. These are not ordinary questions about the wellness corpus. A read-only check of the original Aura Note corpus found zero exact reference-ID matches for these sources. A local wiki check also found no exact requirement phrases. These are coverage screens, not proof that no related concepts exist.

Scoring unrelated retrieved passages against these labels would mix missing source coverage with reasoning performance. The controlled evaluation therefore uses an additional namespace containing the actual reference policies. It does not claim to evaluate general question answering over the private wellness KB.

## Source graph and privacy boundary

The proposed namespace is `nyai_eval_20261026_v1`, with separate `NyAIEvalNote20261026`, `NyAIEvalChunk20261026` and `NyAIEvalSource20261026` labels. It contains 19 source notes, 48 retrievable policy facts and 19 source-reference nodes: 86 nodes in total. Only reference-policy excerpts and the fictional action contract are included. Candidate responses and design labels are absent from the graph.

Import is additive and idempotent. It does not use the original Note, Chunk or Source labels and does not delete or overwrite the source knowledge graph. The workflow verifies that the original Note count stays unchanged and that the benchmark namespace has the expected size. Source hashes prevent silently replacing existing source notes with different content.

Only the fixture-reference excerpts, generic queries and fictional states are sent to the configured API. No private wellness passages are used or exported. The namespace remains in the private Aura instance; it is not part of the proposed public package.

## Four conditions

| Arm | Evidence and instruction |
|---|---|
| Full reference | Exact reference facts directly provided; a strong evidence-access baseline |
| Vector RAG | Six facts retrieved through the native Neo4j vector index |
| GraphRAG | Original upstream selection/diversity code plus expansion from selected source parents to their linked requirement facts |
| GraphRAG structured audit | Exactly the same retrieved GraphRAG evidence, with a NyAI-inspired warrant/scope/defeater instruction |

The original `ask.plain_rag` and `ask.graph_rag` selection functions are reused without modification. A query adapter targets the isolated labels and domain property, and expands source-parent relationships to their requirement facts. This is a benchmark-specific graph and query adaptation, not an unmodified run over the original wellness graph.

All conditions use the same cases, requested model, 1,024-completion-token budget and 8,000-character context cap. Actual context lengths can differ because expansion exposes more facts; token counts and evidence coverage must be reported. A graph advantage can reflect that extra evidence, not an intrinsically better reasoning process. The fourth arm isolates an instruction change given identical graph evidence; it is a prompt protocol, not a test of the complete production NyAI system.

The source relationships and rule families are known during construction. There is no independent source-family holdout. The 24 cases comprise twelve correlated pairs, with repeated positive configurations. Results are descriptive diagnostics, not generalisation estimates.

## Leakage and outcome handling

Retrieval queries come from scenarios or runtime facts, not candidate answers or expected labels. Irrelevant action-name suffixes are normalized in query construction. All variants reuse the frozen evidence for the same query. Model payloads omit labels, target-source IDs and target-fact sets. Source IDs in returned evidence remain legitimate citation locators.

The corpus is created only from source registries and an explicit contract definition. The 120 source-derived candidates naturally reuse some source language; this is template correlation, not independently authored evaluation data. Labels remain unreviewed. The 24 decisions are checked against a separately implemented oracle written by the same assistant; that is not independent human verification.

The 576 requested model responses are retained, including errors or truncations. Failed outputs count as nonmatches and are not silently retried for better scores. The first actual request is checked for provider configuration errors before the concurrent batch. Prompt, payload, context and source hashes identify the frozen run. A pre-execution amendment adds snapshot consistency, namespace size and model identity assertions without changing the intended arms or data.

## Metrics

- Exact reference-fact recall and source-hit rate within the rendered context. These measure recovery of known source facts, not human-reviewed semantic relevance.
- Agreement with unreviewed design labels for the 120 policy cases, with class-wise errors and invalid-output accounting.
- Agreement with the explicit finite contract for the 24 action decisions, including false execution and false withholding.
- Resolution of cited fact IDs against the actual supplied evidence; this is not a semantic citation-entailment metric.
- Token usage, latency and paired disagreements, with the two case sets reported separately.

No claim of human-oversight improvement, independent scientific validity, statutory compliance or catastrophic-risk reduction follows from this experiment. No IID significance test or confidence interval is justified by these correlated design cases.

## Artifacts and commands

The frozen plan and source snapshots are in `experiments/graphrag_144_v1/`. Coverage and subsequent outputs belong in `results/graphrag_144_v1/`. Embedding caches stay in ignored `private_audit/`.

```bash
# Run only after approval of the namespace import and API experiment:
python scripts/evaluate_graphrag144.py import --env /path/to/local.env
python scripts/evaluate_graphrag144.py retrieve --env /path/to/local.env
python scripts/evaluate_graphrag144.py run --env /path/to/local.env
python scripts/summarize_graphrag144.py
```

The earlier 120/24 pilot results remain unchanged. These new results, once generated and verified, form a distinct retrieval experiment.
