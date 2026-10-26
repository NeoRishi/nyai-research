"""Build a source-backed Markdown addendum and clearly marked post-hoc diagnostics."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/graphrag_144_v1'
RESULTS=ROOT/'results/graphrag_144_v1'
NAMES={'full_reference':'Full reference','vector_rag':'Vector RAG','graph_rag':'GraphRAG','graph_rag_structured':'GraphRAG structured'}


if __name__=='__main__':
    summary=json.loads((RESULTS/'summary.json').read_text())
    cases=json.loads((OUT/'cases.json').read_text())
    contexts={(r['case_id'],r['arm']):r for r in json.loads((OUT/'retrieved_contexts.json').read_text())}
    rows=[json.loads(s) for s in (RESULTS/'model_responses.jsonl').read_text().splitlines()]
    by={(r['case_id'],r['arm']):r for r in rows}
    diagnostics={}
    for arm in NAMES:
        selected=[c for c in cases if c['domain']=='action_contract']
        diagnostics[arm]=dict(
            permission_with_incomplete_reference_coverage=sum(by[(c['case_id'],arm)].get('parsed',{}).get('execute') is True and contexts[(c['case_id'],arm)]['target_fact_recall']<1 for c in selected),
            positive_case_withholding_with_incomplete_reference_coverage=sum(c['design_label'] is True and by[(c['case_id'],arm)].get('parsed',{}).get('execute') is False and contexts[(c['case_id'],arm)]['target_fact_recall']<1 for c in selected),
            negative_cases_with_designated_defeater_fact_available=sum(c['design_label'] is False and c['decisive_fact_id'] in {f['fact_id'] for f in contexts[(c['case_id'],arm)]['facts']} for c in selected))
    diagnostic_report=dict(status='POST HOC DESCRIPTIVE DIAGNOSTIC; not the frozen primary endpoint',scores=diagnostics,
        interpretation='Full-policy oracle agreement does not measure whether a decision is justified by partial retrieved evidence. Withholding can be appropriate under source uncertainty.')
    (RESULTS/'available_evidence_diagnostics.json').write_text(json.dumps(diagnostic_report,indent=2)+'\n')
    valid_pairs=[c for c in cases if c['domain']=='policy_audit' and all('parsed' in by[(c['case_id'],a)] for a in ['vector_rag','graph_rag'])]
    pair_counts={a:sum(by[(c['case_id'],a)]['parsed']['label']==c['design_label'] for c in valid_pairs) for a in ['vector_rag','graph_rag']}
    (RESULTS/'complete_pair_diagnostic.json').write_text(json.dumps(dict(status='Secondary complete-response diagnostic; primary results retain all failures',n=len(valid_pairs),matches=pair_counts),indent=2)+'\n')
    primary=['| Condition | Policy template matches | Contract oracle matches | Invalid outputs |','|---|---|---|---|']
    coverage=['| Condition | Policy reference-fact recall | Contract reference-fact recall |','|---|---|---|']
    costs=['| Condition | Total recorded tokens | Policy median latency | Contract median latency |','|---|---|---|---|']
    for arm,name in NAMES.items():
        p=summary['scores']['policy_audit'][arm];a=summary['scores']['action_contract'][arm]
        primary.append(f"| {name} | {p['matches']}/120 ({p['agreement']:.1%}) | {a['matches']}/24 ({a['agreement']:.1%}) | {p['invalid_outputs']+a['invalid_outputs']} |")
        coverage.append(f"| {name} | {p['reference_fact_recall_mean_per_case']:.1%} | {a['reference_fact_recall_mean_per_case']:.1%} |")
        costs.append(f"| {name} | {p['tokens']['total_tokens']+a['tokens']['total_tokens']:,} | {p['median_request_seconds']:.2f} s | {a['median_request_seconds']:.2f} s |")
    report=f'''# NyAI GraphRAG evaluation addendum

26 October 2026 | AI-assisted draft for author review

## Question and observed answer

Does graph-expanded retrieval help with the existing 120 policy candidates and 24 action-contract cases? This controlled pilot uses actual Neo4j retrieval and actual model calls on those synthetic tasks. The tasks and their verification limits remain synthetic; this is not a new independently labelled benchmark or a human-oversight study.

Graph expansion recovered more of the designated reference facts. It increased agreement with the unreviewed policy labels from 63 to 71 of 120 and full-contract agreement from 18 to 24 of 24. The stronger direct-reference baseline still matched 96 policy labels and all 24 contract decisions. Adding structured audit instructions to identical GraphRAG evidence reduced policy agreement to 61 and left contract agreement at 24. These mixed observations do not establish a general NyAI advantage.

## Actual requests and outcomes

{chr(10).join(primary)}

There are 576 request records, with {summary['actual_api_responses']} returned API responses. Three connection failures and two token-limit truncations are retained as nonmatches. Vector RAG has two connection failures and one truncation; the structured arm has one of each. No failed output was replaced to improve a score. In the 117 policy cases with complete responses for both retrieval arms, vector RAG matches {pair_counts['vector_rag']} and GraphRAG {pair_counts['graph_rag']}; this is a secondary diagnostic, not a replacement denominator.

All 120 policy labels remain unreviewed. The 24 contract labels are checked with a separately coded oracle by the same AI assistant. They are not independent human judgments. All 49 template violations were flagged by direct-reference, GraphRAG and structured GraphRAG; vector RAG flagged 48, with one violation request failing in transport. Policy false-positive rates against template nonviolations were 26.8%, 71.8%, 53.5% and 64.8%, respectively. Label ambiguity prevents treating those rates as real-world false alarms.

The contract-oracle score measures decisions against the complete policy. A withheld decision may be appropriate when some required rules were not retrieved. Consequently, its score must not be interpreted as a direct measure of justified acceptance.

The parsed outputs contain 1,723 cited fact-ID mentions, all resolving to supplied context IDs. Two vector-RAG action responses cite no facts. Citation resolution checks identity, not whether the cited text actually supports the conclusion.

<!-- pagebreak -->

## What the graph contains and how retrieval differs

The original wellness graph has no exact benchmark-reference ID matches. The approved experiment therefore adds an isolated reference-policy graph: 19 source notes, 48 policy facts and 19 reference nodes, totalling 86 new nodes. It contains neither candidate answers nor labels. Existing knowledge-base labels and relationships are unchanged; original Note count remains 100. A separate read-only replay reproduced all 31 unique query results and checked every original label and relationship count.

All 144 cases run under four conditions: full reference facts; six vector-retrieved facts; graph-selected facts plus linked sibling requirements; and the same graph evidence with a structured warrant/scope/defeater prompt. The upstream plain_rag and graph_rag selection code is unchanged. A benchmark-specific adapter uses namespaced labels, domain filtering and parent-to-fact traversal. The graph is designed around these known reference policies, with no held-out source families.

{chr(10).join(coverage)}

These are per-case averages of exact reference-fact recovery, not semantic relevance judgments. On unique policy queries, vector recall is 94.4%; the case-weighted figure is 91.7%. All arms reach the designated source for every case. Graph expansion repairs missing facts within those sources. It also adds facts from other retrieved policies: the policy cases average 9.3 facts with GraphRAG versus six with vector RAG and two with the direct-reference baseline. Equal context caps do not mean equal realised context or equal distractor exposure.

The same source inventory is available to both retrieval arms. Queries use scenarios or runtime facts, not candidate answers or labels. The structured arm reuses identical frozen GraphRAG evidence. The model was requested and returned as gpt-6-luna, with its default temperature of one, a 1,024-completion-token limit and an 8,000-character context cap. Prompt, source, payload and context hashes are retained. The protocol was locally frozen before execution, with a pre-execution safeguard amendment; it is not an external preregistration.

## What the contract disagreements mean

Vector RAG provided six of twelve requirements. It withheld six otherwise permitted actions because the remaining requirements were unavailable; the recorded reasons explicitly cite incomplete policy evidence. Those conservative decisions are not unsafe executions. Conversely, it permitted six other positive cases despite equally incomplete reference coverage. Graph expansion supplied all twelve requirements and matched the full-policy oracle on all 24 decisions. No arm permitted any of the twelve defeated actions.

A post-hoc diagnostic records six vector permissions with incomplete reference coverage and zero for the other arms. Only six of twelve designated defeating facts were available to the vector arm; it could still withhold because policy knowledge was incomplete. This illustrates why task-outcome agreement, defect detection and warranted permission are different measurements.

<!-- pagebreak -->

## Policy failures and interpretation

More source coverage did not approach the direct-reference baseline's policy agreement. For POL-02-03, the direct-reference arm treated a conservative pause as compatible with its consent rule. GraphRAG also retrieved a general explanation boundary and called that pause a novel, prohibited action. For POL-01-09, direct-reference auditing called the vague response insufficient, while GraphRAG invoked additional explanation requirements and called it a violation. These examples suggest scope-selection and rubric problems; they are not adjudicated proof that either auditor is correct.

Against vector RAG, GraphRAG alone matched 15 policy cases, vector alone seven, both 56 and neither 42. With identical graph evidence, the structured prompt alone matched six, ordinary GraphRAG alone 16, both 55 and neither 43. The gain from graph expansion and the lack of a structured-prompt gain must therefore be reported separately. No significance test or IID interval is asserted for correlated templates and unreviewed labels.

## Resource use and privacy

{chr(10).join(costs)}

Token usage is what the API reported; failed transport can leave usage unobserved. Monetary cost is not inferred from an unverified price schedule. Request latency includes network and provider behaviour, and the four-worker batch is not a controlled latency benchmark.

Only the approved fixture-reference excerpts, fictional runtime facts and generic queries were sent to model APIs. No private wellness passages were retrieved for this experiment or sent to a model. The full 144-case contexts include proprietary-policy derivatives and remain in the private research repository. The previously prepared public review package remains scoped to the earlier generic 24-case replay; it does not silently acquire these materials or results.

## Reproduce and next step

Run scripts/summarize_graphrag144.py, scripts/report_graphrag144.py and scripts/verify_graphrag144.py to replay the stored results without credentials or charges. Raw requests/responses, retrieved contexts, source snapshots, graph import counts and independent retrieval replay are retained under experiments/graphrag_144_v1 and results/graphrag_144_v1. Live import/retrieval commands and limitations are in docs/graphrag-evaluation-design.md. Original pilot outputs are unchanged.

The next study should use independently authored cases and source-family holdouts, reviewer-adjudicated labels, controls for irrelevant context and explicit warranted-acceptance metrics. A trusted runtime observer is needed before self-reported facts become operational safeguards. Human reviewer outcomes remain unmeasured. Successful reproduction of these finite source-policy tasks does not establish general answer correctness, legal compliance, deception resistance or reduced catastrophic risk.

The applicant supplied the project framing and source materials. AI assistance covered code, fixtures, API orchestration, analysis and this addendum. Neither independent human verification nor applicant approval is implied.
'''
    (ROOT/'docs/graphrag-evaluation-results.md').write_text(report)
    print('Wrote GraphRAG results addendum and post-hoc diagnostics')
