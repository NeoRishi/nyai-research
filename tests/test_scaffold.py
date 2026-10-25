import json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nyai_research.evaluate import read_jsonl,parse_audit,audit_payload
from nyai_research.metrics import metric_rows
class Checks(unittest.TestCase):
 def setUp(self):self.cases=list(read_jsonl(ROOT/'data/fixtures/120_synthetic_cases.jsonl'))
 def test_number_ids_splits(self):
  self.assertEqual(len(self.cases),120)
  self.assertEqual(len(set(c['case_id'] for c in self.cases)),120)
  self.assertTrue(all(c['review_status']=='unreviewed' for c in self.cases))
  self.assertGreater(sum(c['split']=='heldout' for c in self.cases),40)
 def test_no_gold_leakage(self):
  self.assertNotIn('gold_label',audit_payload(self.cases[0]))
 def test_json_parse(self):
  self.assertEqual(parse_audit('{"label":"violation","reason":"violates gate"}')['label'],'violation')
 def test_metrics_ignore_unreviewed(self):
  rows=[{'case_id':self.cases[0]['case_id'],'condition':'baseline','label':'compliant'}]
  labels=[{'case_id':self.cases[0]['case_id'],'review_status':'unreviewed','reviewed_label':'compliant'}]
  self.assertEqual(metric_rows(rows,labels),{})
 def test_label_distribution(self):
  self.assertEqual(set(c['gold_label'] for c in self.cases),{'compliant','violation','insufficient'})
if __name__=='__main__':unittest.main()
