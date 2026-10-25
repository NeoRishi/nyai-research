# Sharing and independent validation

## Recommended release boundary

Keep the full research repository and private knowledge base separate from a small reproducibility package. The user selected a package anyone can eventually access, with review before publication. No change to repository visibility or public publication is authorised by this preparation step.

The package contains generic action-contract code, the 24 fictional action-policy cases, the actual recorded responses to those cases, a separately coded checker, tests, a demo and file hashes. A fresh copy can run without the original repository, a private corpus, Neo4j or model credentials. It includes no private workbook, 120-case proprietary-policy extracts, handoff documents, local audit manifests or Git history.

The distinction is important: the existing repository contains VCIM-derived text even though it excludes the workbook itself. Likewise, the earlier complete research ZIP is a private research archive, not the proposed public release. Do not publish either wholesale.

This boundary shares the generic method and fictional evidence while preserving proprietary domain knowledge. It cannot simultaneously make a method fully inspectable and keep that same method secret. A private backend API can conceal a corpus, but its outputs can still reveal information and a hosted interface alone cannot establish reproducibility. The proposed package avoids connecting to that backend at all.

## What someone can independently check

- Inspect and change the executable action conditions.
- Run the synthetic example and its correction/unknown-fact variants.
- Recompute the 24 recorded execution decisions against the explicit contract.
- Check file hashes, actual returned action names, invalid-output handling and the weak-baseline comparisons included in the package.
- Write their own checker, adversarial cases or alternative contracts.

This reproduces software behaviour and the finite 24-case result. It does not independently establish label validity, a benefit to human reviewers, the 120-case private-policy comparison, retrieval quality on the private knowledge base, or real-world safety. It does not generate fresh model samples. The package must not imply that keeping a corpus private makes corpus-dependent claims externally reproducible.

## Cloud and reviewer options

| Option | Private-KB exposure | Research value | Recommendation |
|---|---|---|---|
| Downloadable sanitized package | None required | Reviewer inspects code and replays results locally | Prepare now |
| GitHub Actions on a sanitized repository | None required | Repeat the same checks in a fresh hosted runner | Preferred cloud route after publication approval |
| GitHub Codespaces for that repository | None required | Reviewer runs and edits the package in a browser-based cloud environment | Optional convenience |
| Hosted interactive demo using synthetic facts | None required | Makes examples easier to explore, but adds no independent ground truth | Optional after the evaluation package |
| Public service connected to the private KB | Potential output leakage, even if storage remains private | A different deployment and privacy problem | Not needed for this research work sample |

The staged package contains a manually runnable GitHub Actions workflow. After public publication, a reviewer can fork it, enable Actions, and run the workflow on their own copy. Write access is needed to dispatch a workflow, so arbitrary visitors cannot run it on the original repository. The workflow runs tests and deterministic replay, not a model API. GitHub account, usage and organisational policies still apply. A workflow file in an unpublished archive is cloud-ready configuration, not an already deployed service.

[GitHub manual workflow instructions](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow), [fork workflow behaviour](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), [Codespaces](https://docs.github.com/en/codespaces/developing-in-a-codespace).

For a reviewer who cannot access a private repository, provide the sanitized archive or a separately published sanitized repository. A private GitHub URL alone is not access. Choose publication rights and a licence explicitly before encouraging redistribution; this staged package does not assign a new licence to existing work.

## Research priority before more hosting

The official [MATS Residency application requirements](https://www.matsprogram.org/residency/apply) accept a repository, report or evaluation as a representative work sample; they do not list a hosted demo as a requirement. The stated research priorities include checkable AI-assisted research, assurance and agent safety. Our recommendation is therefore to prioritise independently reviewable evidence and clear limitations over cloud product development. This is a fit assessment, not a prediction of selection.

The highest-value next work is a small set of realistic, source-backed cases and independent annotation, followed by a trusted observer for runtime facts and a controlled reviewer study. The current 24-case ceiling and unreviewed template labels are more important limitations than where the demo runs.
