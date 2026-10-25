# Work sample: From NyAI to checkable AI reasoning

**Applicant:** Hrishikesh Wattamwar (NeoRishi)
**Type:** Independent technical prototype + early research plan
**Status:** Research scaffold, synthetic fixtures, no validated empirical effect reported

## Problem
AI assistants can provide polished recommendations with weak evidence, misleading citations or missing decision gates. In high-delegation settings, a human may mistake an explanation for verification. I am exploring whether explicit evidence warrants, defeaters and revision conditions make such failures easier to detect.

## What I actually built previously
In NyAI v1 I implemented a working FastAPI/React demonstrator with a deterministic reasoning pipeline: pramāṇa classification, claim checks, belief revision and an inspectable five-part trace. It has five hand-constructed scenarios and a deliberately naive comparator. Separately I built a Neo4j GraphRAG proof of concept for my interlinked Markdown corpus, with source citation nodes and graph-aware passage selection. These are real implementations; neither is a validated alignment technique.

## What I did for this research transition
I separated retrieval, epistemic validation and evaluation. I mapped VCIM v3's claim-specific warrants and policy precedence to synthetic audit fixtures, prepared a repeatable, blinded review workflow and a baseline-vs-structured auditing protocol. I documented a conceptual flaw in v1: a rigid four-category evidence-strength hierarchy cannot be treated as universal philosophical or empirical truth. All synthetic labels remain unreviewed until an independent review is completed.

## New research question
Can explicit claim/warrant/defeater decomposition improve error detection or appropriate reliance, controlling for evidence access, baseline strength and human review costs?

## Evidence available today
- Public original prototype and source code: https://github.com/NeoRishi/nyai-dashboard
- GraphRAG implementation and a worked retrieval example: https://github.com/NeoRishi/vedic-graphrag
- New evaluation scaffold: `data/fixtures`, `src`, `tests`, `docs` (once published)
- NOT available yet: independently annotated corpus, verified accuracy gains, human study or established reduction in catastrophic risk.

## Why I am seeking MATS
The work's strongest potential is in AI oversight rather than a generic wellness chatbot. I would value a research environment that forces rigorous experimental baselines, collaboration with AI safety researchers, evaluation on more capable systems, and clearer threat models. My goal would be to discover whether the approach is useful, where it fails and whether it justifies a longer-term research program.

## Disclosure
The new research scaffold, documentation and synthetic fixtures were prepared with ChatGPT assistance in October 2026; previous NyAI v1 README discloses Claude assistance. I will distinguish independently authored intellectual decisions, assisted implementation and evidence obtained from actual experiments in the application.
