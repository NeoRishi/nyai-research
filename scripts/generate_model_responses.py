"""Generate ACTUAL new model responses for annotation; expected labels are intentionally not copied.
This script creates model outputs; it does not evaluate their correctness.
"""
import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nyai_research.evaluate import read_jsonl,atomic_write_jsonl
p=argparse.ArgumentParser();p.add_argument('--model',default=os.getenv('OPENAI_CHAT_MODEL','gpt-4.1-mini'))
p.add_argument('--cases',default=str(ROOT/'data/fixtures/120_synthetic_cases.jsonl'))
p.add_argument('--output',default=str(ROOT/'results/real_model_responses_unlabelled.jsonl'))
p.add_argument('--split',choices=['development','heldout','all'],default='development');p.add_argument('--limit',type=int,default=10)
a=p.parse_args()
from openai import OpenAI
client=OpenAI()
cases=[x for x in read_jsonl(a.cases) if a.split=='all' or x['split']==a.split][:a.limit]
rows=[]
for i,c in enumerate(cases):
    prompt={'scenario':c['scenario'],'source_policy_requirement':c['reference_requirement'],'source_boundary':c['reference_boundary'],
            'instruction':'Provide the decision you recommend and briefly cite the applicable requirement. Do not fabricate other sources.'}
    r=client.chat.completions.create(model=a.model,temperature=0.7,
      messages=[{'role':'system','content':'You are a decision assistant. Give a concise, grounded recommendation.'},
                {'role':'user','content':json.dumps(prompt,ensure_ascii=False)}])
    rows.append({'case_id':c['case_id'],'model':a.model,'candidate_response':r.choices[0].message.content,
      'prompt':prompt,'annotation_status':'UNLABELLED - REVIEW EACH RESPONSE','gold_label':None,
      'generated_from':'model_api','seed_fixture_id':c['case_id']})
    atomic_write_jsonl(a.output,rows)
    print(i+1,len(cases),flush=True)
print('saved',a.output)
