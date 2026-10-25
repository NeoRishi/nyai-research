# NyAI Research — Evidence, Warrant, Defeater, Correction

**Status (2026-10-25): preliminary research scaffold — NOT a validated AI safety system.**

A reproducible, small-scale investigation of whether explicit evidence/claim decomposition, scope checks, defeaters, and traceable corrections can improve oversight of AI-generated decisions and explanations. Prepared as a work-sample companion for a potential MATS Residency **Bridge** application.

## Existing implementations (preserved, not forked)

1. [NyAI v1](https://github.com/NeoRishi/nyai-dashboard): FastAPI/React rule-based demonstration of source classification, defeaters, belief revision and five-step traces; five constructed scenarios and a deliberately naive comparison agent. The v1 universal `PRAMANA_STRENGTH` ranking is a **design heuristic, not settled Nyāya philosophy**.
2. [Vedic GraphRAG](https://github.com/NeoRishi/vedic-graphrag): Python Obsidian ingestion, Neo4j `Note`/`Chunk`/`Source` relationships, vector retrieval, graph reranking, source citations. Its example demonstrates retrieval differences, not general reasoning correctness.
3. [NeoRishi VCIM v3.0](not-republished): private workbook whose `68_Epistemics`, `74_Policy`, `78_NyAI`, `61_Explanation_Contract`, `41_Evidence_Claims`, and `09_Personalization_Rules` informed evaluation fixtures and audit contracts. Specification != independently validated safety evidence.

## What actually exists in this repo

- **120 synthetic template-derived evaluation fixtures** from VCIM v3, *not* 120 independently sampled model answers. Each carries the original rule ID and an **unreviewed** label. Labels have not been independently verified.
- A blinded-ish review CSV that hides template labels, an import gate requiring reviewer identity, and metrics code that **will not score unreviewed fixtures**.
- A paired baseline-vs-structured prompt protocol for model-as-judge experiments. This is a *prompt experiment*; it does **not** measure human oversight and should not be claimed to validate NyAI as a system.
- Optional read-only integration probes for NyAI v1's original scenarios and the existing Neo4j GraphRAG.
- A privacy-preserving Markdown file manifest script. No private vault content, cloud database secrets or proprietary full VCIM workbook are included.

## Reproduce without secrets

```bash
python -m unittest discover -s tests -v
python scripts/prepare_review.py
# Edit data/annotations/review_queue.csv and fill reviewed_label, reviewer_id, review_notes
python scripts/import_review.py
```

## Run paired LLM experiment *after reviewing the fixtures*

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[llm,graph]'
export OPENAI_API_KEY='YOUR_KEY_IN_LOCAL_SHELL' # never commit
export OPENAI_CHAT_MODEL='YOUR_AVAILABLE_CHAT_MODEL'
PYTHONPATH=src python -m nyai_research.evaluate --split development --limit 10
# Inspect errors and freeze protocol before testing held-out cases
PYTHONPATH=src python -m nyai_research.evaluate --split heldout
PYTHONPATH=src python -m nyai_research.metrics --judgments results/paired_judgments.jsonl
```

A metric is generated only for fixtures with a *verified reviewer label*. All model-as-judge runs, costs and model settings must be documented. Stronger evidence requires independently authored holdout cases and/or actual human participants.

## Generate real (unlabelled) model responses

```bash
PYTHONPATH=src python scripts/generate_model_responses.py --limit 10
# Label them independently before computing research metrics.
```

This is distinct from the 120 synthetic response fixtures.

## Use existing repositories locally

```bash
# In a parent directory on your machine:
git clone https://github.com/NeoRishi/nyai-dashboard.git
git clone https://github.com/NeoRishi/vedic-graphrag.git
git clone https://github.com/NeoRishi/nyai-research.git # once created
cd nyai-research
python integrations/nyai_v1_smoke.py --repo ../nyai-dashboard
# Existing GraphRAG needs its own Neo4j .env and API key configured
python integrations/graphrag_probe.py 'What does the source say about pramana?' --repo ../vedic-graphrag
# Desktop vault manifest (read-only, no cloud sync):
python scripts/ingest_manifest.py --vault ~/Desktop/my-knowledge-base
```

**CAUTION:** `vedic-graphrag/import_wiki.py` and `build_chunks.py` can modify data in Neo4j; do **not** run them against a production instance without backup, schema review and dry-run. The research adapter `graphrag_probe.py` only queries Neo4j.

## Research limitations

- 120 template variants are correlated and easy to overfit; no effective-N or external validity claim is made.
- VCIM policies are product specifications; a rule can be internally consistent without clinical/empirical validation.
- Numeric universal source rankings in v1 conflict with VCIM v3's claim-specific evidential warrant rule; they are retained in the original repository for honest comparison.
- Cited source files and markdown wikilinks are not independently validated evidence.
- Neither the experiment nor the prototypes establish mitigation of catastrophic AI risk. This is an early investigation toward **checkable oversight**.
- Any participant study requires appropriate consent and ethics review where applicable.

## Research artifacts

- `docs/research-plan.md`: falsifiable question and theory of change
- `docs/methodology.md`: experiment and leakage controls
- `docs/repository-audit.md`: verified assets, reuse and limitations
- `docs/mats-application-checklist.md`: current MATS Bridge application requirements
- `docs/work-sample.md`: standalone work-sample framing

## Provenance and disclosure

Original NyAI and GraphRAG repositories are attributed to NeoRishi. This independent research scaffold was prepared with ChatGPT assistance on 2026-10-25. Automated generated fixtures and assistant-authored code are clearly marked as such; attribution and AI-use disclosure should accompany applications and submissions.

## Work-mode / desktop handoff

See [`WORK_HANDOFF.md`](WORK_HANDOFF.md) for repository publication instructions, read-only Neo4j verification, the user's `~/Desktop/my-knowledge-base` handoff, priority order and MATS application acceptance criteria. The new GitHub repository should start **private** because it contains specification-derived fixtures from proprietary VCIM v3.
