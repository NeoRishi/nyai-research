# NyAI: checkable evidence for AI oversight

AI-assisted research can fail when a persuasive conclusion hides a missing evaluation, an out-of-scope source or a permission boundary. NyAI investigates whether explicit evidence warrants, defeaters and external decision records can help reviewers detect those failures before accepting conclusions or delegating further actions.

This is a small reproducibility package for a research prototype. It is prepared for publication review; no public deployment or licence grant is implied by this candidate archive.

## Run it yourself

Extract the archive, open its folder, and use Python 3.11 or later:

```bash
python3 scripts/demo.py
python3 scripts/verify_bundle.py
python3 scripts/verify_agentic.py
python3 -m unittest discover -s tests -v
```

No installation, private corpus, database or API key is required. No live model request or external action occurs. The demo uses synthetic facts; its model comparison replays a recorded response.

The checker withholds a research-publication action when a claimed test has no execution record. It permits it after a simulated correction, and withholds when a required fact is unknown. The resulting explanation is derived from the checks that ran.

## What is being reproduced

The archive contains 24 fictional action-policy cases, their actual recorded model responses, the executable contract, a separately coded finite-set checker and tests. It includes raw model input/output so a reader can inspect what the model actually saw and returned. File hashes identify the reviewed snapshot.

| Method | Matches against the explicit contract |
|---|---|
| Any evidence | 12/24 |
| Permission-only gate | 13/24 |
| Recorded API model | 24/24 |
| Executable contract | 24/24 |

The competent model baseline already solves these simple cases. No improvement is demonstrated. The cases comprise twelve correlated counterfactual pairs; positive cases repeat one valid configuration. The separate checker was written by the same AI assistant, not an independent human reviewer. It is a cross-check on these well-formed synthetic records, not a general proof.

This package reproduces the 24-case action-contract experiment only. It does not include or independently reproduce the separate 120-case private-policy prompt pilot. No private workbook, proprietary policy extracts, knowledge-base text, source-corpus manifests, credentials, application materials or Git history are included.

## Why it is relevant to AI safety

The research direction concerns scalable oversight, safe delegation and assurance: make the link from evidence to conclusion inspectable, let failed or unknown conditions defeat an action, and identify what corrected evidence would warrant reconsideration. Feature attribution and these external warrants answer different questions. This prototype does not reveal model internals, establish arbitrary claim truth, measure deception resistance or demonstrate improved human oversight.

Runtime facts remain a trust boundary: this code checks supplied values, not independently attested test execution, file integrity or source authenticity. A fabricated but internally consistent record can fool it. A stronger study needs realistic unsupported claims, trusted runtime observations, independent source labels and reviewer outcomes.

To test your own counterexample, save a JSON runtime record and run `python3 scripts/check_record.py your_record.json`. Missing or malformed mandatory fields withhold execution. You can inspect the fixture states for the field schema. This command evaluates a record, not its free-text explanation. Keep the original snapshot intact for hash verification; use a copy for changes to code or fixtures.

## Cloud execution

After publication, fork the sanitized repository, enable GitHub Actions on the fork, and run **Reproduce NyAI contract pilot** in its Actions tab. The included workflow runs tests and replay in a hosted Python runner, without model or database secrets. A repository owner can also inspect its automatic CI runs. This is cloud execution of the research package, not a hosted web application. Account and usage policies apply.

[Manual workflow instructions](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow) and [fork workflow behaviour](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

## Governance context

The research relates to transparency, human oversight and explanation objectives in EU Regulation 2024/1689: [Article 13](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-13), [Article 14](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14) and [Article 86](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-86). This connection motivates evaluation; it establishes no statutory compliance. [Detailed mapping and limits](docs/eu-ai-act-relevance.md).

## Provenance and AI assistance

The source experiment was conducted on 25 October 2026. The recorded API model was requested and returned as gpt-6-luna, with provider-default temperature one and a 512-completion-token limit. Exact fresh generations are not guaranteed from a mutable model alias. Replay makes no new requests and does not alter the recorded outputs.

AI assisted implementation, fixture construction, checking, analysis and documentation. No AI annotation is presented as independent human verification. See `PROVENANCE.json` for source-file hashes and export boundaries. Redistribution terms must be selected before public publication; no third-party code is vendored in this archive.
