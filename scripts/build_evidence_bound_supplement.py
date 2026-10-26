"""Build allowlisted private review packages; never publish or change repo privacy."""
import hashlib
import json
import random
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'dist/evidence-bound-reproducibility'
PRIMARY = 'results/evidence_bound_v1_final'
ALLOW = [
    'src/nyai_research/__init__.py', 'src/nyai_research/evidence_bound.py',
    'scripts/run_evidence_bound.py', 'tests/test_evidence_bound.py',
    'experiments/evidence_bound_v1/protocol.json', 'experiments/evidence_bound_v1/cases.json',
    'experiments/evidence_bound_v1/freeze.json', 'experiments/evidence_bound_v1/amendment_01.json',
    'experiments/evidence_bound_v1/amendment_02.json',
    PRIMARY+'/records.jsonl', PRIMARY+'/summary.json', PRIMARY+'/manifest.json', PRIMARY+'/review_queue.csv',
    'docs/evidence-bound-work-sample.md', 'docs/related-work-2026-10-27.md',
]
README = '''# NyAI evidence-bound study: private review candidate

This package contains only fictional evaluation artifacts and the new bounded study.
It excludes the private knowledge base, VCIM excerpts, credentials and Git history.
It is prepared for author review; no public release or new reuse licence is implied.

Python3.10+; standard library only. From this folder:

```
python3 -m unittest discover -s tests -v
python3 scripts/run_evidence_bound.py --phase verify --output results/evidence_bound_v1_final
python3 scripts/run_evidence_bound.py --phase run --output /tmp/nyai-independent-replay
```

Use a new output directory for each run. Compare summary counts; process timings,
platform metadata and traceback formatting can differ. No network/API/database is used.

The primary study has24 correlated constructed scenarios,33 local grader executions,
five reference accepts and19 withholds. Behavioral strings are fictional, not model
outputs. Reference rules and cases share an AI author. The two complete conditions
share one acceptance predicate and tie by construction. No reviewer benefit is proven.

All first-run/first-amendment archives remain in the private research repository.
This supplement includes the final amended archive and the full amendment history.
Temporary host path prefixes in stderr are replaced with <TEMP>; the derived record
hash and export provenance are updated. Original raw outputs remain private/unmodified.
Hash manifests establish integrity relative to this package, not trusted attestation.

For independent annotation, use the separate reviewer packet before this report or
source files, which expose our policy interpretation and method decisions. Record
ambiguity and disagreements. No external reviewer has yet completed annotations.
'''
GUIDE = '''# External technical review: instructions

Please challenge this research rather than endorse it. The policy concerns permission
to endorse a current conclusion, not whether a historical observation was true.
The behavior tables are fictional; execution is real. Host registry and authority
events are trusted within the exercise. A later contrary result need not falsify an
earlier measurement. Mark a policy you consider inappropriate as ambiguous.

Read policy.json, then review_packet.json. For each R-number, enter your identity,
accept/withhold/ambiguous, rationale and any policy objection in review_queue.csv.
Do not force agreement with what you think we intend. State which hashes or results
you actually inspected. Case labels/arm outputs and our answer key are omitted.
This is not fully blinded: raw evidence and constructed defects can reveal intent.

Only after freezing your judgments, request the report and implementation to critique
the rules and baseline choices. You may propose new cases independently of ours.
Return your original worksheet and optional critique to the applicant. This package
does not contact anyone or collect responses automatically. No review is recorded
until a real reviewer supplies dated judgments and agrees to attribution/use.
'''


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(folder, target):
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(folder.rglob('*')):
            if path.is_file(): z.write(path, path.relative_to(folder))


def main():
    if DEST.exists(): shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for name in ALLOW:
        out = DEST/name; out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, out)
    original = ROOT/PRIMARY/'records.jsonl'
    # Redact local temporary traceback prefixes without touching grading data.
    text = original.read_text()
    redacted = re.sub(r'/(?:private/)?var/folders/[^"\\\n ]*/nyai-bound-[^/"\\\n ]+', '<TEMP>', text)
    (DEST/PRIMARY/'records.jsonl').write_text(redacted)
    manifest_path = DEST/PRIMARY/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['records_sha256'] = hash_file(DEST/PRIMARY/'records.jsonl')
    manifest['export_transformation'] = dict(original_records_sha256=hash_file(original),
        temporary_stderr_prefixes_redacted=True, original_retained_in_private_repository=True)
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    (DEST/'README.md').write_text(README)
    pdf = ROOT/'output/pdf/NyAI_Evidence_Bound_Oversight_2026-10-27.pdf'
    if pdf.exists(): shutil.copyfile(pdf, DEST/pdf.name)
    export_manifest = {str(p.relative_to(DEST)):hash_file(p) for p in sorted(DEST.rglob('*')) if p.is_file()}
    (DEST/'EXPORT_MANIFEST.json').write_text(json.dumps(export_manifest, indent=2)+'\n')
    archive(DEST, ROOT/'dist/NyAI_Evidence_Bound_Reproducibility_Review_2026-10-27.zip')

    reviewer = ROOT/'dist/evidence-bound-external-review'
    if reviewer.exists(): shutil.rmtree(reviewer)
    reviewer.mkdir()
    records = [json.loads(line) for line in original.read_text().splitlines()]
    random.Random(20261027).shuffle(records)
    packet, key = [], []
    for i,r in enumerate(records, 1):
        review_id = f'R{i:02d}'
        packet.append(dict(review_id=review_id, current_state=r['packet']))
        key.append(dict(review_id=review_id, case_id=r['case_id'], reference_accept=r['reference_accept']))
    (reviewer/'review_packet.json').write_text(json.dumps(packet, indent=2)+'\n')
    # Reviewer evidence can also contain failed-run temporary paths.
    p = reviewer/'review_packet.json'; p.write_text(re.sub(r'/(?:private/)?var/folders/[^"\\\n ]*/nyai-bound-[^/"\\\n ]+', '<TEMP>', p.read_text()))
    (reviewer/'policy.json').write_text((ROOT/'experiments/evidence_bound_v1/protocol.json').read_text())
    (reviewer/'README.md').write_text(GUIDE)
    (reviewer/'review_queue.csv').write_text('review_id,reviewer,decision,rationale,ambiguity,review_date\n'+''.join(f'{r["review_id"]},,,,,\n' for r in packet))
    key_path = ROOT/'private_audit/evidence_bound_review_key.json'; key_path.parent.mkdir(exist_ok=True)
    key_path.write_text(json.dumps(key, indent=2)+'\n')
    archive(reviewer, ROOT/'dist/NyAI_External_Reviewer_Packet_2026-10-27.zip')
    print('Prepared reproducibility and external-review ZIPs in dist/. No publication performed.')


if __name__ == '__main__': main()
