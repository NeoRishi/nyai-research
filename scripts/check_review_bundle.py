"""Extract and run the review archive alone using Python's standard library only."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    checks = []
    with tempfile.TemporaryDirectory(prefix='nyai-independent-replay-') as temporary:
        with ZipFile(args.archive) as archive:
            for name in archive.namelist():
                path = Path(name)
                if path.is_absolute() or '..' in path.parts:
                    raise ValueError('Unsafe archive member')
            archive.extractall(temporary)
        root = Path(temporary) / 'nyai-reproducibility'
        commands = [['scripts/verify_bundle.py'], ['scripts/demo.py'], ['scripts/verify_agentic.py'],
                    ['-m', 'unittest', 'discover', '-s', 'tests', '-v']]
        for command in commands:
            result = subprocess.run([sys.executable, '-I', '-S', *command], cwd=root,
                                    capture_output=True, text=True)
            if result.returncode:
                print(result.stdout)
                print(result.stderr)
                raise SystemExit(result.returncode)
            checks.append({'command': 'python3 ' + ' '.join(command), 'status': 'PASS'})
        print(json.dumps({'status': 'PASS', 'mode': 'Fresh temporary extraction; isolated Python; third-party site packages disabled',
                          'checks': checks,
                          'limits': 'Runs recorded synthetic experiment only; not independent human validation or a cloud deployment'}, indent=2))
