"""Exact registry transcription check against private XLSX, with no workbook export."""
import argparse,datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('workbook',type=Path);p.add_argument('--latest',type=Path);a=p.parse_args()
    import openpyxl
    w=openpyxl.load_workbook(a.workbook,read_only=True,data_only=True)
    checks=[]
    for sheet,registry,columns in [('74_Policy','vcim_policy_registry.json',['id','order','gate','trigger','required_behavior','boundary','status']),('68_Epistemics','vcim_epistemics_registry.json',['id','layer','warrant','allowed_use','prohibited_inference','registry'])]:
        w[sheet].reset_dimensions()
        actual={r[0]:(i,list(r)) for i,r in enumerate(w[sheet].values,1) if r and r[0] and str(r[0]).startswith(('POL-','EP-'))}
        for r in json.loads((ROOT/'data/fixtures'/registry).read_text())['rows']:
            row,values=actual[r['id']]
            mismatch=[col for i,col in enumerate(columns) if col in r and r[col]!=values[i]]
            checks.append(dict(id=r['id'],sheet=sheet,cell_row=row,matches=not mismatch,mismatched_fields=mismatch))
    out=dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        review_type='Automated exact transcription check; not substantive or independent human validation',
        source_sha256=hashlib.sha256(a.workbook.read_bytes()).hexdigest(),registry_rows=checks)
    policies={r['id']:r for r in json.loads((ROOT/'data/fixtures/vcim_policy_registry.json').read_text())['rows']}
    epistemics={r['id']:r for r in json.loads((ROOT/'data/fixtures/vcim_epistemics_registry.json').read_text())['rows']}
    case_checks=[]
    for line in (ROOT/'data/fixtures/120_synthetic_cases.jsonl').read_text().splitlines():
        c=json.loads(line);key=c['policy_id']
        if key in policies:
            r=policies[key];match=c['reference_requirement']==r['required_behavior'] and c['reference_boundary']==r['boundary']
        else:
            r=epistemics[key];match=c['reference_requirement']==r['allowed_use'] and c['reference_boundary']==r['prohibited_inference']
        case_checks.append(dict(case_id=c['case_id'],source_rule=key,reference_text_matches=match,label_verified=False))
    out['fixture_reference_checks']=case_checks
    if a.latest:
        w2=openpyxl.load_workbook(a.latest,read_only=True,data_only=True)
        out['latest_copy_relevant_sheets_equal']={}
        for n in ['68_Epistemics','74_Policy','78_NyAI','61_Explanation_Contract']:
            w[n].reset_dimensions();w2[n].reset_dimensions()
            norm=lambda s:[tuple(v for v in r if v is not None) for r in s.values if any(v is not None for v in r)]
            out['latest_copy_relevant_sheets_equal'][n]=norm(w[n])==norm(w2[n])
        out['normalization_note']='Ignore empty cells/rows; latest workbook has formatted trailing rows and omits dimensions.'
    (ROOT/'results/vcim_source_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Verified transcription rows',sum(c['matches'] for c in checks),'/',len(checks))
