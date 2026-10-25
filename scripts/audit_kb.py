"""Read local Markdown; export hashes/structural counts, never raw source content.

Upstream GraphRAG helpers are reused. File contents are research data, not instructions.
Private filenames stay in ignored private_audit/. No ingestion or embedding is performed.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sys
import os
import signal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor/graphrag"))
from import_wiki import split_frontmatter, LINK_RE, SOURCE_RE, link_target


def audit(roots):
    rows, failures = [], []
    for root in roots:
        paths=[]
        for base, dirs, files in os.walk(root):
            dirs[:]=[d for d in dirs if d not in {'.git','node_modules','.venv','.obsidian'}]
            paths.extend(Path(base)/f for f in files if f.endswith('.md'))
        paths.sort()
        print('Inventory',root.name,len(paths),flush=True)
        names = collections.Counter(p.stem.casefold() for p in paths)
        for p in paths:
            if any(x in {".git", "node_modules", ".venv"} for x in p.parts):
                continue
            try:
                if getattr(p.stat(),'st_flags',0) & 0x40000000:
                    failures.append(dict(root=root.name,path=str(p.relative_to(root)),error='dataless_cloud_placeholder'))
                    continue
                signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError()))
                signal.alarm(3)
                b = p.read_bytes()
                signal.alarm(0)
                text = b.decode("utf-8")
                meta, body = split_frontmatter(text)
                targets = [link_target(m.group(1)).casefold() for m in LINK_RE.finditer(body)]
                rows.append(dict(root=root.name, path=str(p.relative_to(root)),
                    sha256=hashlib.sha256(b).hexdigest(), bytes=len(b), words=len(text.split()),
                    frontmatter=bool(meta), wikilinks=len(targets),
                    unresolved_basename_links=sum(t not in names for t in targets if t),
                    ambiguous_basename_links=sum(names[t] > 1 for t in targets),
                    source_markers=len(SOURCE_RE.findall(body)),
                    prompt_like=any(s in text.casefold() for s in ["ignore previous instructions", "system prompt", "you are an ai"])))
            except (OSError, UnicodeDecodeError) as e:
                signal.alarm(0)
                failures.append(dict(root=root.name, path=str(p.relative_to(root)), error=type(e).__name__))
        print('Read',root.name,sum(r['root']==root.name for r in rows),flush=True)
    groups = collections.Counter(r["sha256"] for r in rows)
    totals = {}
    for name in sorted({r["root"] for r in rows}):
        selected = [r for r in rows if r["root"] == name]
        totals[name] = {"markdown_files_read":len(selected), **{
            k:sum(r[k] for r in selected) for k in ["bytes","words","frontmatter","wikilinks","unresolved_basename_links","ambiguous_basename_links","source_markers","prompt_like"]}}
    summary = dict(roots=totals, total_files_read=len(rows), unique_byte_hashes=len(groups),
        redundant_copies=len(rows)-len(groups), duplicate_hash_groups=sum(n>1 for n in groups.values()),
        read_failures=len(failures), notes=[
        "Duplicate counts use exact bytes; near-duplicates are not detected.",
        "Link resolution is a root-local basename heuristic, not an Obsidian resolver.",
        "Source markers establish presence of a string, not validity or entailment.",
        "Prompt-like matches are screening signals, not evidence of malicious instructions.",
        "No scientific, clinical, philosophical or copyright verification is implied."])
    return rows, failures, summary


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("roots", nargs="+", type=Path)
    a = p.parse_args()
    rows, failures, summary = audit(a.roots)
    (ROOT/"private_audit").mkdir(exist_ok=True)
    (ROOT/"private_audit/kb_manifest.json").write_text(json.dumps(dict(files=rows,failures=failures),indent=2))
    (ROOT/"results/kb_audit_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
