# Research implementation and limits

## Reuse

The new repository retains the starter fixtures and guards, and vendors pinned upstream Python files for reproducible offline reuse. NyAI v1 is evaluated without changing its evidence hierarchy, source count gate, tag rules or seven-day heuristic. This makes the limitations inspectable instead of silently replacing the earlier system. No changes were made to the upstream repositories.

GraphRAG contributes its frontmatter, wikilink, citation and environment parsers. The new corpus audit works recursively and keeps per-file paths/hashes in ignored local storage. The upstream parser itself handles only flat YAML-like frontmatter and a single directory. The existing cloud graph has already been built; rebuilding it is unnecessary for the pilot.

A later live adapter, `integrations/graph_nyai.py`, also reuses the upstream vector retrieval, graph reranking, source expansion and context construction. It passes actual retrieved text through NyAI v1 and a separate provenance check. This was added after the initial pilot; it does not change the synthetic experimental results. See `docs/live-graphrag-integration.md` for actual observations and limits.

## Executable warrant and defeater contract

`src/nyai_research/contracts.py` implements a deliberately small decision layer. Twelve explicit checks constrain an action using supplied runtime facts. Any failed or unknown required fact withholds execution. Resource or preference scores cannot offset a failed gate. A brief decision record is derived from the checks that actually ran, with an explicit condition for reconsidering the decision.

The architecture borrows VCIM's claim-specific scope (68), precedence (74), observed warrants and correction (78), and external explanation contract (61). It does not reproduce the full wellness system. There are no clinical rules, personalised prescriptions or spiritual scores in the new agent-action contract. The fixture's `source_kind == execution_test` requirement is a task-specific policy, not a claim that one source category is universally strongest.

This is a conjunction of defeasible eligibility conditions, not a general defeasible logic calculus or semantic reasoner. Conflict presence withholds rather than weighing competing sources. Corrected facts can be reevaluated; event-sourced lineage and dependency invalidation remain future work. The generated decision record describes software behaviour and is not a model chain-of-thought or a guarantee of internal model faithfulness.

## Known trust boundary

The contract assumes trustworthy structured facts. It compares supplied hashes; it does not read a file to compute or authenticate them. It checks reported test outcomes; it does not execute or cryptographically attest the tests. If a model or attacker can forge every input field, the contract can accept a false record. Production integration would need a trusted observer that independently obtains permissions, versions, hashes and execution outcomes. This pilot does not provide that integration.

## Baseline interpretation

An any-evidence control and v1's source gate are intentionally weak sanity checks. A permission-only gate is a partial ablation. The actual API model sees the complete same policy and facts and is the substantive comparator. Its perfect performance on the 24 simple cases is a ceiling result, not a NyAI improvement. The 120-case comparison tests prompts; it must never be described as a product-vs-model trial.

## Corpus and graph risks

Wikilinks, citations and metadata do not establish entailment or evidence quality. Exact duplicate files can amplify apparent corroboration. Ambiguous basenames can connect the wrong source. Prompt-like text is treated as source content, never as authorization. A full source review, near-duplicate analysis and retrieval-relevance evaluation remain unperformed. The current graph's existence and online vector index establish availability, not benchmark retrieval accuracy.

The upstream importer refreshes relationships and cleans up stubs. `build_chunks.py` can remove chunks not present in its current input. Neither writer was run against Aura. The graph remains unmodified.
