# Observed execution and evidence revision

Date: 26 October 2026. Engineering diagnostic, not a human oversight study.

27 October audit update: harness identity, malformed-field and observation-failure defects were found and fixed. The original recorded results and manifest remain evidence of commit742ae57. The current hardened runner defaults to `/tmp/nyai-runtime-replay`; its hashes differ from the historical manifest. The new artifact-based study is reported separately in `docs/evidence-bound-work-sample.md`.

## Problem and safety connection

An AI research assistant may report that an evaluation passed even when it failed, or continue relying on a result after the tested artifact changes. Fluent explanations and structurally consistent records cannot establish that a test ran. Checkable AI-assisted research needs a connection between observed execution, the artifact it concerns and the authority for the next action.

The previous contract checks supplied fields. This diagnostic adds a host-owned observation path: actual subprocess exit status and output, SHA-256 hashes before/after execution, a task identifier, and an approval bound to the particular execution and artifact. Synthetic assistant claims cannot overwrite those observations through the provided interface. This is a separate, narrower executable contract, not a replacement for all twelve gates of the older engine.

## Prospective protocol

`experiments/runtime_revision_v1/protocol.json` was written before the first execution. It specifies twelve event trajectories, expected decisions and four comparison conditions. The runner records protocol, runner and engine hashes. The protocol is not externally preregistered or independently authored. The observer, scenarios, labels, engine and analysis were created with the same AI assistant.

Each trajectory begins with a passing test and applicable approval. A final decision follows one of: no change; artifact edit without retest; retest without renewed approval; valid edit/test/approval; failed test despite approval; approval revocation; restored approval; missing execution record; changed task; fabricated success claim despite failure; corrected failure; mutation after approval. There are 24 decision points but only twelve constructed trajectories, with identical initial conditions. Do not use 24 as an independent statistical sample size.

The policy requires passing observed execution for the current artifact/task and active approval bound to that exact execution. Reapproval after every execution is a deliberately chosen benchmark policy, not a universally necessary safety condition. A reviewer should challenge whether that policy is appropriate for the intended deployment.

The fictional program sums numbers. Three real assertions run in a separate Python process. An intentionally defective version returns zero. This verifies execution binding on trivial code, not correctness of realistic AI research. Permission is a recorded decision; no publication, deployment or other consequential action is performed.

## Comparisons and results

All conditions receive the same current observations and synthetic claim. No API calls, actual model responses, Neo4j writes or private data are involved in this diagnostic.

| Condition | Designated permits accepted / 16 | Designated withholds incorrectly permitted / 8 | Designated withholds respected / 8 |
|---|---|---|---|
| Trust the synthetic success claim | 16 | 8 | 0 |
| Cache the initial permission | 16 | 8 | 0 |
| Conventional execution/version/approval revalidation | 16 | 0 | 8 |
| NyAI observed-evidence contract | 16 | 0 | 8 |

The first two conditions are deliberately weak diagnostic controls, not representative evaluations of existing agents. The conventional workflow is the meaningful baseline. It enforces the same policy without NyAI explanation records and ties NyAI. **No incremental NyAI benefit is established.** No confidence intervals or significance claims are appropriate for these constructed correlated cases.

The NyAI record identifies the specific unmet checks. Whether this representation helps a human review or correct a decision better than ordinary logs remains an empirical question.

## Reproduction and review

From the repository root:

```bash
python3 scripts/run_runtime_revision.py --output /tmp/nyai-runtime-replay
python3 -m unittest discover -s tests -v
```

Only the standard library is needed. The runner executes only its built-in fictional code; it is not designed to accept untrusted programs. Outputs include raw test stdout/stderr, event histories, decisions, summary counts, a provenance manifest and a blank review worksheet. Temporary paths and Python traceback formatting can differ across machines; do not expect identical raw stderr bytes.

For human review, provide the reviewer only the policy plus `review_packet.json` and `review_queue.csv`. The packet omits design labels and arm decisions, but scenario names and test evidence can make intended labels apparent; this is not a fully blinded study. The reviewer should record a decision, rationale and ambiguity before consulting `protocol.json`, `records.jsonl` or this results table. Keep reviewer identity and actual completion date. Applicant review is useful but is not external independent review. No reviewer has completed this worksheet yet.

## Trust boundary and next experiment

The host process, fixed tests and approval event source are trusted. Approval is simulated, not authenticated human authorization. Hashes bind bytes; they do not establish test quality, scientific correctness or author identity. The observer is not resistant to a compromised operating system, malicious test harness or an adversary able to replace host-owned observations. The artifact could also change after the final permission check: production execution would require atomic binding to the checked artifact. Source retraction and dependency propagation across a general knowledge graph are not implemented here.

The next research experiment should use independently authored research tasks, realistic evaluation artifacts and real model proposals. Compare normal guarded workflows with the same evidence plus explicit warrant/revision records. Measure unwarranted acceptance, warranted completion, appropriate withholding and reviewer time/errors. Freeze task-family holdouts and annotation rules before generation. Test whether explanation records add value beyond conventional checks; allow a negative result.
