"""Audit a Markdown vault without uploading user content; no persistence of note text.
Use --vault /path/to/my-knowledge-base to produce hashes and wikilink/source counts.
"""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vault',required=True);p.add_argument('--output',default='results/vault_manifest.json');a=p.parse_args()
root=Path(a.vault).expanduser().resolve()
if not root.is_dir():raise SystemExit('Missing vault directory: '+str(root))
rows=[]
for f in sorted(root.rglob('*.md')):
 if '.obsidian' in f.parts:continue
 raw=f.read_bytes();s=raw.decode('utf-8',errors='replace')
 rows.append({'path':str(f.relative_to(root)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
   'wikilinks':len(re.findall(r'\[\[.*?\]\]',s)),'source_refs':len(re.findall(r'\[Source:',s,re.I)),
   'has_frontmatter':s.startswith('---'),'header_count':len(re.findall(r'^#{1,6}\s',s,re.M))})
result={'vault_path_not_exported':True,'files':len(rows),'wikilinks':sum(x['wikilinks'] for x in rows),
  'source_references':sum(x['source_refs'] for x in rows),'source_provenance_verified':False,
  'records':rows}
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print('files',len(rows),'wikilinks',result['wikilinks'],'sources',result['source_references'],'manifest',out)
