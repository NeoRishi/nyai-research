"""Read-only connectivity and minimal synthetic API probe. Never prints credentials."""
import argparse
import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"vendor/graphrag"))
from import_wiki import read_env

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--env",type=Path,required=True)
    a=p.parse_args()
    env=read_env(a.env)
    out={"checked_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"database_writes":False}
    try:
        from neo4j import GraphDatabase, READ_ACCESS
        assert "8ed83df4" in env["NEO4J_URI"], "Unexpected Aura instance"
        with GraphDatabase.driver(env["NEO4J_URI"],auth=(env["NEO4J_USERNAME"],env["NEO4J_PASSWORD"]),connection_timeout=15) as d:
            d.verify_connectivity()
            with d.session(database=env.get("NEO4J_DATABASE","neo4j"),default_access_mode=READ_ACCESS) as s:
                r=s.run("MATCH (n) RETURN count(n) AS nodes").single()
                out["aura"]={"connected":True,"instance_id":"8ed83df4","nodes":r["nodes"]}
    except Exception as e:
        out["aura"]={"connected":False,"error_type":type(e).__name__}
    try:
        from openai import OpenAI
        c=OpenAI(api_key=env["OPENAI_API_KEY"],timeout=40,max_retries=0)
        model=env.get("OPENAI_CHAT_MODEL","gpt-6-luna")
        r=c.chat.completions.create(model=model,messages=[{"role":"user","content":"This is an API connectivity check for a synthetic research experiment. Reply only OK."}],max_completion_tokens=40)
        out["generation"]={"connected":True,"requested_model":model,"returned_model":r.model,"response_id":r.id,"text":r.choices[0].message.content,"usage":r.usage.model_dump()}
    except Exception as e:
        out["generation"]={"connected":False,"error_type":type(e).__name__,"status_code":getattr(e,"status_code",None)}
    (ROOT/"results/connectivity.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
