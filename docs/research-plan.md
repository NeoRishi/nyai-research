# NyAI research agenda for checkable AI oversight

Update 27 October: the immediate research target is detecting stale or invalidated research endorsements under a declared scope/authority policy. See `docs/evidence-bound-work-sample.md` for executed results and `application/bridge-alignment-2026-10-27.md` for the proposed continuation/pivot criteria. The initial agenda below is retained as history; no reviewer efficacy hypothesis has been established.

## Question
Can **explicit, claim-specific warrants and defeater checks** help evaluators identify unsupported or policy-violating recommendations made by AI agents, compared with a conventional answer-and-explanation interface?

## Motivation
As AI systems perform longer sequences of work, fluent justifications can create false reassurance. Source citations are not automatically verified, explanations may omit relevant counterevidence, and human overseers have limited time. The aim is not to reveal hidden chain-of-thought but to test **checkable external decision records**: action/claim, supporting source, applicable rule, opposing evidence, uncertainty, and revision trigger.

## Starting point
- NyAI v1: deterministic pramāṇa tagging, fallacy rules, beliefs and five-part trace.
- Vedic GraphRAG: source-addressable Obsidian/Neo4j retrieval with graph relationships.
- VCIM v3: a detailed, **unvalidated product specification** for claim-specific evidence scopes, hard gates, decision precedence and explanation contracts.

## Hypotheses
- H1: On independently adjudicated cases, structured decision records increase violation detection recall versus ordinary explanation when both methods receive the same evidence.
- H2: The protocol does **not** increase false-positive rate beyond a prespecified acceptable tolerance (to be defined before testing).
- H3 (exploratory): Under limited review time, human raters with structured records make more *appropriate* accept/reject decisions than those receiving conventional explanations.

## Experimental approach
1. Audit existing prototypes and freeze input/output interfaces.
2. Build varied independent tasks with verifiable reference materials and explicit counterevidence (agent actions, research synthesis and policy compliance), including benign controls.
3. Run the same candidate responses and sources in baseline and NyAI-structured conditions; isolate retrieval as a separate experimental factor.
4. Blind reviewers to condition and template labels; collect categorical gold label, uncertainty and disagreement; resolve conflicts with an adjudication protocol.
5. Compare precision, recall, false-positive rate, calibration, time and cost. Analyse failure cases and report negative results.
6. Extend into human oversight only after ethics/consent considerations are addressed.

## Pilot and pivot criteria
The present 120 synthetic fixtures are a *harness smoke-test only*. They are too templated, domain-specific and unreviewed to support a safety impact claim. Proceed to a wider study only if a curated independent set demonstrates a plausible signal with transparent uncertainty; otherwise test retrieval-vs-reasoning confounds, simplify the approach, or stop.

## Why it could matter for AI safety
This research targets a component of the broader **scalable oversight** problem: can an overseer efficiently spot a wrong or unsupported agent conclusion without blindly trusting its narrative? This is an indirect, early-stage theory of change toward making delegated AI research and agent actions checkable. There is **no established link yet to catastrophic-risk reduction**; later work must test stronger models, more consequential agentic settings, deception and distribution shifts.

## Scope and boundaries
This is not mechanistic interpretability, a general proof of alignment, a medical intervention or a claim that Nyāya philosophy by itself guarantees reliable AI. The philosophical influence informs the candidate evaluation structure, which must stand or fall by results.

## Proposed longer-horizon progression
I. Build reliable baselines and independent benchmarks. II. Test structured oversight in longer agent traces and adversarial settings. III. Evaluate how humans actually use and challenge external decision records. IV. Identify failure modes, deployment boundaries and conditions requiring abstention or escalation.
