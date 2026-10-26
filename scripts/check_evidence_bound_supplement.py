"""Verify the allowlisted review ZIP in isolation, without private dependencies."""
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/'dist/NyAI_Evidence_Bound_Reproducibility_Review_2026-10-27.zip'


def main():
    with tempfile.TemporaryDirectory(prefix='nyai-review-isolation-') as folder:
        path = Path(folder)
        with zipfile.ZipFile(ARCHIVE) as archive:
            for name in archive.namelist():
                parts = Path(name).parts
                if name.startswith('/') or '..' in parts:
                    raise ValueError('Unsafe archive member')
            archive.extractall(path)
        manifest = json.loads((path/'EXPORT_MANIFEST.json').read_text())
        actual = {str(p.relative_to(path)) for p in path.rglob('*') if p.is_file()}
        if actual != set(manifest) | {'EXPORT_MANIFEST.json'}:
            raise ValueError('Archive members differ from allowlisted manifest')
        for name, expected in manifest.items():
            content = (path/name).read_bytes()
            if hashlib.sha256(content).hexdigest() != expected:
                raise ValueError('Export digest mismatch: '+name)
            if not name.endswith('.pdf'):
                text = content.decode()
                if any(secret in text for secret in ('neo4j+s://', '/Users/neorishi/', '/var/folders/', 'OPENAI_API_KEY=')):
                    raise ValueError('Private path or credential-shaped field: '+name)
        commands = [
            ['-m','unittest','discover','-s','tests','-v'],
            ['scripts/run_evidence_bound.py','--phase','verify','--output','results/evidence_bound_v1_final'],
            ['scripts/run_evidence_bound.py','--phase','run','--output',str(path/'independent-replay')],
        ]
        for arguments in commands:
            completed = subprocess.run([sys.executable,*arguments], cwd=path, capture_output=True, text=True)
            if completed.returncode:
                raise RuntimeError(completed.stdout+'\n'+completed.stderr)
        reference = json.loads((path/'results/evidence_bound_v1_final/summary.json').read_text())
        replay = json.loads((path/'independent-replay/summary.json').read_text())
        if reference != replay:
            raise ValueError('Isolated rerun summary differs')
    reviewer_path = ROOT/'dist/NyAI_External_Reviewer_Packet_2026-10-27.zip'
    with zipfile.ZipFile(reviewer_path) as archive:
        data = archive.read('review_packet.json').decode()
        if any(key in data for key in ('reference_accept', 'design_expected', 'complete_revalidation_with_records', '/Users/neorishi/', '/var/folders/')):
            raise ValueError('Reviewer packet contains answer fields or private paths')
        if len(json.loads(data)) != reference['scenarios']:
            raise ValueError('Reviewer packet count differs')
    print('PASS: export digests, exact members, path scan, isolated tests/verification, full executable rerun, identical summaries and unlabelled reviewer packet. Not independent human validation.')


if __name__ == '__main__': main()
