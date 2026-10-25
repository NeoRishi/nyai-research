# Source reconciliation — audit on 2026-10-25

| Component | Source | Found | Reuse | Main limitation |
|---|---|---|---|---|
| NyAI rule evaluator | `nyai-dashboard/backend/nyai/reasoning_agent.py` | `NyAIAgent.evaluate_claim`, `revise_belief`, `NaiveAgent` | Integration smoke tests and future condition | Naive comparator and general numerical evidence gate are weak baselines |
| Epistemic typing | `nyai-dashboard/backend/nyai/pramana.py` | Four types with numeric strengths (4/3/2/1) | Historical implementation as-is | Code calls hierarchy 'confirmed philosophically correct'; not supportable as a universal hierarchy |
| API | `nyai-dashboard/backend/main.py` | `/api/evaluate`, `/api/revise`, five scenarios | Can call to test original behavior | Does not establish external validity or frontier AI alignment |
| Graph retrieval | `vedic-graphrag/ask.py` | Vector candidates, graph boost, expanded sources, `--compare` | Read-only retrieval probe | Personalization boost is not rigorous source reliability validation |
| Markdown parser | `vedic-graphrag/import_wiki.py` | Frontmatter, wikilinks, `[Source:]`, Note/Source relationships | Reuse script under explicit flags | Import writes Neo4j; only reads a single wiki directory, should not run blindly |
| Graph chunks | `vedic-graphrag/build_chunks.py` | Source chunks and vector index | Later retrieval benchmark | README warns chunks absent from current wiki may be removed |
| VCIM NyAI governance | `VCIM v3 78_NyAI` | Observe/Warrant/Gate/Trace/Correct; no silent stale facts | Evaluation rubric design | Workbook calls v3 operations proposals, not validated product behavior |
| VCIM evidence scopes | `VCIM v3 68_Epistemics` | Empirical vs methods vs traditional vs hypothesis vs personal vs frontier | Grounding and categorical warrants | Biomedical predictive weights explicitly not granted to traditional content |
| VCIM policy | `VCIM v3 74_Policy` | 11 gate orders and required outcomes | Template case provenance | Compliance with an unvalidated specification is not safety proof |

## Important discrepancy
NyAI v1's `PRAMANA_STRENGTH` imposes a fixed ordinal ranking; VCIM v3's `NY-WARRANT` states that a universal pramāṇa ladder must **not** be imposed. We will preserve v1 history and test claim-specific warrant design as a separately versioned experimental condition.

## Schema reconciliation recommendation
- `Source`: URI/document SHA, title, publication info, retrieval timestamp, validation status.
- `Claim`: natural-language assertion, domain, intended population/context, inferences.
- `Evidence`: source anchoring, passage span, contradiction flag, warrant type, reliability limits.
- `Decision`: actual rule IDs executed, exclusions, output, model/prompt version, time.
- `Correction`: supersedes prior decision, immutable event lineage, reason and recalculation status.

No false claim that every graph edge is evidence or that an explanation reveals hidden model cognition.
