# Reused source code

NyAI v1 files in `nyai_v1/` were copied without modification from
https://github.com/NeoRishi/nyai-dashboard at commit
`5534d4c4985bf74e0ef5e7da64fae8143b9e046b`, path `backend/nyai/`.
The original comments include claims about philosophical correctness and fixed
hierarchies that this research does not endorse. They remain intact for comparison.

`graphrag/import_wiki.py`, `graphrag/ask.py` and `graphrag/kb_common.py` are copied without modification from
https://github.com/NeoRishi/vedic-graphrag at commit
`a6e0bc7e7b4b90e39b34dd6b192869bd92f9e9ab`.
The audit scripts call parsing and environment-reading helpers. The live
`integrations/graph_nyai.py` adapter calls the original plain/graph vector retrieval,
graph expansion and context-building functions, then passes the resulting passages
through the original NyAI v1 engine and a scoped provenance audit. Its optional
embedding request sends only the query. The answer-generation and graph-writing
functions are not invoked. Private passages stay local.

Both repositories are attributed to the applicant, who explicitly requested reuse.
No LICENSE file was found in either checkout. This private reuse does not assert
any general third-party redistribution licence. Keep attribution and clarify rights
before a public release. Original repositories were not changed.

The starter scaffold was provided by the user in
`NyAI_Research_Starter_Fresh.zip` on 25 October 2026. Its original handoff,
120 fixtures, evaluation protocol and review guardrails are retained.
