"""Evaluation report: observed paired performance on human-reviewed cases only.
Unreviewed synthetic fixture labels are not treated as validation evidence.
"""
import json
from .evaluate import read_jsonl

VALID_LABELS = {'compliant', 'violation', 'insufficient'}


def _valid_label(value):
    return type(value) is str and value in VALID_LABELS


def _reviewed_labels(annotations):
    """The explicit review flag is required; template labels are never a fallback."""
    labels = {}
    for annotation in annotations:
        if annotation.get('review_status') != 'verified' or not _valid_label(annotation.get('reviewed_label')):
            continue
        case_id, label = annotation['case_id'], annotation['reviewed_label']
        if case_id in labels and labels[case_id] != label:
            raise ValueError('Conflicting reviewed labels require adjudication: ' + str(case_id))
        labels[case_id] = label
    return labels


def metric_rows(judgments, annotations, conditions=None):
    """Score every eligible reviewed case for each condition, including failures.

    Missing rows and invalid/error responses are accuracy nonmatches. Recall uses
    all reviewed violation cases. False-positive rate uses all reviewed nonviolation
    cases; failures are reported separately and are not credited as true negatives.
    Precision is conditional on producing a violation prediction. Supply conditions
    explicitly to represent an arm with no recorded rows at all. No scoring function
    can establish whether the supplied annotation's human-review flag is authentic.
    """
    judgments = list(judgments)
    labels = _reviewed_labels(annotations)
    if not labels:
        return {}
    arms = sorted(set(conditions) if conditions is not None else {
        j['condition'] for j in judgments if j.get('condition') is not None})
    by = {}
    for judgment in judgments:
        key = (judgment.get('condition'), judgment.get('case_id'))
        if key[0] not in arms or key[1] not in labels:
            continue
        if key in by:
            raise ValueError('Duplicate case/condition judgment: ' + str(key))
        by[key] = judgment
    out={}
    for cond in arms:
        pairs = []
        missing = invalid = errors = 0
        failed_violation = failed_nonviolation = 0
        for case_id, truth in labels.items():
            judgment = by.get((cond, case_id))
            if judgment is None:
                prediction = None
                missing += 1
            elif judgment.get('error') or judgment.get('error_type'):
                prediction = None
                errors += 1
            elif not _valid_label(judgment.get('label')):
                prediction = None
                invalid += 1
            else:
                prediction = judgment['label']
            if prediction is None:
                failed_violation += truth == 'violation'
                failed_nonviolation += truth != 'violation'
            pairs.append((prediction, truth))
        tp=sum(a=='violation' and b=='violation' for a,b in pairs)
        fp=sum(a=='violation' and b!='violation' for a,b in pairs)
        fn=sum(a!='violation' and b=='violation' for a,b in pairs)
        tn=sum(a in VALID_LABELS and a!='violation' and b!='violation' for a,b in pairs)
        negatives = sum(b != 'violation' for _, b in pairs)
        failures = missing + invalid + errors
        out[cond]={'n_verified':len(pairs),'accuracy':sum(a==b for a,b in pairs)/len(pairs),
          'violation_precision':tp/(tp+fp) if tp+fp else None,
          'violation_recall':tp/(tp+fn) if tp+fn else None,
          'violation_false_positive_rate':fp/negatives if negatives else None,
          'tp':tp,'fp':fp,'fn':fn,'tn':tn,
          'n_valid_predictions':len(pairs)-failures,
          'prediction_coverage':(len(pairs)-failures)/len(pairs),
          'failure_count':failures,'missing_count':missing,'invalid_count':invalid,
          'error_count':errors,'failed_violation_cases':failed_violation,
          'failed_nonviolation_cases':failed_nonviolation}
    return out

def main(judgments_path,annotation_path,out_path):
    judgments=list(read_jsonl(judgments_path));annotations=list(read_jsonl(annotation_path))
    report=metric_rows(judgments,annotations)
    result={'status':'VERIFIED LABELS ONLY; comparison is prompt protocol, not product efficacy',
            'scores':report,'n_judgments':len(judgments),'n_verified_annotations':len(_reviewed_labels(annotations)),
            'caveats':['Reviewer could be biased; blind independent annotation recommended.',
              'Synthetic template cases are not independent model outputs.',
              'No human-oversight or catastrophic-risk outcome measured.',
              'Paired protocol prompts are not equal-length; attribution remains uncertain.',
              'Missing, invalid and errored predictions remain in primary accuracy and recall denominators.',
              'False-positive rate includes all reviewed nonviolations in its denominator; failures are not credited as true negatives.',
              'Completely absent arms require the optional conditions argument to metric_rows; otherwise conditions are inferred from recorded rows.']}
    with open(out_path,'w') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--judgments',required=True)
    p.add_argument('--annotations',default='data/annotations/reviewed_labels.jsonl')
    p.add_argument('--output',default='results/metrics.json');a=p.parse_args()
    main(a.judgments,a.annotations,a.output)
