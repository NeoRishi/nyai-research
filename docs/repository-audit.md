# Repository and source audit

## Completed

| Asset | Observed state and verification |
|---|---|
| NyAI v1 | Commit 5534d4c4985bf74e0ef5e7da64fae8143b9e046b; five API tests passed; all five original scenario verdicts reproduced |
| GraphRAG | Commit a6e0bc7e7b4b90e39b34dd6b192869bd92f9e9ab; parser reused; write paths inspected, not run |
| Starter archive | NyAI_Research_Starter_Fresh.zip found in Downloads; original 120 cases, handoff and review guard retained |
| VCIM | Scaffold source hash matches workbook; 18 registry rows and 120 reference fields checked; four relevant sheets agree with latest copy |
| Primary KB | 579 Markdown files inventoried, 501 read, 78 dataless placeholders skipped |
| All three folders | 2,797 files read; 2,615 unique byte hashes; 182 redundant copies; no raw content uploaded |
| Aura 8ed83df4 | 100 Notes, 1,976 Chunks, 178 Sources, 20 Stubs; vector index online; read-only counts/schema queries |
| API pilot | 360 recorded audit responses and 24 generated action decisions after a documented settings amendment |
| New code | Minimal executable contract, separate finite-set verifier, descriptive scorer, source audit and review packets |

Exact copied vendor bytes are checked against their local pinned upstream checkouts. No LICENSE file was found in either upstream tree. Reuse is private and explicitly requested by the common owner; public redistribution rights must not be inferred.

## Findings that limit interpretation

NyAI v1 uses a fixed source hierarchy, source-count gate, keyword/tag rules and an arbitrary seven-day age threshold. The code does not perform general entailment checking. Some comments assert philosophical correctness that the existing work sample and VCIM v3 appropriately qualify. The new research keeps the original implementation intact as a baseline.

GraphRAG handles citation and wikilink relationships, but the input parser supports only flat frontmatter and a single wiki directory. Whole-note dosha metadata and lexical ambiguity can distort retrieval. No source-relevance or factuality benchmark was run. Its importer refreshes edges and removes orphan stubs; its chunk builder can remove existing chunks absent from the current input. Neither writer was run against populated Aura.

The 120-case dataset is dominated by repeated policy wording and obvious corruptions. Its labels reward policy restatement in some cases while mandatory explanation policies appear to require an actual decision. No independent reviewer has resolved those ambiguities. Both the prompt comparison and 24-case contract experiment have serious construct-validity limits; see the report.

## Remaining dependencies

Independent annotation, independently authored source-backed cases, trusted runtime observers, meaningful retrieval comparisons and human reviewer outcomes remain incomplete. These are research tasks, not missing infrastructure. No new database, hosting service or product UI was added.

The user deferred MATS application logistics, references and CV work until after NyAI. Research results should be reviewed by the applicant before being represented as their submission-ready work.
