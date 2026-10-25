"""Inspect a reviewer-supplied JSON runtime record; no tools or API calls."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from nyai_research.contracts import adjudicate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path, help='JSON object containing runtime facts')
    args = parser.parse_args()
    try:
        state = json.loads(args.record.read_text())
    except (OSError, ValueError):
        parser.error('Cannot read a valid JSON record')
    if type(state) is not dict:
        parser.error('The runtime record must be a JSON object')
    print(json.dumps(adjudicate(state), indent=2))
