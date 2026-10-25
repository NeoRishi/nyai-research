# NyAI: making AI conclusions checkable

An AI-generated explanation can sound convincing even when its evidence does not justify the conclusion. A citation may be irrelevant, a source may have been superseded, or an agent may claim it performed a check that never ran. A reviewer needs a way to inspect those grounds before accepting the answer or allowing the next action.

**NyAI investigates whether explicit evidence warrants, defeaters and revision conditions can make that review more reliable.** The goal is to help people see what supports a conclusion, what blocks it, and what new evidence would change the decision.

This repository contains a runnable research prototype and reproducible pilot experiments. Improved human oversight has not yet been demonstrated.

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

## What we tested

Two experiments examine different parts of the research question:

- **Auditing explanations:** compare ordinary, general-checklist and NyAI-style structured prompts on the same 120 synthetic candidate answers. These are prompt comparisons, not tests of the executable engine.
- **Checking action conditions:** compare an API model, the executable contract and simpler baselines on 24 synthetic action-policy cases, using a separately coded checker.

| Pilot | Observed result | What it tells us |
|---|---|---|
| 120 candidates, three audit prompts | Ordinary: 96/120 template matches; checklist: 92/120; structured: 84/120 | No demonstrated structured-prompt advantage; the reference labels need independent review |
| 24 action-policy cases | API model and executable contract: 24/24 checker matches each | Both handle these simple cases; no incremental benefit is observed |

The repository retains **360 actual API audit responses and 24 actual model-generated action decisions**, separately from their synthetic inputs. Six truncated audit outputs remain counted as nonmatches. The 120 design labels are unreviewed, and the separate checker was coded by the same AI assistant. Neither experiment measures human reviewer performance or establishes general safety or accuracy gains.

The next useful test is a harder, independently labelled set of plausible unsupported conclusions and conflicting evidence, followed by a study of reviewer decisions and effort.

## Reproduce and inspect

```bash
python3 -m unittest discover -s tests -v
python3 scripts/summarize_pilot.py
python3 scripts/verify_agentic.py
python3 scripts/verify_artifacts.py
```

These commands use stored outputs and need no credentials. Full replay and live-run instructions are in [Running experiments](docs/running-experiments.md).

- [Research work sample](docs/work-sample.md) and [standalone PDF](output/pdf/NyAI_Research_Work_Sample_2026-10-25.pdf)
- [Research question and proposed study](docs/research-plan.md)
- [Implementation and trust boundaries](docs/implementation-notes.md)
- [What has actually been verified](docs/verification-status.md)
- [Protocol, controls and limitations](docs/methodology.md)

## Foundations and scope

NyAI draws selectively on Nyaya concepts of warranted knowledge, defeaters and revisable conclusions. The philosophical framing supplies research questions; it does not establish correctness. The prototype uses task-specific conditions rather than treating evidence categories as a universal numerical hierarchy.

The project reuses [NyAI v1](https://github.com/NeoRishi/nyai-dashboard), which demonstrates source classification, belief revision and reasoning traces, and parsing utilities from [Vedic GraphRAG](https://github.com/NeoRishi/vedic-graphrag). The existing graph and corpus were audited; retrieval is not connected to the new action-contract demo. Selected VCIM mechanisms inform evidence scope, policy precedence and explanation records. See [source provenance](vendor/PROVENANCE.md) and [the source audit](docs/repository-audit.md).

## AI assistance

AI assisted code, synthetic cases, experiment orchestration, analysis and documentation. API-generated outputs are recorded explicitly. No assistant-generated annotation is represented as independent human verification.
