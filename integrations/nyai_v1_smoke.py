"""Run ORIGINAL NyAI 1.0 scenarios without copying or rewriting its source.
Clone https://github.com/NeoRishi/nyai-dashboard to ../nyai-dashboard first.
"""
import argparse,sys,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',default='../nyai-dashboard');a=p.parse_args()
root=Path(a.repo).resolve();base=root/'backend'
if not base.exists():raise SystemExit(f'Cannot find existing NyAI repo at {root}')
sys.path.insert(0,str(base))
from nyai.scenarios import run_all_scenarios
results=run_all_scenarios()
print(json.dumps({'count':len(results),'divergence_count':sum(bool(r.get('diverges')) for r in results)},indent=2))
