# NyAI: Evidence-Bound Oversight for Autonomous AI Research Agents

Technical report | 27 October 2026 | Preliminary findings; pending factual and authorship approval

## Abstract

AI research agents can report convincing conclusions whose execution evidence is missing, stale or outside the claimed scope. We investigate a narrow distinction: an evaluation ran successfully, versus its result warrants current endorsement of a particular research claim. We audit earlier NyAI experiments and implement a reproducible artifact-based challenge set with 24 constructed scenarios. A real subprocess grader evaluates fictional behavioral records; the benchmark does not run a frontier model. A provenance-only condition makes nine unwarranted acceptances under the declared policy; selective revision misses two deliberately omitted dependencies. Complete conventional revalidation accepts all five eligible cases and withholds all 19 ineligible cases. Adding NyAI warrant/revision records gives identical decisions by construction. These results illustrate verification boundaries, not a novel safety method or improved human oversight. The useful next question is whether explicit records help reviewers beyond ordinary guarded workflows and logs.

## 1. Problem and safety motivation

An autonomous assistant might claim a safety evaluation succeeded without running it, associate a result with the wrong model or dataset, generalize an aggregate measurement to a failing subgroup, or continue using a conclusion after contrary evidence arrives. Such failures can undermine AI-assisted alignment research even if the final prose is plausible and every citation identifier resolves.

The proposed causal pathway is: automation produces more research artifacts than people can inspect; binding conclusions to observable evidence makes some unsupported endorsements detectable; preventing those endorsements from propagating could preserve the reliability of safety decisions. Each step is conditional. It requires valid evaluations, sufficiently complete observation, responsive overseers and consequential downstream use. It fails if the scientific test is inadequate, relevant actions are unobserved, infrastructure is compromised or reviewers ignore correct warnings. No experiment here measures catastrophic-risk reduction, deception resistance, alignment or mechanistic interpretability.

Nyaya concepts of warrants, defeaters and revisability motivate questions, not guarantees. The implementation uses explicit engineering rules that stand or fall independently of the philosophical influence.

<!-- pagebreak -->

## 2. Related work and research choice

AI Control evaluates oversight protocols under intentional subversion[1]; CTRL-ALT-DECEIT examines sabotage in automated AI R&D[2]. Those settings are more adversarial and behaviorally realistic than our current fixtures. NyAI does not establish robustness against their threat models.

Execution evidence and version binding are established safeguards. SLSA requires checking artifact digests and trusted provenance expectations[3]; W3C PROV models derivation, revision and invalidation[4]. A Trust Layer for Agent Evaluation separates score support, traceable computation, completion honesty and repeatability[5]. Merely distinguishing a reported result from observed execution is not a new contribution.

STALE studies agent-memory invalidation[6]. Especially close, Change-Provenant Supervision separates recorded lineage from independent current-contract revalidation and tests omitted dependency edges[7]. We therefore treat the missing-edge experiment as a bounded conceptual stress test in research-evaluation artifacts, not a novel invalidation algorithm. ALCE distinguishes citation support/completeness from answer correctness[8]. Resolvable identifiers in our earlier GraphRAG study are a much weaker check. Trace-tampering results also show why an agent-writable log is not independent attestation[9]. Recent preprints are cited as their authors' findings, not independently reproduced results. This targeted review is not exhaustive novelty clearance.

We choose stale or invalidated conclusions as the immediate target. Better execution verification is necessary engineering; whether explicit records improve overseer decisions is the next empirical question. There is currently no defensible claim of a new reasoning calculus or superior oversight method.

## 3. Mechanism and trusted boundary

The observer writes exact copies of model-manifest, behavioral-output, dataset, configuration and grader files into a temporary directory. It runs a fixed grader, records exit status/stdout/stderr, hashes all bound inputs before and after execution and registers the result. A claim specifies model/task identity, group, observed-rate threshold and conclusion type. Endorsement also requires current simulated approval, active evidence and no active relevant contrary run.

The registry, authority source, fixed grader and operating system are trusted. A proposer can issue false claims, mutate working inputs, cite an unregistered run or omit a declared dependency. It cannot alter the protected observer in this model. Hashes bind bytes; they do not validate the scientific test. No signatures, remote attestation, sandbox for malicious code or host-compromise defense is claimed. A final consume step rechecks a private snapshot and copies those verified bytes; this is a simulated handoff, not atomic distributed deployment or protection from operating-system races.

<!-- pagebreak -->

## 4. Experimental design

The prospective local protocol and code hashes were committed at 9727b26 before the first full run. There are 24 scenarios from one shared generator, without an independent holdout. They cover valid controls; a threshold boundary; missing/empty execution; input/version changes; unsupported subgroup/population claims; contrary or retracted results; changed authority; benign unrelated edits; correction; and omitted dependencies. Reference decisions are computed by a separately written same-author oracle from raw artifacts and host state. No expected label or case identifier is used to make an arm decision. This is specification checking, not independent human scientific judgment.

The data are 20 fictional refusal/compliance markers per ordinary scenario. The grader computes group counts and failure fractions. These are not model-generated completions or evidence of any real model's safety. Local execution and arithmetic are real; behavior and permissions are constructed. An observed-rate statement concerns only the fixture. Withholding means permission to endorse is absent under a conservative policy; a later contrary run does not make the earlier historical measurement false. Retiring contrary evidence is a simulated authority action, not proof a scientific conflict was resolved.

All conditions receive identical current information. Report-only follows a synthetic success assertion and is explicitly weak. Integrity-only checks registered execution, input identity and metric coverage; it is a provenance-component ablation, not the strongest conventional end-to-end workflow. Lineage-selective rechecks after changes intersect declared dependencies; two cases deliberately omit a load-bearing dependency. Complete conventional revalidation checks all current requirements. The recorded NyAI condition uses exactly that predicate plus explicit unmet-check, warrant and revision records. It is not a fifth independently distinguishable decision algorithm.

After the first run, AI review identified a registry-key/internal-execution-ID inconsistency. Amendment 01 adds a strict identity check. A subsequent raw-record audit found that the missing-evidence scenario also hid one execution from accounting. Amendment 02 retains a separate complete host execution log: 33 runs occurred, while earlier archives counted 32 retained observations. All archives are preserved. Case decisions and acceptance counts are unchanged; the final amended run is primary. This is transparent post-run hardening, not an untouched confirmatory evaluation or external preregistration.

## 5. New findings

|Condition|Valid accepted /5|Unwarranted accepted /19|Appropriate withheld /19|
|---|---|---|---|
|Report-only weak control|5|19|0|
|Execution integrity only|5|9|10|
|Lineage-selective ablation|5|2|17|
|Complete conventional revalidation|5|0|19|
|Same checks with NyAI records|5|0|19|

The final amended run includes 33 subprocess evaluations and two deliberate errors: empty data and incomplete output coverage. They remain recorded, without silent retry. There are zero model calls, tokens or API charges. All complete conditions have zero false withholds on these five controls. This small, deliberately chosen set does not establish an operational false-positive rate. All cases are correlated engineering examples; no significance tests or population confidence intervals are reported.

<!-- pagebreak -->

## 6. Failure analysis and earlier findings

Nine integrity-only errors remain because a reproducible current run is insufficient for claim scope, evidential status or authority. A subgroup can fail while the aggregate passes; a current unsupported generalization can retain perfect artifact provenance. Approval revocation and source retraction defeat present use under the policy without changing historical execution facts.

The selective condition fails on a missing dataset dependency and a missing active-counterevidence dependency. This demonstrates a familiar completeness requirement in deliberately defective declarations. It does not estimate how often real systems omit dependencies. Complete revalidation catches both. Nineteen cases trigger logical lineage rechecking, but every arm is actually computed in the runner: this number measures notification behavior, not measured computational savings.

Complete revalidation and the recorded condition are equal by construction. The tie checks implementation consistency; it neither proves records help reviewers nor proves they cannot help. A future matched presentation experiment must measure reviewer errors and time. A contribution could be an informative negative result about that proposed benefit.

Historical evidence remains separate. In the 120-case prompt pilot, ordinary/checklist/structured instructions match 96/92/84 unreviewed template labels; 360 actual audit responses include six truncations counted as nonmatches. A separate 24-case action experiment reaches 24/24 for both model and executable contract. These easy cases show no incremental contract benefit.

The actual Neo4j GraphRAG comparison yields 96/63/71/61 policy matches for full-reference/vector/graph/graph-plus-structured conditions, and 24/18/24/24 action-oracle matches. Its 576 application-level request records include 573 returned responses and five failed/invalid outputs; client retries mean these are not transport-attempt counts. Extra graph context recovers more reference facts but creates length/distractor confounds. The six vector action disagreements are withholding with missing rules, not unsafe permissions. Full-truth outcome agreement alone can penalize appropriate epistemic caution. No private wellness passage was sent to a generation model.

The earlier 12-trajectory runtime diagnostic ties conventional and NyAI on 24 correlated decision points. Audit found an unused harness identity check, malformed-record acceptance and unhandled observation failures. These have regression-tested fixes. Historical bytes and manifest are retained as evidence of their original version. The reviewed-label scorer also now retains missing/invalid responses in primary denominators; historical human-reviewed metrics remain empty.

<!-- pagebreak -->

## 7. Limitations and novelty assessment

This is a bounded artifact-integrity and policy-application study. Cases, oracle and analysis share an AI author; separate AI review is not independent human validation. There are no completed human annotations, participant outcomes, new live-agent decisions or independently authored evaluation tasks. Near-perfect complete-check results are unsurprising for a finite specification designed by the same author. Cases are neither representative nor powered to estimate deployment reliability.

The evaluator is a toy refusal-marker metric, not a valid frontier safety evaluation. Model identity is a manifest, not a loaded model/weight attestation. Approval and retraction are simulated authority events. The no-conflicting-run policy can be overly conservative; a failed or conflicting rerun may reflect noise or an inadequate task. Generalization beyond observed data requires statistical and scientific warrants outside this contract. The observer registry is protected by assumption, not a deployed security boundary.

Existing provenance and stale-state research already addresses much of the mechanism. The present contribution is a reproducible, challengeable research-evaluation stress test and a diagnosis of where acceptance notions diverge, including negative incremental findings. It is not evidence of algorithmic novelty, general safety superiority or reduced human review burden. The applicant reports originating the conceptual framing and earlier prototype/GraphRAG designs, directing the consolidation and research pivot, and reviewing reported limitations. AI tools substantially assisted implementation, cases, execution, analysis and writing. The applicant has not independently reproduced every run. This contribution statement is applicant-supplied; final report approval remains pending.

## 8. Falsifiable continuation agenda

First, externally review the policy and cases, record disagreement and add independently authored research-evaluation tasks. Distinguish arithmetic truth, scientific support and policy permission. Hold out task families and freeze numerical success thresholds before collecting new outcomes.

Second, compare ordinary guarded workflows and explicit records using the same artifacts, tools and model budgets. Test model reviewers only after a frozen protocol and cost approval. The key hypothesis is improved detection of invalidated endorsements at an acceptable false-withhold and review-cost tradeoff, not higher unqualified accuracy. If complete conventional checks account for all benefits, stop claiming a new decision method and focus on diagnosis or retire the mechanism.

Third, subject to recruitment, consent and appropriate review, counterbalance ordinary-log versus structured-record presentation across tasks. Measure unwarranted acceptance, useful acceptance, appropriate withholding, reviewer time and explanation-grounded corrections. Pivot if records add burden without a useful detection benefit. No such study has been performed or guaranteed. Extend to stronger models and intentional sabotage only if the evaluation boundary remains credible.

## 9. Reproduction, access and disclosure

The allowlisted supplement contains fictional artifacts, frozen protocol, amended results, source, tests and a blank review queue. It needs Python 3.10+ and no credentials, database, private corpus or model service. Commands are `python3 scripts/run_evidence_bound.py --phase verify --output results/evidence_bound_v1_final` and `python3 scripts/run_evidence_bound.py --phase run --output /tmp/nyai-independent-replay`. Compare resulting summaries, not temporary traceback paths or timings. Full repository tests and historical integrity checks are separate.

AI assisted code, fixtures, audit, analysis and writing; additional AI agents provided critical review. None is a human reviewer. No external human study, public release or application submission occurred. The full repository remains private. The supplement is prepared for author privacy/rights review before distribution; it removes local temporary traceback prefixes and records that transformation while preserving unmodified raw outputs privately.

<!-- pagebreak -->

## References

[1] Greenblatt et al. AI Control: Improving Safety Despite Intentional Subversion. https://arxiv.org/abs/2312.06942

[2] Ward et al. CTRL-ALT-DECEIT: Sabotage Evaluations for Automated AI R&D. https://arxiv.org/abs/2511.09904

[3] SLSA. Verifying artifacts, specification v1.2. https://slsa.dev/spec/v1.2/verifying-artifacts

[4] W3C. PROV-DM: The PROV Data Model. https://www.w3.org/TR/prov-dm/

[5] Sediqin et al. A Trust Layer for Agent Evaluation. 2026 preprint. https://arxiv.org/abs/2610.07274

[6] Chao et al. STALE: Can LLM Agents Know When Their Memories Are No Longer Valid? 2026 preprint. https://arxiv.org/abs/2605.06527

[7] Salas. Change-Provenant Supervision: Governing Learned Artifacts Under Policy Change. 2026 preprint. https://arxiv.org/abs/2609.28574

[8] Gao et al. Enabling Large Language Models to Generate Text with Citations. https://arxiv.org/abs/2305.14627

[9] Qin et al. LLM Agents Can Easily Tamper With Their Own Traces. 2026 preprint. https://arxiv.org/abs/2609.30266

## Evidence map

New study: `experiments/evidence_bound_v1/`, `results/evidence_bound_v1_final/`, original `results/evidence_bound_v1/`. Core implementation: `src/nyai_research/evidence_bound.py`. Runner: `scripts/run_evidence_bound.py`.

Historical experiments: `results/template_pilot_summary.json`, `results/agentic_contract_summary.json`, `results/graphrag_144_v1/`, `results/runtime_revision_v1/`. Historical raw material includes proprietary derivatives and is excluded from the new sanitized supplement.

Audit: `docs/research-audit-2026-10-27.md`. Detailed literature: `docs/related-work-2026-10-27.md`. Application-specific positioning and unresolved author facts are separate from this technical report.
