"""Load human annotated CSV; fail on invalid labels; only explicitly reviewed rows verified."""
import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
src=root/'data/annotations/review_queue.csv'
out=root/'data/annotations/reviewed_labels.jsonl'
valid={'compliant','violation','insufficient'}
records=[]
with src.open(encoding='utf-8',newline='') as f:
 for row in csv.DictReader(f):
  v=row['reviewed_label'].strip().lower()
  if v and v not in valid:raise ValueError(f'Invalid label for {row["case_id"]}: {v}')
  records.append({'case_id':row['case_id'],'reviewed_label':v or None,
                  'review_status':'verified' if v and row['reviewer_id'].strip() else 'unreviewed',
                  'reviewer_id':row['reviewer_id'].strip(),'review_notes':row['review_notes']})
with out.open('w',encoding='utf-8') as f:
 for item in records:f.write(json.dumps(item,ensure_ascii=False)+'\n')
print(out,'verified',sum(x['review_status']=='verified' for x in records),'total',len(records))
