# Execution handoff for ChatGPT Work / Codex / local desktop

Goal: Complete a truthful, research-grade NyAI **Bridge** work sample and application by 27 Oct 2026, ahead of MATS 31 Oct 2026 AoE cutoff. Do not spend time on UI redesign or unnecessary Supabase integration.

## Inputs
- This repo archive: `NyAI_Research_MATS_Starter_2026-10-25.zip`
- Existing public repos: `NeoRishi/nyai-dashboard` and `NeoRishi/vedic-graphrag`
- Existing local folder: `~/Desktop/my-knowledge-base` (may require desktop app/local permissions; cloud browser alone cannot assume filesystem access)
- Existing VCIM v3 workbook: user's private source (not stored in new repo)
- Neo4j Aura project URL: `https://console.neo4j.io/projects/35d1f0d9-1c3b-4043-b352-d3aef35c7245/instances`; instance short ID `8ed83df4` (not a Bolt URI)
- Credentials: must remain only in local protected `.env` or environment variables; never print in chat or commit.

## Work sequence — no redundant rebuilding

1. **GitHub:** Create a private repository named `NeoRishi/nyai-research`; initialize it from this scaffold (do not overwrite original repos). Commit with reproducibility metadata, retain source links and AI-use disclosure.
2. **Local evidence audit:** Clone existing repos; run their tests and original NyAI five scenarios. Record commit SHAs and actual outcomes. Audit graph code for destructive writes; never re-run import against populated Aura without explicit backup/check.
3. **Vault inspection:** Inventory `~/Desktop/my-knowledge-base` using `scripts/ingest_manifest.py`, inspect note count, coverage, sources and provenance. Avoid uploading full private notes without permission.
4. **Neo4j:** Configure actual `neo4j+s://...` URI locally; run `scripts/check_neo4j.py` read-only. Confirm counts/labels/vector index. Only after confirming backup/compatibility, plan any ingestion changes.
5. **Benchmark:** Use the 120 fixtures for harness smoke tests; select 20–40 diverse, high-quality cases for independent source review. Add 10+ agentic oversight cases in another domain. Do not call template labels human verified.
6. **Model outputs:** Run `scripts/generate_model_responses.py` with an available API model, recording version/settings/cost. Independently annotate **these outputs**, not reusing original template labels. If unable to recruit independent reviewer, explicitly label as founder-reviewed pilot.
7. **Comparison:** Run baseline and structured protocols on frozen same inputs. Compare errors, false positives and limitations; publish confidence intervals when supportable. Avoid inferring human oversight outcomes from LLM judge metrics.
8. **Report:** Update `docs/work-sample.md` with actual empirical findings, failures and links, keeping original history. Produce a concise standalone PDF only if useful and feasible.
9. **MATS:** Submit Bridge application with two referees, 2-page CV, one representative work sample, track note, research plan, written responses and AI disclosure. Target 27 Oct rather than waiting for deadline.

## GitHub command sequence (locally after extracting this repo)

```bash
cd nyai-research
git init -b main
git add .
git commit -m "Initial NyAI oversight research scaffold and synthetic fixtures"
# With GitHub CLI authenticated (or use Work UI to create the private repo):
gh repo create NeoRishi/nyai-research --private --source=. --remote=origin --push
```

## Decision gates
- No newly fabricated performance claim.
- No secrets, original full VCIM workbook or private vault uploaded into public git history.
- No need to add Supabase for the initial study.
- No need to reimplement NyAI v1.
- High priority: a real, independently assessed small evaluation and honest Bridge application.
