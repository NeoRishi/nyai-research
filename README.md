# NyAI research

Evidence validation and checkable AI oversight. Preliminary research pilot, 25 October 2026.

**The experiments do not establish an improvement over a competent model baseline.**

- On 120 **unreviewed synthetic candidates**, ordinary, checklist and NyAI-style structured prompts matched template labels on **96, 92 and 84** cases. All found all 49 template violations. Six truncated responses remain counted as nonmatches.
- On 24 **synthetic action-policy cases**, both the API model and the new executable contract matched a separately coded oracle on **24/24**. These easy cases have a ceiling effect.
- There are **360 actual API audit responses and 24 actual generated action decisions**. The candidate inputs and expected labels remain clearly distinguished from those responses.
- There are **zero independent human-reviewed labels** and no measured human-oversight benefit.

Start with [the work sample](docs/work-sample.md), [verification status](docs/verification-status.md), [implementation limits](docs/implementation-notes.md), and [the research plan](docs/research-plan.md). The standalone PDF is in `output/pdf/`.

## Reproduce the recorded results without credentials

Python 3.11 or later; no external packages are required for these commands:

```bash
python -m unittest discover -s tests -v
python scripts/summarize_pilot.py
python scripts/verify_agentic.py
PYTHONPATH=src python -m nyai_research.metrics \
  --judgments results/template_pilot.jsonl \
  --output results/human_verified_metrics.json
python scripts/verify_artifacts.py
```

The human-reviewed metrics correctly return an empty score table. Template agreement is intentionally computed by a separately labelled descriptive path. Replays use stored API responses and never incur charges. Dataset and model outputs must not be silently relabelled after outcome inspection.

## Live reruns

Install `requirements-live.lock.txt` into a local virtual environment. Keep credentials in a protected local file outside the repository. Then run:

```bash
python scripts/run_pilot.py --env /path/to/local.env --output /path/to/new_run.jsonl
```

The runner resumes by case, condition and input/prompt hashes. For a new experiment use a new output file; it will not replace the recorded pilot. The recorded protocol uses the provider's default temperature of one because this model rejects temperature zero. Model alias and stochastic output are not immutable. Stored raw outputs and the failed first attempt are retained with a protocol amendment. The starter `evaluate.py` is retained for provenance; the recorded experiment uses `scripts/run_pilot.py`.

The agentic generator is resume-safe and will not repeat existing responses. Before new live runs, freeze a new protocol and output path rather than editing existing results. API costs are user-billed; token usage is recorded, monetary totals are not inferred.

## Existing code and infrastructure

[NyAI v1](https://github.com/NeoRishi/nyai-dashboard) and [GraphRAG](https://github.com/NeoRishi/vedic-graphrag) remain unchanged. Pinned source files are reused under `vendor/`; see [provenance](vendor/PROVENANCE.md). v1's ordinal evidence weights and seven-day heuristic remain visible but are not endorsed as universal philosophical rules.

Read-only audits found 2,797 readable Markdown files, 2,615 unique exact byte hashes, and 78 skipped cloud placeholders across the three supplied folders. The private file manifest stays local. Aura contains 100 Notes and 1,976 Chunks, with its vector index online. No graph writes, embedding refresh or new infrastructure was needed. Source and link markers are not treated as truth.

The 18 policy/epistemic registry rows and all 120 fixture reference fields matched the VCIM workbook text. Relevant sheets in the latest workbook copy match after excluding empty formatting. This is transcription verification, not clinical or empirical validation.

## Review and next step

The 24 real-output review worksheet is `data/annotations/live_output_review.csv`; human labels are blank. Keep its mapping key away from reviewers until annotations freeze. The starter's 120-case review queue remains separate. The next study needs independently authored source-backed cases and independent reviewer labels before any efficacy claim.

Application logistics and CV work are deferred at the user's request. The research report is a draft for applicant review, not an application submission.

## AI assistance

The applicant supplied the framing, existing projects and private sources. AI assisted inspection, code, cases, experiment orchestration, analysis and documentation. The API model generated recorded judgments and decisions. No assistant annotation is called independent human review. Original starter documents are preserved under `docs/archive/` and `WORK_HANDOFF.md`.
