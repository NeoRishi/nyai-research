# EU AI Act relevance and limits

Reviewed against official sources on 25 October 2026. This is a research mapping, not a legal compliance assessment.

## What the earlier project actually cited

The NyAI v1 repository's `Nyaya_XAI_Research_Position_Paper.pdf` cites Regulation (EU) 2024/1689, the Artificial Intelligence Act, specifically Article 86. Section 2.2 discusses regulatory explanation; section 3.4 proposes a connection to five-part reasoning records; section 8.2 treats that connection as work requiring formal analysis. In the PDF these appear on file pages 3, 6 and 13. The source repository's current README does not itself name the Act.

[Original position paper at the inspected commit](https://github.com/NeoRishi/nyai-dashboard/blob/5534d4c4985bf74e0ef5e7da64fae8143b9e046b/Nyaya_XAI_Research_Position_Paper.pdf).

Some earlier passages make broad claims about the limits of all post-hoc XAI and regulatory sufficiency. Those passages are not adopted as established findings here. An attractive architectural analogy does not prove faithfulness, explainability by construction, or legal conformity.

## Scope of the connection

| Official provision | What it addresses | Candidate NyAI contribution | What remains unestablished |
|---|---|---|---|
| [Article 13](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-13) | Transparency and information enabling deployers to interpret and use high-risk-system outputs | Document assumptions, check outcomes and limitations | Complete provider instructions, appropriate output interpretation and system-specific conformity |
| [Article 14](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14) | Effective human oversight, awareness of automation bias, interpretation and intervention capabilities | Test whether external records help a reviewer challenge a conclusion and decide to withhold | Actual reviewer benefit, deployed override/stop controls, suitable human-machine interfaces and operational safeguards |
| [Article 86](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-86) | Explanations for affected people about certain consequential decisions involving Annex III high-risk systems | Explore records explaining system involvement and the principal decision grounds | An affected-person explanation process or evidence that these records meet the applicable legal duty |

Article 86 excludes the Annex III point 2 systems and includes legal or similarly significant effects perceived as adversely affecting health, safety or fundamental rights. Other restrictions and overlapping Union-law rights also matter. It is not a general requirement to disclose model weights, training data or internal chain-of-thought. Whether any duty applies depends on the actual system, use and legal context; this pilot makes no such determination. The Commission's service-desk pages identify their consolidated-text basis; this note does not attempt to resolve applicability dates or every amendment.

## Appropriate research claims

NyAI may provide a way to study inspectable grounds and contestability. Its explanation is generated from its own executed contract checks, but the input facts can still be wrong or forged. The current simulation does not operate a deployed high-risk AI system or make actual decisions about affected people. A record of a check is not evidence that a human understood it or could intervene effectively.

The strongest connection to AI safety is the hypothesis that reliable external evidence checks could improve oversight of delegated AI work. The regulatory connection supplies useful design questions and evaluation criteria. It does not replace threat modelling, independent evaluation or a theory of change for advanced-AI risks.

No claim is made that NyAI is EU AI Act compliant, certifies another system, fulfils Article 86, or guarantees meaningful human oversight.
