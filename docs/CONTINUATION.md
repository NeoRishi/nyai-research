# NyAI continuation state

As of 25 October 2026, the local research implementation and preliminary experiments are complete. The work sample reports negative or ceiling results honestly. The central human-oversight hypothesis remains untested.

After the user identified the missing retrieval integration, a real read-only GraphRAG-to-NyAI adapter was added and run against Aura. See `docs/live-graphrag-integration.md` and `results/graph_nyai_integration.json`. This is distinct from the prior synthetic experiments. Private passages stay local; it is not a generated-answer evaluation and makes no claim of entailment validation. No Neo4j writes were performed.

## What to open

1. `docs/work-sample.md` and the PDF in `output/pdf/`.
2. `results/template_pilot_summary.json`: 96/120 ordinary, 92/120 checklist, 84/120 structured template matches. All labels are unreviewed.
3. `results/agentic_contract_summary.json`: 24/24 model and contract oracle matches; no incremental gain.
4. `docs/verification-status.md`: distinguishes byte/transcription checks, automated oracle checks and missing human review.
5. `docs/implementation-notes.md`: defines the implementation and its trust boundary.

## Do not rerun unnecessarily

All raw model outputs are recorded. The settings failure and amendment are preserved. Standard-library scoring commands do not need credentials. Live API reruns cost money and change stochastic samples. Do not silently retry truncated responses or replace frozen labels. Do not run the upstream importer or chunk builder against Aura; no graph mutation is needed for the current study.

## Next research priority

Obtain independent review of a small diverse set and rewrite the benchmark rubric before running another large batch. The 24-output worksheet has blank labels. Labels from source templates cannot be copied onto model-generated outputs. A second AI pass is not independent human review. Include realistic research claims and permission failures with primary-source excerpts; control evidence availability and reviewer time. The easy action-policy set is already at ceiling for the model.

## Application readiness requested by the user

The user has now requested the exact remaining steps for application readiness. See `docs/mats-application-checklist.md` for the current applicant actions, assistant preparation tasks and proposed 90-day research milestones. The published requirements place the explicit 90-day plan under Incubation; Bridge asks for a research plan and theory of change. Do not mistake proposed future validation for completed work. No application has been submitted and no referee has been contacted.

The separate sanitized 24-case package remains unpublished for applicant review. The full private repository and older complete research archive should not be made public. The live application's introduction was inspected; later prompts and file/word limits remain to be checked without invented entries or acknowledgments on the applicant's behalf.

The target remains 27 October for readiness, with the official 31 October 2026 AoE deadline. Two referees means people able to speak directly to the quality of the applicant's work. Obtain their actual details and consent through the applicant; do not invent or contact them without authorization.
