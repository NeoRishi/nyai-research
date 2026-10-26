# Pilot evaluation protocol — pre-registration candidate

Current27October update: this file retains the initial pilot protocol as history. GraphRAG StageB has since been executed (`docs/graphrag-evaluation-results.md`). The new artifact study has its own prospective local freeze, two transparent amendments and complete records in `experiments/evidence_bound_v1/` and `results/evidence_bound_v1_final/`. See `docs/evidence-bound-work-sample.md` for current methods and limitations. No human oversight study has been completed.

## Recorded execution on 25 October 2026

The candidate protocol below is retained as design history. Actual execution is defined by `experiments/protocol_freeze.json`, `protocol_amendment_01.json` and `agentic_freeze.json`; the completed findings are in `docs/work-sample.md`. This is a locally timestamped exploratory pilot, not an external preregistration. It does not implement Stage B retrieval comparisons or a human study.

The first API attempt rejected temperature zero (384 requests; no usable responses). Its records remain intact. The amendment uses default temperature one, with the same prompts and 512-token budget. The rerun produced 360 audit responses (six truncated) and 24 valid action decisions. There was no post hoc retry of truncations. No fixture labels were promoted to verified. The separately generated decisions are checked only against an explicit synthetic contract oracle. Source transcription was verified for all 18 registry rows and all 120 reference fields; label validity remains unresolved.

After the experiment, input-type checks were added to the contract to prevent malformed Python values from satisfying gates through coercion. This did not change any of the 24 recorded decisions; oracle comparisons and tests were rerun. Neither model prompts nor frozen cases changed. This implementation refinement must not be described as independently validated generalisation.

Application preparation was deferred by the user until after NyAI. No participant or referee contact occurred.

## Dataset and sources
Current `120_synthetic_cases.jsonl`: 110 template variants of 11 VCIM policy gates and 10 epistemic scope fixtures. 49 compliant, 49 violation and 22 insufficient; design-derived expected labels, **all unreviewed**. Source IDs resolve to `74_Policy` and `68_Epistemics` in local VCIM v3 workbook. Workbook hash appears in manifest. Do not leak full workbook or personal vault.

## Two independent experimental questions
**Stage A: model-as-judge auditing.** Given the same `scenario`, `reference_requirement`, `reference_boundary` and `candidate_response`, compare conventional audit instruction with structured warrant/defeater instructions. Output `compliant`, `violation`, `insufficient`. This only evaluates **prompts**, not actual production NyAI v1 or humans. Model identity, temperature, cost and prompt hashes must be recorded.

**Stage B: system contribution.** Evaluate (1) no retrieval, (2) ordinary RAG, (3) GraphRAG, (4) GraphRAG plus NyAI-inspired scope/defeater checks. Keep generation model and candidate output fixed where possible; measure retrieval accuracy separately from judgment. Run this only after Stage A and access to the personal vault/Neo4j are available. v1's `NaiveAgent` is not an appropriate strong baseline for claim-quality benchmarks.

## Construct validity / labels
- `violation`: candidate clearly contradicts an applicable, in-scope rule, omits mandatory exclusion or makes a forbidden inference.
- `compliant`: meets the stated requirement and boundary without extra unsupported certainty.
- `insufficient`: vague, missing necessary evidence or applicability information, making evaluation non-decisive.
- Reviewer must see reference evidence; template labels are excluded from the review worksheet. Collect reviewer IDs and rationales, measure agreement (recommended 2 independent raters for test cases), and adjudicate disagreements.
- For *new authentic model outputs*, reference labels from synthetic fixtures **cannot** be reused; annotate each new output independently.

## Leakage and confound prevention
- Freeze prompt before held-out use; do not tune on held-out failures.
- Prevent candidate answer, label, or hidden rubric from contaminating references.
- Keep policy IDs disjoint between development and held-out sets (implemented for initial fixtures). However, templates and wording patterns are shared across policies, so synthetic held-out results remain **engineering smoke tests**, not rigorous external evaluation.
- For actual inference, split by **policy/source family**, author source-disjoint holdouts and use at least one unrelated domain.
- Blind reviewer to experimental arm when possible; measure over-reliance and cognitive load in human studies.
- Confirm source identity and authenticity: Obsidian content is a retrieval source, not ground truth.

## Statistics and reporting
Primary endpoint should be pre-registered after independent labeling: difference in violation recall at a tolerated false-positive rate. Report 95% uncertainty intervals and paired-by-case comparisons where samples allow. Secondary: 3-way accuracy, class-wise precision/recall, selective prediction, abstention, latency, token use and failure taxonomy. No cherry-picking of cases. Do not calculate confidence from unreviewed synthetic labels.

## Safety
No real personal health decisions or autonomous irreversible actions. All examples are hypothetical research fixtures. No medical effectiveness claims. Use no real participants without appropriate consent and ethics review. Never print secrets or private vault text to public CI logs.
