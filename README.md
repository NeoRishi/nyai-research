# NyAI: evidence validation for AI oversight

An AI-generated explanation can sound convincing even when its evidence does not justify the conclusion. A citation may be irrelevant, a source may have been superseded, or an agent may claim it performed a check that never ran. A reviewer needs a way to inspect those grounds before accepting the answer or allowing the next action.

**NyAI studies how to keep AI-assisted research and agent decisions checkable when explanations alone are not reliable evidence.** It investigates whether explicit warrants, defeaters and revision conditions help reviewers identify unsupported conclusions and inappropriate actions.

This repository contains a runnable research prototype and reproducible pilot experiments. Improved human oversight has not yet been demonstrated.

## Four-study progression

| Study | Question | Recorded result |
|---|---|---|
| 1. Synthetic audits and action contracts | Do structured checks improve agreement? | Structured prompts do not beat ordinary audit; model and contract tie on 24 action cases. |
| 2. Controlled GraphRAG | Does retrieval provide needed evidence? | Graph expansion improves designated fact coverage; structured prompting adds no observed advantage. |
| 3. Runtime revision | Can current execution evidence invalidate permission? | Observed contract and conventional revalidation tie at 24/24. |
| 4. Multi-hop AssuranceDAG | Can transitive and shared-warrant checks distinguish harder failures? | Stage 1: 30/32; hybrid AST inspection: 32/32; configured 1-hop baseline: 23/32. |

These are exploratory, constructed diagnostics with correlated cases. See the [work sample guide](docs/work-sample.md) for runnable entry points and limits.

## The AI safety problem

An AI research assistant might declare an evaluation successful without running it, cite a result outside its tested scope, or continue using a conclusion after its evidence changes. As work is delegated to increasingly capable agents, fluent summaries can hide those failures from reviewers.

NyAI targets three connected questions:

- **Scalable oversight:** can a reviewer check the grounds of an AI conclusion without repeating the entire task?
- **Safe delegation:** can missing evidence or authority block a proposed action, even when its explanation sounds convincing?
- **AI assurance:** can an evaluator inspect which checks actually ran and challenge a particular evidence-to-decision link?

The proposed path to safety impact is to make unsupported conclusions easier to detect before they influence further AI research or consequential actions. That path remains a hypothesis. The current experiments do not measure deception resistance or a reduction in catastrophic risk.

Feature attribution can help explain model behaviour. NyAI examines a complementary question: **does the available evidence justify accepting this conclusion or taking this action?** Its records expose the external decision procedure; they do not reveal neural model internals or solve the black-box problem in general.

## How it works

The executable prototype checks a proposed action against a supplied policy and structured runtime facts:

1. **Establish the grounds:** identify the action, permission, evidence scope, source version and reported check outcomes.
2. **Look for defeaters:** check for revoked consent, mismatched scope, superseded evidence, unresolved conflicts, missing checks and other blocking conditions.
3. **Permit or withhold:** every mandatory condition must pass; failed or unknown facts withhold execution.
4. **Make the decision inspectable:** return the actual check results, a brief decision record and a condition for reconsideration. Reevaluate when facts change.

For example, a high confidence score cannot override missing permission or a failed test. The explanation is derived from the checks that ran; it is not a model's private chain-of-thought.

## Try the local demonstration

From the repository folder, with Python 3.11 or later:

```bash
python3 scripts/demo.py
```

No installation, API key or database connection is required. The demo runs the actual engine on synthetic facts and replays one recorded model response. It performs no real publication or other external action.

| Situation | Engine decision | Reason |
|---|---|---|
| A record claims unit tests ran, but lists no executed checks | Withhold | Claimed checks lack an execution record |
| The supplied record is corrected to include the executed tests | Permit | All mandatory conditions now pass |
| Required consent information is then removed | Withhold | A required fact is unknown |

**The trust boundary matters:** the engine checks the supplied record. It does not independently run tests, authenticate source documents or establish that an arbitrary scientific claim is true. The correction in the demo is simulated. The recorded model also catches the missing-check defect.

## Live GraphRAG to NyAI integration

A separate private-data adapter now connects the existing Aura graph to the original GraphRAG retrieval code and NyAI v1:

```bash
python3 integrations/graph_nyai.py --env /path/to/local.env \
  --query "How does Nyaya distinguish evidence sources and warranted inference?"
```

This requires the live dependencies and your own graph/API credentials. It embeds only the question, retrieves plain-RAG and graph-expanded evidence, runs the original NyAI v1 engine and audits citation/provenance structure. Private passages are saved only in ignored local storage and are not sent to a generation model. The adapter performs no database writes. A `--seed-note` diagnostic can instead use an existing chunk vector without any model API call.

The first live run returned six passages from two notes for plain RAG and six from four notes for GraphRAG, with 12 source-file references supplied by graph expansion. This shows a working integration and additional provenance availability, not better answer accuracy. Semantic support, applicability and source currentness remain unverified; a validated-answer claim is withheld. [Integration details and recorded run](docs/live-graphrag-integration.md).

## Initial experiments on 25 October

Two experiments examine different parts of the research question:

- **Auditing explanations:** compare ordinary, general-checklist and NyAI-style structured prompts on the same 120 synthetic candidate answers. These are prompt comparisons, not tests of the executable engine.
- **Checking action conditions:** compare an API model, the executable contract and simpler baselines on 24 synthetic action-policy cases, using a separately coded checker.

| Pilot | Observed result | What it tells us |
|---|---|---|
| 120 candidates, three audit prompts | Ordinary: 96/120 template matches; checklist: 92/120; structured: 84/120 | No demonstrated structured-prompt advantage; the reference labels need independent review |
| 24 action-policy cases | API model and executable contract: 24/24 checker matches each | Both handle these simple cases; no incremental benefit is observed |

The repository retains **360 actual API audit responses and 24 actual model-generated action decisions**, separately from their synthetic inputs. Six truncated audit outputs remain counted as nonmatches. The 120 design labels are unreviewed, and the separate checker was coded by the same AI assistant. Neither experiment measures human reviewer performance or establishes general safety or accuracy gains.

The next useful test is a harder, independently labelled set of plausible unsupported conclusions and conflicting evidence, followed by a study of reviewer decisions and effort.

## Controlled GraphRAG evaluation on 26 October

We also ran both case sets through actual Neo4j retrieval and a new four-condition model comparison. Because their exact reference policies are not indexed in the original wellness corpus, this experiment uses an isolated 86-node reference-policy graph. It contains source facts, not candidate answers or labels. The original knowledge-base nodes and relationships remain unchanged.

| Condition | 120 policy template matches | 24 contract-oracle matches |
|---|---|---|
| Full reference supplied directly | 96/120 | 24/24 |
| Vector RAG | 63/120 | 18/24 |
| GraphRAG | 71/120 | 24/24 |
| GraphRAG with structured audit prompt | 61/120 | 24/24 |

Graph expansion recovered all designated reference facts, compared with 91.7% for vector retrieval on the policy cases and 50% on the contract cases. It improved the recorded outcomes over vector RAG, but did not beat direct-reference access. The extra structured instruction did not improve them. The six vector-RAG contract disagreements were conservative withholding when rules were missing, not unsafe permissions.

There are 576 request records, 573 returned API responses and five failed/invalid outputs counted as nonmatches. Model calls and retrieval are real; the tasks remain synthetic. Policy labels are still unreviewed, graph structure is designed around known sources, and human oversight remains untested. [Results and interpretation](docs/graphrag-evaluation-results.md), [PDF addendum](output/pdf/NyAI_GraphRAG_Evaluation_2026-10-26.pdf), and [protocol](docs/graphrag-evaluation-design.md).

## Reproduce and inspect

### Observed execution and evidence revision

The new local diagnostic runs real tests against small fictional Python artifacts, records exit codes and content hashes, and reevaluates permission after edits, failures, missing records, changed task scope and revoked approval:

```bash
python3 scripts/run_runtime_revision.py --output /tmp/nyai-runtime-replay
```

It needs no credentials, private knowledge base or LLM framework. Twelve constructed trajectories contain 24 correlated decision points. Both a conventional rechecking workflow and the NyAI observed-evidence contract agree with all 24 design decisions; each withholds all eight designated invalid permissions. Trusting a synthetic success claim or caching the initial permission permits those eight. **This shows the importance of current execution evidence; it does not show an advantage over conventional checks.** The programs are trivial, approval changes are simulated, and no model responses or human review are involved. [Protocol, results and remaining validation](docs/runtime-evidence-study.md).

### Multi-hop assurance graphs, shared-warrant cuts and causal-slice compression (Study 4)

Because Study 3 (`runtime_evidence.py`) tests a single-step dependency ($d=1$), conventional revalidation and the NyAI contract tie (`24/24`). Study 4 (`src/nyai_research/assurance_dag.py`, `scripts/run_assurance_dag.py`) extends host-observed execution binding to **multi-hop evaluation chains ($d \in \{1, 2, 3\}$), shared-warrant checks across safety-case branches, and causal-slice pruning ($\text{Ancestors}(D)$)**:

```bash
python3 scripts/run_assurance_dag.py
```

Across 16 multi-step trajectories (32 correlated decision points; mean step compression **79.5%**, token compression **85.5%**):

| Arm | Valid permits (/20) | False alarms (/20) | Invalid withheld (/12) | Agreement (/32) |
|---|---:|---:|---:|---:|
| Conventional 1-hop revalidation | 20 | 0 | 3 | 23/32 (71.9%) |
| Flat hash manifest (configured heuristic) | 20 | 0 | 4 | 24/32 (75.0%) |
| Unpruned transcript monitor | 19 | 1 | 2 | 21/32 (65.6%) |
| **NyAI AssuranceDAG (Stage-1 structural only)** | **20** | **0** | **10** | **30/32 (93.8%)** |
| **NyAI AssuranceDAG (Stage-1 + Stage-2 causal slice)** | **20** | **0** | **12** | **32/32 (100.0%)** |

Stage-1 catches all 4 multi-hop zombie claims ($d \ge 2$) and all 3 shared-warrant collapses with 0 false alarms, while missing the 2 pure semantic reward hacks (`T11–T12`) by design because file hashes are fresh and exit codes are zero. Stage-2 causal-slice AST inspection over $\text{Ancestors}(D)$ catches both semantic hacks while avoiding the dead-branch false alarm suffered by the windowed transcript heuristic (`T14`). Compression counts recorded log steps and whitespace-separated log words; human effort and model tokenizer counts were not measured. These are constructed cases with configured claim dependencies, not a general minimum-cut solver or an open-ended agent evaluation. See [Study 4 details and limitations](docs/assurance-dag-study.md).

### Earlier experiment replay

```bash
python3 -m unittest discover -s tests -v
python3 scripts/summarize_pilot.py
python3 scripts/verify_agentic.py
python3 scripts/verify_artifacts.py
python3 scripts/summarize_graphrag144.py
python3 scripts/verify_graphrag144.py
```

These commands use stored outputs and need no credentials. Full replay and live-run instructions are in [Running experiments](docs/running-experiments.md).

The demo and recorded action-policy results do not depend on the private knowledge base. A separate, allowlisted reproducibility package is prepared for review; see [Sharing and independent validation](docs/sharing-and-validation.md). It excludes private corpus content, proprietary policy excerpts, credentials and repository history. Private knowledge-base vault notes and raw proprietary workbooks remain excluded from this repository.

- [Research work sample](docs/work-sample.md) and [standalone PDF](output/pdf/NyAI_Research_Work_Sample_2026-10-25.pdf)
- [Current consolidated research summary](docs/current-research-summary.md), including the runtime revision diagnostic and its limits
- [Research question and proposed study](docs/research-plan.md)
- [Implementation and trust boundaries](docs/implementation-notes.md)
- [What has actually been verified](docs/verification-status.md)
- [Protocol, controls and limitations](docs/methodology.md)

## Transparency, oversight and the EU AI Act

The earlier NyAI position paper discusses **Regulation (EU) 2024/1689, Article 86**. The research also relates to the Act's transparency and oversight objectives:

| Provision | Research connection |
|---|---|
| [Article 13](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-13) - transparency for deployers | Make outputs, evidence limits and check results interpretable |
| [Article 14](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14) - human oversight | Investigate appropriate reliance, contestability and conditions for withholding an action |
| [Articles 55 & 72](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-55) - systemic-risk evaluation & post-market monitoring | Propagate upstream evaluation retractions and detect correlated-warrant collapse across safety-case branches |
| [Article 86](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-86) - explanation of certain individual decisions | Emit machine-checkable principal grounds (`Ancestors(D)`), unmet gates, and repair suggestions (`minimal_repair_set`) |

These are research connections, not a compliance determination. Article 86 has a specific scope involving certain Annex III high-risk systems and consequential decisions affecting people; it is not a universal right to every model's internal reasoning. No statutory duty is established as fulfilled by this prototype. See [the regulatory mapping and its limits](docs/eu-ai-act-relevance.md).

## Foundations and scope

NyAI draws selectively on Nyaya concepts of warranted knowledge, defeaters and revisable conclusions. The philosophical framing supplies research questions; it does not establish correctness. The prototype uses task-specific conditions rather than treating evidence categories as a universal numerical hierarchy.

The project reuses [NyAI v1](https://github.com/NeoRishi/nyai-dashboard), which demonstrates source classification, belief revision and reasoning traces, and parsing/retrieval code from [Vedic GraphRAG](https://github.com/NeoRishi/vedic-graphrag). The live graph adapter is separate from the 24-case action-contract demo and the completed 120-case prompt pilot. Selected VCIM mechanisms inform evidence scope, policy precedence and explanation records. See [source provenance](vendor/PROVENANCE.md) and [the source audit](docs/repository-audit.md).

## AI assistance

AI assisted code, synthetic cases, experiment orchestration, analysis and documentation. API-generated outputs are recorded explicitly. No assistant-generated annotation is represented as independent human verification.
