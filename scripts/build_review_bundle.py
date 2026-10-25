"""Build a separate allowlisted review archive. Never publish or copy Git history.

Only generic action-contract artifacts are exported, not the proprietary-policy
experiment or its prompts/results. A snapshot can be tested without this repository.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
COPIES = [
    'src/nyai_research/contracts.py',
    'scripts/demo.py',
    'scripts/check_record.py',
    'tests/test_contracts.py',
    'data/fixtures/24_agentic_contract_cases.jsonl',
    'results/agentic_model_responses.jsonl',
    'docs/eu-ai-act-relevance.md',
]


def write(base, relative, text):
    target = base / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def build(destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='nyai-review-build-') as temporary:
        stage = Path(temporary) / 'nyai-reproducibility'
        stage.mkdir()
        provenance = {}
        for relative in COPIES:
            source = ROOT / relative
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            provenance[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
        write(stage, 'src/nyai_research/__init__.py', '"""External decision-contract research prototype."""\n')
        write(stage, 'README.md', (ROOT / 'release_template/README.md').read_text())
        checker_source = (ROOT / 'scripts/verify_agentic.py').read_text()
        tree = ast.parse(checker_source)
        oracle = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'oracle')
        checker = ('"""Separately coded oracle; same AI author, no independent human review."""\n'
                   'import json, sys\nfrom pathlib import Path\n'
                   'ROOT = Path(__file__).resolve().parents[1]\n'
                   "sys.path.insert(0, str(ROOT / 'src'))\n\n" + ast.get_source_segment(checker_source, oracle) + '\n' +
                   (ROOT / 'release_template/verify_agentic_main.py.txt').read_text())
        write(stage, 'scripts/verify_agentic.py', checker)
        write(stage, 'scripts/verify_bundle.py', (ROOT / 'release_template/verify_bundle.py.txt').read_text())
        full = json.loads((ROOT / 'results/agentic_contract_summary.json').read_text())
        selected = {key: full['summary'][key] for key in
                    ['any_evidence', 'permission_only', 'model_api', 'all_contract_gates']}
        write(stage, 'results/expected_contract_summary.json', json.dumps({
            'status': 'FINITE SYNTHETIC CONTRACT RESULT; NO HUMAN OVERSIGHT OUTCOME',
            'summary': selected}, indent=2) + '\n')
        workflow = '''name: Reproduce NyAI contract pilot
on:
  workflow_dispatch:
  push:
  pull_request:
permissions:
  contents: read
jobs:
  reproduce:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Verify snapshot and run synthetic research replay
        run: |
          python scripts/verify_bundle.py
          python scripts/demo.py
          python scripts/verify_agentic.py
          python -m unittest discover -s tests -v
'''
        write(stage, '.github/workflows/reproduce.yml', workflow)
        write(stage, '.gitignore', '__pycache__/\n*.pyc\n.env\n.venv/\n')
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        write(stage, 'PROVENANCE.json', json.dumps({
            'status': 'Publication review candidate; not yet public',
            'experiment_date': '2026-10-25',
            'source_revision_at_export': revision,
            'source_working_tree_may_include_documentation_changes': True,
            'copied_files_sha256': provenance,
            'oracle_function_sha256': hashlib.sha256(ast.get_source_segment(checker_source, oracle).encode()).hexdigest(),
            'export_scope': 'Generic contract and 24 fictional action-policy cases only',
            'excluded': ['private corpus', 'private workbook', 'proprietary-policy fixtures and outputs',
                         'local audit manifests', 'credentials', 'Git history', 'application materials', 'upstream vendored code'],
            'licence_status': 'Select before publication; none newly assigned by this export'}, indent=2) + '\n')
        # The package intentionally includes no arbitrary user files or source credentials.
        files = sorted(p for p in stage.rglob('*') if p.is_file())
        for path in files:
            content = path.read_text()
            if re.search(r'\b(?:sk-[A-Za-z0-9_-]{30,}|gh[pousr]_[A-Za-z0-9]{30,})', content):
                raise ValueError('Potential token found; export halted')
            if '/Users/' in content or '.databases.neo4j.io' in content:
                raise ValueError('Private local path or database endpoint found; export halted')
        manifest = {str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
        write(stage, 'MANIFEST.json', json.dumps({'scope': 'Identity of this review snapshot, not correctness evidence',
                                                 'sha256': manifest}, indent=2) + '\n')
        with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
            for path in sorted(p for p in stage.rglob('*') if p.is_file()):
                entry = ZipInfo('nyai-reproducibility/' + str(path.relative_to(stage)), date_time=(2026, 10, 25, 0, 0, 0))
                entry.compress_type = ZIP_DEFLATED
                entry.external_attr = 0o644 << 16
                archive.writestr(entry, path.read_bytes())
        summary = {'archive': destination.name,
                   'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                   'files': len(manifest) + 1, 'published': False,
                   'scope': '24-case generic contract replay only'}
        print(json.dumps(summary, indent=2))
        return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/NyAI_Reproducibility_Review_2026-10-25.zip')
    args = parser.parse_args()
    build(args.output)
