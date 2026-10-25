"""Write the protocol and immutable input/code hashes BEFORE first pilot execution."""
import datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
paths=['scripts/run_pilot.py','src/nyai_research/evaluate.py','data/fixtures/120_synthetic_cases.jsonl']
out=dict(frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    status='Timestamped local protocol freeze, not an external preregistration',
    model='gpt-6-luna',temperature=0,max_completion_tokens=512,seed_for_request_order=20261025,
    arms=['baseline','checklist','structured'],cases=120,
    primary='Descriptive agreement with UNREVIEWED design labels; no confirmatory efficacy test',
    baseline_control='Checklist controls some extra instruction effects; token lengths are reported and are not exactly matched',
    metrics=['3-way template agreement','violation recall versus template','violation false-positive rate versus template','invalid responses','tokens','latency','paired disagreements'],
    exclusions='None; errors count as nonmatches. No failed response is silently discarded.',
    statistics='No inferential interval for correlated unreviewed templates. Do not treat 120 variants as 120 independent draws.',
    heldout='Original development/heldout field retained, but all primary results are exploratory harness diagnostics. No source-disjoint validation claimed.',
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
target=ROOT/'experiments/protocol_freeze.json'
if target.exists():raise SystemExit('Freeze already exists; preserve history instead of overwriting')
target.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
