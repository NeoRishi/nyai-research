# MATS Winter 2027 Work Sample Guide (`nyai-research`)

## Core research question

**Can a host-anchored multi-hop assurance graph (`AssuranceDAG`) with correlated-warrant cuts and causal-slice pruning catch multi-step stale claims ("zombie claims"), shared-dependency failures, and semantic reward hacks that conventional 1-hop runtime checks miss — while compressing the trace a human overseer or statutory auditor must inspect by ~80%?**

## Why this work sample is structured as four progressive studies

This repository documents a progression across four studies, with 23 unit tests and offline replay of stored results. Runtime depends on the host:

1. **Study 1 (`scripts/run_pilot.py`) — Synthetic audit prompts and action contracts:** On 120 policy cases, ordinary, checklist and structured prompts match 96, 92 and 84 unreviewed template labels. A separate 24-case action-contract comparison gives both the API model and executable contract 24/24 oracle matches. No incremental benefit is demonstrated; protocols and raw outputs are retained.
2. **Study 2 (`scripts/evaluate_graphrag144.py`) — Controlled GraphRAG evaluation (144 cases):** Full reference, vector RAG, GraphRAG and structured GraphRAG match 96/120, 63/120, 71/120 and 61/120 policy templates, and 24/24, 18/24, 24/24 and 24/24 contract decisions. Retrieval uses an isolated reference graph. These results do not establish independent warrant paths or general safety gains; see [the recorded results](graphrag-evaluation-results.md).
3. **Study 3 (`scripts/run_runtime_revision.py`) — Observed runtime evidence (12 trajectories / 24 decision points):** Runs real subprocesses and binds observations to SHA-256 file hashes. Both the observed contract and conventional revalidation match 24/24 design decisions; synthetic self-report matches 16/24. This exposes an equivalence boundary for single-file checks.
4. **Study 4 (`scripts/run_assurance_dag.py`) — Host-Anchored Multi-Hop Assurance DAG & Causal-Slice Oversight Compression (16 trajectories / 32 decision points):** Tests multi-hop and shared-warrant mechanisms motivated by the earlier studies in one architecture (`src/nyai_research/assurance_dag.py`):
   - **Separates the configured baselines (`32/32` vs `23/32`):** Conventional 1-hop revalidation catches `3/3` depth-1 failures (`T01–T03`) but **0/4 multi-hop zombie claims** (`T04–T07`) and **0/3 correlated-warrant collapses** (`T08–T10`). This baseline checks top-level current hashes against stored execution observations; it does not rerun every dependency at each decision.
   - **Demonstrates Stage-1 vs Stage-2 honesty (`30/32` vs `32/32`):** Stage-1 structural DAG (`nyai_assurance_dag_structural`) catches all 10 structural/dependency invalidations (`30/32`, `93.8%`) with `0` false alarms on valid refactors (`T13–T16`), but misses `2/2` pure semantic reward hacks (`T11–T12`) where hashes and exit codes remain clean (`assert True`). Adding the Stage-2 Causal-Slice AST inspector (`nyai_assurance_dag_hybrid`) catches `2/2` semantic hacks (`32/32`, `100.0%`) while running only on the pruned causal slice.
   - **Compresses recorded logs (`79.49%` step reduction, `85.53%` token reduction):** Prunes exploratory log steps (`T14`), avoiding the false alarm triggered by the configured windowed transcript heuristic (`21/32`, `65.6%`). Tokens are whitespace-separated log words, not model tokenizer counts. Human review effort has not been measured. Decisions include machine-readable EU AI Act research mappings and contestability records (`results/assurance_dag_v1/records.jsonl`).

## Offline verification path for reviewers

```bash
python3 scripts/run_assurance_dag.py
python3 -m unittest discover -s tests -v
python3 scripts/verify_artifacts.py
python3 scripts/verify_agentic.py
python3 scripts/verify_graphrag144.py
```

## Key files to inspect first

- `src/nyai_research/assurance_dag.py` — Multi-hop `AssuranceDAG`, AST import extractor, correlated-warrant cut detector, Stage-2 semantic AST inspector, causal-slice pruner, and EU AI Act contestability record builder.
- `docs/assurance-dag-study.md` — Full study design, failure taxonomy, baseline comparison table, and scope limitations.
- `docs/eu-ai-act-relevance.md` — Technical mapping to EU AI Act Articles 12, 13, 14, 15, 53/55, 72, and 86 + GPAI Code of Practice Appendix 3.5.
- `results/assurance_dag_v1/summary.json` & `results/assurance_dag_v1/review_queue.csv` — Machine-readable evaluation summary and compressed human-oversight queue.

All Study 4 cases are constructed and correlated. Claim links are configured; the shared-warrant check is a limited overlap heuristic. See [measurement and implementation boundaries](assurance-dag-study.md#measurement-and-implementation-boundaries) for the trust model and baseline limits.
