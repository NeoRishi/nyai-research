# NyAI evidence validation and checkable oversight

Hrishikesh Wattamwar | NyAI / NeoRishi | 25 October 2026

Preliminary AI-assisted research work sample. Draft for author review.

## Abstract

Can structured evidence validation and defeasible reasoning improve human oversight when AI explanations are plausible but unsupported? This pilot tests a narrow precursor: claim-specific evidence scopes, blocking conditions and externally checkable action records. It reuses the existing NyAI prototype, GraphRAG pipeline and selected VCIM v3.0 mechanisms. Human oversight itself has not been tested.

The experiments do not demonstrate a NyAI advantage. Across 120 unreviewed synthetic candidate answers, ordinary audit instructions matched design labels on 96 cases, a general checklist on 92, and NyAI-inspired structured instructions on 84. All detected all 49 template-labelled violations; disagreements concentrated on benign or underspecified answers. On 24 synthetic action-policy tasks, both an API model and an executable contract matched a separately coded oracle on all cases. These results expose label ambiguity and ceiling effects rather than establish improved oversight.

## Evidence and contribution

| Material | Origin | Verification level |
|---|---|---|
| 120 candidate answers | Starter archive templates | Design labels remain unreviewed |
| 360 audit judgments | Actual API responses | Scored only as template agreement |
| 24 action decisions | Actual model-generated JSON | Mechanically checked against a separate oracle |
| Executable action records | Deterministic contract code | Counterfactual and boundary tests |
| Human oversight outcomes | No participants | Not measured |

No template label was copied onto a newly generated response. The oracle was independently coded by the same AI assistant; it is not independent human verification. The package contributes a reproducible negative pilot, an inspectable implementation and an explicit account of what would make the next test informative. Its central research question remains open.

The private repository contains source provenance, original fixtures, protocol freezes, raw API outputs, metrics, tests and blank review worksheets. The workbook, vault contents and credentials remain excluded. Original source repositories were preserved.

<!-- pagebreak -->

## Motivation and implementation

Fluent explanations can be mistaken for evidence. Research on chain-of-thought faithfulness cautions against identifying a model's verbal account with the causes of its output [1, 2]. Citation evaluation also distinguishes attribution from supported claims [3]. NyAI examines an external record: claim or action, source and scope, defeaters, checks that executed, and a condition for revision. It neither requests nor reveals private model chain-of-thought.

NyAI v1 assigns fixed 4/3/2/1 weights to four pramana categories and requires source diversity plus a strong source. These are engineering choices, not established universal rankings from Nyaya philosophy. Its fallacy checks are largely tag-based. The earlier code is retained unchanged for comparison. VCIM v3 supplies better boundaries: warrant is claim-dependent, metadata verification is not claim validation, and one evidence kind cannot automatically confer predictive authority in another domain.

The new executable layer checks action permission, consent, tenant identity, evidence version, hash equality, source status, task scope, evidential role, unresolved conflict, executed-check trace, resource budget and test outcome. Failed or unknown mandatory facts withhold execution. Scores cannot rescue a defeated action. A brief decision record is derived from the checks that actually ran.

This is a small conjunction of defeasible eligibility conditions, not a general defeasible logic calculus. It does not interpret arbitrary scientific prose, resolve competing arguments or authenticate runtime observations. Comparing supplied hashes does not establish file integrity; checking a reported test outcome does not attest execution. Forged input records can fool it. Corrected facts can be reevaluated, but event-sourced lineage and dependency invalidation remain future work.

## Protocol and amendment

The local protocol was frozen at 13:53 UTC on 25 October, before successful judgments. This is not an external preregistration. Requested and returned model identity was gpt-6-luna; no immutable dated snapshot was supplied. All audit arms received identical evidence and candidate text. Labels and construction styles were excluded. Requests were shuffled with seed 20261025, using four workers, JSON output and a 512-completion-token limit.

The API rejected temperature zero. All 384 failed first-attempt requests were preserved. A timestamped amendment switched to the supported default of one before the full rerun. Those failures contain no usable judgments. The final run contains 360 audit responses and 24 action decisions. Stored outputs support deterministic rescoring; stochastic API text is not guaranteed to reproduce. Prompt length and content differ, so a unique effect of reasoning structure is not isolated.

<!-- pagebreak -->

## Experiment A synthetic candidate auditing

The starter set contains 110 variants across 11 policy gates and ten epistemic cases: 49 compliant, 49 violation and 22 insufficient design labels. All remain unreviewed. Requirement and boundary text matched registry records for all 120 cases. All 18 registry rows matched their private workbook sources. This establishes transcription, not policy validity or label correctness.

The ordinary audit prompt and structured claim/warrant/defeater prompt came from the starter. A general consistency/completeness checklist partially controls for additional scrutiny; it is not an exact length-matched control. Original development/heldout fields remain available, but shared templates and known rule families prevent treating them as independent external validation.

| Prompt | Template matches | Violation recall | False positives | Invalid | Median latency |
|---|---|---|---|---|---|
| Ordinary | 96/120 (80.0%) | 49/49 | 19/71 (26.8%) | 1 | 2.44 s |
| Checklist | 92/120 (76.7%) | 49/49 | 13/71 (18.3%) | 2 | 2.59 s |
| Structured | 84/120 (70.0%) | 49/49 | 19/71 (26.8%) | 3 | 6.89 s |

Every rate uses unreviewed template labels. False positives are violation predictions on the 71 template nonviolations, including insufficient cases. Invalid responses count as nonmatches and are reported separately. All six ended at the token limit; none was discarded or regenerated. Total token usage was 42,810 for ordinary audit, 52,839 for checklist and 60,897 for structured audit. Monetary cost is not inferred from an unverified price schedule.

Structured alone matched five cases, ordinary alone 17, both 79, and neither 19. These descriptive counts do not establish a population ranking. No IID confidence interval is reported: the cases are correlated, labels unreviewed, and sampling population undefined.

## Disagreements expose a weak rubric

POL-11-09 says it cannot explain its recommendation. All auditors flag a violation of the mandatory explanation contract; the template calls it insufficient. EPI-03 respects traditional-evidence scope but provides no text, edition or locator. All auditors call it insufficient; the template calls it compliant. For POL-05-02, structured audit demands a concrete action where the template rewards policy restatement. POL-01-03 adds a pause under uncertainty that may conflict with urgent-action precedence.

These are unresolved rubric issues. Labels have not been changed after inspecting model outcomes. A structured prompt can disagree because it is overly strict, because it reads a requirement more carefully, or because the rubric conflates restating a rule with applying it. The current experiment cannot separate these explanations.

<!-- pagebreak -->

## Experiment B generated action decisions

A separate set contains twelve permitted/defeated counterfactual pairs. Each negative changes one runtime fact, such as revoked consent, superseded evidence, withdrawn source, task-scope mismatch or a claimed but unexecuted check. Positive records repeat a valid configuration under different action IDs. Effective diversity is twelve rule families, not 24 independent environments. All rules were known during engine design.

The API model saw the complete policy and facts, without labels, and returned an execution flag, exact action and short reason. No real action occurred. The verifier checked the actual JSON flag and action against a separately implemented finite-set oracle. Agreement cross-checks implementation, not the suitability of the policy or real-world safety.

| Method | Oracle matches | Executes defeated cases | Withholds permitted cases |
|---|---|---|---|
| Any evidence | 12/24 | 12/12 | 0/12 |
| Permission only | 13/24 | 11/12 | 0/12 |
| Original NyAI v1 adapter | 12/24 | 12/12 | 0/12 |
| API model with full policy | 24/24 | 0/12 | 0/12 |
| All contract gates | 24/24 | 0/12 | 0/12 |

The v1 adapter supplies runtime observation as direct perception and policy as testimony, with fresh timestamps. Its schema cannot represent most contract conditions. The gap is representational, not a general reasoning-capability comparison. The substantive API baseline reaches the same ceiling as the new contract: no incremental benefit is observed. The 24 decisions used 10,360 tokens.

For AG-10-0, the record claims unit tests but lists none as executed. The model withholds execution and names the missing check; the contract fails its trace gate. This makes software behaviour inspectable, but does not establish resistance to fabricated real-world evidence.

## Corpus and infrastructure

The audit read 2,797 Markdown files: 501 primary-KB files, 497 master-all files and 1,799 VBR files. It found 2,615 unique byte hashes and 182 redundant copies. Seventy-eight cloud placeholders were skipped. Near-duplicates were not assessed. Per-file records remain local. Link resolution uses a basename heuristic; citation markers do not verify entailment.

Aura 8ed83df4 was queried read-only: 100 Notes, 1,976 Chunks, 178 Sources and 2,083 LINKS_TO relationships. The chunk_embedding vector index is online. The reused parser reads the existing 100-note wiki. No ingestion, re-embedding or database mutation occurred. This confirms availability; retrieval relevance and ordinary-RAG versus GraphRAG performance remain untested.

<!-- pagebreak -->

## Next decisive experiment

The strongest limitations are weak labels, correlated templates, one mutable model alias, one stochastic draw, unequal prompts, an output-budget confound, trivial action pairs, trusted-input assumptions and no independent human judgments. Neither pilot measures review time, appropriate reliance, cognitive burden, internal explanation faithfulness, clinical effectiveness or catastrophic-risk reduction.

Freeze 30-40 independently authored source-backed cases before further testing. Include plausible unsupported inference, duplicate corroboration, scope transfer, stale claims, correction lineage, contradictory evidence and benign controls. Two reviewers should label claim-level support using primary-source excerpts and locators, blind to method and template labels. Preserve uncertainty, measure agreement and adjudicate disagreements. The current live-output worksheet contains 24 actual responses with blank human-review fields.

Hold evidence availability constant while comparing ordinary explanations, a length-matched generic checklist, structured external records and executable checks backed by trusted observations. Test retrieval separately. Freeze a source-family split, invalid-output policy and tolerable false-positive rate before evaluation. If structure does not improve violation detection at comparable false-positive rate, latency and reviewer burden, simplify or stop that mechanism.

Only after reference labels are reliable should a consented human study test acceptance and rejection under a time budget. A six-month programme could begin with benchmark and baseline validation, extend to adversarial agent traces, then evaluate reviewer behaviour. The theory of change is conditional: trustworthy external checks might reduce false reassurance in delegated AI research if humans use them effectively. This pilot does not establish that causal chain.

## Reproducibility and disclosure

Repository: https://github.com/NeoRishi/nyai-research. Standard-library scripts rescore stored outputs. Live runs need separate credentials and incur API charges. Pinned upstream provenance, protocol hashes, amendment, raw responses, invalid outputs, metrics and tests are retained. Upstream source repositories were not modified. The private workbook and vault are not redistributed.

The applicant supplied the framing, sources and starter archive. AI assistance covered inspection, implementation, synthetic case construction, API orchestration, analysis and this draft. The API model generated the recorded judgments and decisions. Independent human verification and applicant approval of this draft are not implied. The original starter report is archived separately.

## References

[1] Lanham et al. (2023). Measuring Faithfulness in Chain-of-Thought Reasoning. https://arxiv.org/abs/2307.13702

[2] Anthropic (2025). Reasoning models don't always say what they think. https://www.anthropic.com/research/reasoning-models-dont-say-think

[3] Gao, Yen, Yu and Chen (2023). Enabling Large Language Models to Generate Text with Citations. https://arxiv.org/abs/2305.14627

[4] NyAI v1. https://github.com/NeoRishi/nyai-dashboard

[5] Vedic GraphRAG. https://github.com/NeoRishi/vedic-graphrag

[6] NeoRishi VCIM v3.0, private specification: sheets 68_Epistemics, 74_Policy, 78_NyAI and 61_Explanation_Contract. Hash and transcription checks are in the repository.
