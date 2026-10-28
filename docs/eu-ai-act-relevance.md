# EU AI Act & Technical AI Governance Relevance Note

This note maps the host-anchored multi-hop `AssuranceDAG` prototype to research questions motivated by Regulation (EU) 2024/1689 and the EU General-Purpose AI (GPAI) Code of Practice. It does not establish applicability, legal sufficiency, certification, or improved human oversight.

## Scope and official sources

The Act distinguishes high-risk AI systems from general-purpose AI models and from GPAI models with systemic risk. These obligations do not automatically apply to every research or coding agent. Applicability and transition dates depend on the system, provider and use; see the Commission's current [Article 113 text](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-113), rather than assuming all high-risk obligations began on one date.

The [GPAI Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai) is a voluntary compliance tool. Its Transparency and Copyright chapters address Article 53; Safety and Security addresses Article 55. **Appendix 3.5 concerns independent external model evaluations**, not a statutory requirement to implement an assurance DAG. The Commission identifies this role in [COM(2026) 577, footnote 18](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A52026DC0577). **Measure 3.5** is a separate provision concerning post-market monitoring, discussed in the [AI Office's fourth Signatory Taskforce meeting report](https://digital-strategy.ec.europa.eu/en/news/fourth-gpai-signatory-taskforce-meeting). Sharing fewer code dependencies does not establish evaluator independence.

## Technical mapping and limits

| Official provision | Research connection in `AssuranceDAG` | What remains outside scope |
|---|---|---|
| [Article 12: record-keeping](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-12) | `observe_step_execution()` captures subprocess outcomes, stdout/stderr, direct local AST imports and selected before/after file digests in memory. Decision records expose resulting checks and causal metadata. | Full observation persistence, lifetime logging, retention, access controls and tamper-evident storage. The saved `records.jsonl` does not contain the full execution observations. |
| [Article 13: deployer transparency](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-13) | Records list ancestor claims, bound artifact names, unmet gates and repair suggestions. Structural and hybrid evaluations are saved separately. | Complete instructions for use and evidence that deployers correctly interpret the outputs. |
| [Article 14: human oversight](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14) | Backward traversal selects active support claims and associated recorded steps. The fixture mean reductions are 79.49% of log steps and 85.53% of whitespace-separated log words. | Human accuracy, fatigue, review time, automation bias, deployed override/stop controls and effective intervention. Compression is a log-size measure, not a demonstrated reduction in human burden. |
| [Article 15: accuracy, robustness and cybersecurity](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-15) | Current hashes, execution outcomes and selected shared warrants identify ten constructed structural/dependency invalidations. Optional Stage-2 AST inspection catches two selected assertion hacks. | General semantic correctness, adversarial coverage, implicit dependency tracing, secure execution and production robustness. |
| [Article 53](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-53), [Article 55](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-55), and GPAI Code of Practice | Structured records may support documentation and evaluation review. Transitive invalidation illustrates how changed upstream evidence can defeat a downstream claim. Appendix 3.5 motivates external review as a separate governance question. | Provider obligations, systemic-risk evaluation and mitigation, incident reporting, independent external evaluation and a complete safety case. |
| [Article 72: post-market monitoring](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-72) | The runner evaluates initial and final states after controlled revisions, illustrating evidence-drift detection. | A deployed monitoring system, continuous collection of operational performance data, a monitoring plan or tracking actual repository commits. |
| [Article 86: explanations of certain individual decisions](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-86) | `principal_grounds_ancestors`, `unmet_gates`, `shared_warrants_detected` and `minimal_repair_set` support research into inspectable decision grounds and reconsideration. | An affected-person explanation process or proof of legal sufficiency. Article 86 has a specific scope involving consequential deployer decisions based on certain Annex III high-risk systems, excludes point 2 systems, and is subject to legal restrictions and overlapping Union-law rights. It does not prescribe this record schema or a counterfactual repair field. |

## Recorded Study 4 example

The final record for `T08_shared_grader_warrant_collapse` shows `run_eval_a.py` and `run_eval_b.py` importing `shared_grader.py`. Both subprocess checks pass and their hashes are current. The configured 1-hop and flat-manifest baselines permit; both AssuranceDAG variants suspend because the branches share a selected warrant.

The actual `statutory_contestability_record` contains:

```json
{
  "effective_independent_branches": 1,
  "required_independent_branches": 2,
  "shared_warrants_detected": ["module:shared_grader.py"],
  "unmet_gates": ["warrant_independence_vertex_cut"],
  "minimal_repair_set": ["decouple_shared_warrant:shared_grader.py"],
  "oversight_compression": "4/23 steps in causal slice (82.6% pruned)"
}
```

This example detects shared reliance without requiring the shared grader itself to be corrupted. `minimal_repair_set` is a legacy name for collected repair suggestions; the implementation does not prove a mathematically minimal or sufficient counterfactual repair. It emits no `counterfactual_fix` field. The `eu_ai_act_research_mapping` strings are research annotations, not legal findings.

See [Study 4 methods and limitations](assurance-dag-study.md). All 16 trajectories are constructed subprocess diagnostics with simulated approval and configured claim dependencies. There are no affected-person decisions, participant trials or independent human annotations.
