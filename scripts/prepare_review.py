"""Creates non-deceptive review queue; template labels are hidden from reviewers."""
import csv,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
src=root/'data/fixtures/120_synthetic_cases.jsonl'
out=root/'data/annotations/review_queue.csv'
with src.open(encoding='utf-8') as f:cases=[json.loads(x) for x in f if x.strip()]
cols=['case_id','scenario','reference_requirement','reference_boundary','candidate_response','reviewed_label','reviewer_id','review_notes','review_status']
with out.open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for c in cases:w.writerow({k:c.get(k,'') if k not in {'reviewed_label','reviewer_id','review_notes','review_status'} else '' for k in cols})
print(out,'rows',len(cases))
