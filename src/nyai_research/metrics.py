"""Evaluation report: observed paired performance on human-reviewed cases only.
Unreviewed synthetic fixture labels are not treated as validation evidence.
"""
import json
from collections import defaultdict,Counter
from .evaluate import read_jsonl

def metric_rows(judgments, annotations):
    labels={x['case_id']:x['reviewed_label'] for x in annotations
       if x.get('review_status')=='verified' and x.get('reviewed_label') in {'compliant','violation','insufficient'}}
    by=defaultdict(list)
    for j in judgments:
        if j.get('case_id') in labels and j.get('label') in {'compliant','violation','insufficient'}:
            by[j['condition']].append((j['label'],labels[j['case_id']]))
    out={}
    for cond,pairs in by.items():
        tp=sum(a=='violation' and b=='violation' for a,b in pairs)
        fp=sum(a=='violation' and b!='violation' for a,b in pairs)
        fn=sum(a!='violation' and b=='violation' for a,b in pairs)
        tn=sum(a!='violation' and b!='violation' for a,b in pairs)
        out[cond]={'n_verified':len(pairs),'accuracy':sum(a==b for a,b in pairs)/len(pairs),
          'violation_precision':tp/(tp+fp) if tp+fp else None,
          'violation_recall':tp/(tp+fn) if tp+fn else None,
          'violation_false_positive_rate':fp/(fp+tn) if fp+tn else None,
          'tp':tp,'fp':fp,'fn':fn,'tn':tn}
    return out

def main(judgments_path,annotation_path,out_path):
    judgments=list(read_jsonl(judgments_path));annotations=list(read_jsonl(annotation_path))
    report=metric_rows(judgments,annotations)
    result={'status':'VERIFIED LABELS ONLY; comparison is prompt protocol, not product efficacy',
            'scores':report,'n_judgments':len(judgments),'n_verified_annotations':sum(x.get('review_status')=='verified' for x in annotations),
            'caveats':['Reviewer could be biased; blind independent annotation recommended.',
              'Synthetic template cases are not independent model outputs.',
              'No human-oversight or catastrophic-risk outcome measured.',
              'Paired protocol prompts are not equal-length; attribution remains uncertain.']}
    with open(out_path,'w') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--judgments',required=True)
    p.add_argument('--annotations',default='data/annotations/reviewed_labels.jsonl')
    p.add_argument('--output',default='results/metrics.json');a=p.parse_args()
    main(a.judgments,a.annotations,a.output)
