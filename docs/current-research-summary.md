# NyAI: evidence-grounded decisions in AI-assisted research

Preliminary work sample - updated 28 October 2026. Prepared with AI assistance; applicant review and contribution statement remain pending.

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

## Study 4: when do multi-hop assurance graphs outperform 1-hop revalidation?

Study 3 tied conventional revalidation (`24/24`) because every check was depth-1 ($d=1$). On 28 October 2026, we implemented `src/nyai_research/assurance_dag.py` and `scripts/run_assurance_dag.py` to test multi-hop evaluation chains ($d \in \{1, 2, 3\}$) across 16 trajectories (32 decision points) using real Python subprocess executions and AST import analysis.

At depth $d=1$ (`T01–T03`), conventional 1-hop revalidation and `AssuranceDAG` again tie (`3/3`). However, on multi-hop transitive invalidations ("zombie claims", `T04–T07`, where an upstream calibration split, root dataset status, execution order, or scope drifts after an intermediate claim was cached) and correlated-warrant collapses (`T08–T10`, where branches share an imported `shared_grader.py` module or a `shared_calib.json` input file), 1-hop revalidation catches `0/7` while Stage-1 `AssuranceDAG` catches `7/7` with `0/20` false alarms across valid decision points, including the four terminal valid controls (`T13–T16`).

Crucially, on pure semantic reward hacks (`T11–T12`, where an evaluation script is modified to weaken assertions to `>= -999` or `assert True` and re-executed cleanly with valid hashes), Stage-1 structural checking gets `0/2` by design. Pruning dead exploratory branches ($\mathcal{V} \setminus \text{Ancestors}(D)$) compresses trajectory steps by **79.5%** (tokens by **85.5%**), allowing Stage-2 causal-slice AST inspection to catch `2/2` semantic hacks while avoiding the dead-branch false alarm suffered by unpruned transcript monitoring (`T14`). See `docs/assurance-dag-study.md` and `results/assurance_dag_v1/summary.json`.

## Interpretation and next contribution to test

The current contribution is a reproducible investigation that separates evidence coverage, outcome agreement and warranted permission, with explicit negative results and executable examples. It is not a demonstrated improvement in human oversight or a novel general reasoning calculus. Novelty relative to existing provenance, workflow validation and oversight methods requires a systematic prior-art comparison.

The next falsifiable hypothesis is that explicit warrant and revision records help reviewers detect an unsupported conclusion or withdraw a previously justified acceptance after evidence changes, beyond what ordinary guarded workflows and logs provide. Test this using independently reviewed research tasks and artifact-based references; compare equal evidence and tool access; separate unwarranted acceptance, appropriate withholding, useful completion and reviewer effort. Hold out task families rather than near-duplicate variants.

## Reproducibility, privacy and attribution

This public repository preserves protocols, recorded model responses, retrieval contexts, code hashes, scoring and limitations. `scripts/run_runtime_revision.py` and `scripts/run_assurance_dag.py` rerun the local observation diagnostics without credentials or private data. `scripts/verify_artifacts.py` and `scripts/verify_graphrag144.py` check stored experiment integrity and scoring. These checks are automated, not independent scientific validation.

AI assisted code, synthetic cases, analysis and documentation. Applicant intellectual contributions must be stated from actual work before submission. No external human annotation or participant study has been performed. Private vault notes, proprietary workbooks and credentials remain excluded. Independent reviewers can run both fictional runtime studies and replay the recorded experiments from this repository without the private knowledge base. The earlier standalone review package covers only the 24-case experiment.
