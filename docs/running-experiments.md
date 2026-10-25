# Running and reproducing experiments

For an immediate offline demonstration, run `python3 scripts/demo.py` from the repository. It exercises the actual contract engine with frozen synthetic facts and replays one recorded model response. It makes no API calls, database queries or external changes.

## Replay the recorded pilot

Python 3.11 or later is sufficient; these commands require no external packages or credentials:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/summarize_pilot.py
python3 scripts/verify_agentic.py
PYTHONPATH=src python3 -m nyai_research.metrics \
  --judgments results/template_pilot.jsonl \
  --output results/human_verified_metrics.json
python3 scripts/verify_artifacts.py
```

These scoring commands rewrite their derived summary files using stored outputs. The human-reviewed score table is deliberately empty because no independent human labels exist. The separate descriptive path reports agreement with unreviewed template labels. Invalid outputs remain counted as nonmatches.

## Live API experiments

Install `requirements-live.lock.txt` in a local virtual environment. Keep credentials in a protected local file outside the repository:

```bash
python3 scripts/run_pilot.py --env /path/to/local.env --output /path/to/new_run.jsonl
```

The runner resumes by case, condition and input/prompt hashes. Use a new output file for a new run; preserve the recorded pilot. Live runs incur charges. Freeze a new protocol before changing prompts, settings or cases. The recorded experiment uses the provider's default temperature of one because this model rejects temperature zero. The mutable model alias and stochastic text are not guaranteed to reproduce exactly.

The separate agentic generator is resume-safe and will not repeat existing responses. It currently writes to its fixed recorded-output path; add a new output path and protocol version before using it for another experiment. The starter `evaluate.py` and `generate_model_responses.py` are retained for provenance; the recorded experiments used `run_pilot.py` and `generate_agentic_responses.py`.

The failed temperature-zero attempt, subsequent protocol amendment, and six truncated responses are preserved. Do not silently replace truncations or change design labels after inspecting outcomes. Token usage is recorded; monetary costs were not inferred from an unverified price schedule.

## Source and infrastructure audits

The corpus and read-only Aura audit commands, results, and limitations are documented in [the repository audit](repository-audit.md). Private workbook transcription can be checked with `scripts/verify_vcim.py` when the source file is available. No private source content or credentials are needed for replaying the public-facing experiment artifacts in this private repository.

The upstream importer and chunk builder modify graph data. They are not part of this demo or reproducibility workflow.
