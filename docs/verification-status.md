# What has and has not been verified

The word **verified** must name the specific check. It must not collapse these distinct activities.

| Activity | Evidence | Status |
|---|---|---|
| Existing NyAI v1 code | Pinned upstream commit and five upstream API tests | Executed and passed locally |
| Original five scenarios | Saved execution records | Reproduced; constructed examples only |
| VCIM registry transcription | Exact values from 18 workbook rows | Automated match; no scientific validation |
| Latest VCIM workbook copy | Four relevant sheets, ignoring empty cells/rows | Same substantive cell values as scaffold source |
| Local corpus | Readable file bytes, hashes, structural markers | Audited; private per-file manifest remains local |
| Aura | Read-only schema/count queries | Connected, vector index online; no database writes |
| 120 initial cases | Design-derived expected labels | Unreviewed; never promoted to human ground truth |
| Paired model audit | Raw API outputs, prompts and protocol hashes | Actual model judgments, not human judgments |
| 24 action-policy cases | Separate finite-set oracle vs engine implementation | Automated independent recomputation by the same assistant |
| 24 generated action decisions | Actual returned JSON decisions vs finite-set oracle | Mechanically checked; human review not performed |
| Explanation truthfulness | Brief reasons inspected by the assistant | Not a blinded, independent human evaluation |
| Human oversight improvement | No participants or reviewer study | Not tested |
| Real-world source entailment | No independent expert source review | Not established |

No assistant-generated label is represented as a human review, founder review, or independent expert judgment. The two implementations of the contract check are separately coded, but share an author, design and interpretation. Agreement between them can miss shared mistakes.

The proposed *human-reviewed* metrics path remains empty until actual reviewers provide identities and rationales. `data/annotations/live_output_review.csv` contains 24 real responses, their complete synthetic policy and runtime facts, and blank annotation fields. `live_review_key.json` should be withheld from reviewers until their annotations are frozen. The starter's 120-case review queue remains separate.

For a source-review pilot, prioritise POL-01/02/03/06/11 and all seven epistemic layers. Review at least one benign control, one corruption and one vague response per selected policy. Reviewers should flag ambiguous labels rather than force agreement with templates. In particular, a conservative fallback may violate an urgent-action precedence rule, and a vague answer may be noncompliant under a mandatory explanation policy rather than merely insufficient.

No review has been booked or performed on the applicant's behalf. Recruiting reviewers is a real remaining dependency for an independently adjudicated efficacy claim; it does not block this preliminary work sample.
