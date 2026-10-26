# NyAI: evidence-grounded decisions in AI-assisted research

Preliminary work sample - 26 October 2026. Prepared with AI assistance; applicant review and contribution statement remain pending.

## Research problem

An AI-generated explanation can sound plausible even when its supporting evidence is incomplete, out of date or outside the task's scope. In AI-assisted research, accepting such a conclusion can propagate an invalid result into later evaluations or decisions. The relevant question is not only whether a conclusion happens to be correct, but whether accepting it is justified by the evidence available to the reviewer or agent.

NyAI investigates explicit evidence requirements, blocking conditions and revision records as tools for keeping research decisions checkable. Its safety theory of change is that detecting unsupported conclusions and invalidated permissions before downstream use could help preserve meaningful oversight as more research is automated. The experiments below do not establish that impact or measure catastrophic risk reduction.

## Study 1: do structured audit instructions improve judgments?

The initial pilot compared three audit prompts on 120 synthetic candidate answers with identical supplied evidence. Ordinary, general-checklist and NyAI-style structured prompts matched 96, 92 and 84 template labels, respectively. There are 360 actual model responses, with six truncations counted as nonmatches. Labels were derived from constructed cases and have not been independently reviewed.

The structured prompt did not demonstrate an advantage. An additional 24-case action-policy comparison reached a ceiling: both the model and the executable twelve-gate contract matched all 24 finite-set design decisions. The separate checker was authored with the same assistant, not an independent human. These findings motivated examination of evidence availability and runtime observation rather than more elaborate prompting.

## Study 2: does graph retrieval provide the necessary evidence?

The original GraphRAG retrieval code was integrated with Neo4j Aura. Because the exact benchmark policies were absent from the original private corpus, the evaluation used an approved isolated 86-node graph containing reference-policy facts and fictional runtime facts. Existing knowledge-base counts were preserved; no private wellness passages were sent to a generation model.

Four conditions used the same model: complete reference evidence, vector retrieval, graph-expanded retrieval and the same graph evidence with a structured audit prompt. Across the 120 policy candidates, template-label matches were 96/120, 63/120, 71/120 and 61/120. Across 24 action-policy cases, full-policy oracle matches were 24/24, 18/24, 24/24 and 24/24. The archive contains 576 request records, 573 returned responses and five failed or invalid outputs counted as nonmatches.

Graph expansion recovered more designated facts but did not beat direct reference access. Structured instructions again did not help. The extra graph context creates a context-length and distractor confound. The graph was designed around known source families; no held-out family generalization is established.

Crucially, the six vector-retrieval action disagreements were withholding when rules were missing, not unsafe permissions. Some other permissions matched the full-policy answer despite incomplete rule coverage. Thus full-policy outcome agreement alone cannot determine whether a decision was warranted by the retrieved evidence. Citation identifiers resolving successfully also does not establish that the cited facts support the conclusion.

## Study 3: can observed execution invalidate an earlier permission?

A separate engineering diagnostic connects actual local subprocess test outcomes to artifact hashes, task identity and simulated approval bindings. Twelve constructed event trajectories contain 24 correlated decision points. Changes include failed tests, edits without retesting, missing observations, changed tasks, revoked approval, false success claims and correction after failure. No model calls are involved.

Both a conventional rechecking workflow and the NyAI observed-evidence contract permit all 16 designated valid decision points and withhold all eight designated invalid points. Trusting a synthetic success claim or retaining the initial permission permits those eight invalid points. The weak controls illustrate failure modes; they are not representative model baselines. The conventional workflow is the meaningful baseline and ties NyAI. No incremental decision advantage is established.

The observer executes real tests, but the programs are trivial and the tests are fixed. Approval events are simulated. The host and observation store are trusted; this is not tamper-proof attestation. No real action is authorized or executed. The test suite does not establish scientific correctness, and final permission is not atomically bound to a subsequent external action.

## Interpretation and next contribution to test

The current contribution is a reproducible investigation that separates evidence coverage, outcome agreement and warranted permission, with explicit negative results and executable examples. It is not a demonstrated improvement in human oversight or a novel general reasoning calculus. Novelty relative to existing provenance, workflow validation and oversight methods requires a systematic prior-art comparison.

The next falsifiable hypothesis is that explicit warrant and revision records help reviewers detect an unsupported conclusion or withdraw a previously justified acceptance after evidence changes, beyond what ordinary guarded workflows and logs provide. Test this using independently reviewed research tasks and artifact-based references; compare equal evidence and tool access; separate unwarranted acceptance, appropriate withholding, useful completion and reviewer effort. Hold out task families rather than near-duplicate variants.

## Reproducibility, privacy and attribution

The private repository preserves protocols, raw model responses, retrieval contexts, code hashes, scoring and limitations. `scripts/run_runtime_revision.py` reruns the local observation diagnostic without credentials or private data. `scripts/verify_artifacts.py` and `scripts/verify_graphrag144.py` check stored experiment integrity and scoring. These checks are automated, not independent scientific validation.

AI assisted code, synthetic cases, analysis and documentation. Applicant intellectual contributions must be stated from actual work before submission. No external human annotation or participant study has been performed. A separate sanitized public review package exists for the earlier 24-case experiment only; it does not yet reproduce every study in this report. The full repository should remain private. Independent reviewers can inspect the new fictional runtime study without the private knowledge base, but its distribution package still needs preparation and applicant review.
