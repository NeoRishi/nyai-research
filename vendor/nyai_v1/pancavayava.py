"""
Pancavayava (five-limbed syllogism) - The reasoning trace output.

Order (standard, confirmed textbook-accurate):
1. Pratijna (proposition) - what we claim
2. Hetu (reason) - why we claim it
3. Udaharana (example) - analogous case supporting the reason
4. Upanaya (application) - applying the example to this case
5. Nigamana (conclusion) - therefore...
"""

from dataclasses import dataclass
from typing import List, Optional
from .belief import Belief, BeliefStatus
from .pramana import PRAMANA_ENGLISH


@dataclass
class SyllogismStep:
    """One step in the five-limbed syllogism."""
    step_number: int
    sanskrit_name: str
    english_name: str
    content: str
    pramana_used: Optional[str] = None
    is_fallacy_step: bool = False
    fallacy_type: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "sanskrit_name": self.sanskrit_name,
            "english_name": self.english_name,
            "content": self.content,
            "pramana_used": self.pramana_used,
            "is_fallacy_step": self.is_fallacy_step,
            "fallacy_type": self.fallacy_type,
        }


def generate_pancavayava(
    belief: Belief,
    verdict: str,
    fallacy_results: list = None,
    context: dict = None,
) -> List[SyllogismStep]:
    """
    Generate a five-step Nyaya syllogism trace for a belief evaluation.

    This is the core explainability output — every recommendation
    gets a human-readable reasoning chain.
    """
    context = context or {}
    claim = belief.claim
    evidence_list = belief.evidence
    steps = []

    # Step 1: Pratijna (proposition)
    steps.append(SyllogismStep(
        step_number=1,
        sanskrit_name="Pratijña",
        english_name="proposition",
        content=claim,
    ))

    # Step 2: Hetu (reason)
    reasons = []
    for ev in evidence_list:
        english = PRAMANA_ENGLISH.get(ev.pramana_type, ev.pramana_type.value)
        reasons.append(f"{ev.content} ({english})")
    hetu_content = "; ".join(reasons) if reasons else "No supporting reasons found."
    primary_pramana = evidence_list[0].pramana_type.value if evidence_list else None
    steps.append(SyllogismStep(
        step_number=2,
        sanskrit_name="Hetu",
        english_name="reason",
        content=hetu_content,
        pramana_used=primary_pramana,
    ))

    # Step 3: Udaharana (example/analogy)
    example = context.get("example", None)
    if not example:
        if evidence_list:
            tags = belief.all_tags
            if "vata" in tags or "kapha" in tags or "pitta" in tags:
                example = "In similar constitutional types, this approach has shown consistent results when conditions align."
            else:
                example = "In analogous cases with comparable evidence profiles, this reasoning pattern holds."
        else:
            example = "No analogous case available."
    steps.append(SyllogismStep(
        step_number=3,
        sanskrit_name="Udāharaṇa",
        english_name="example",
        content=example,
        pramana_used="upamana" if example else None,
    ))

    # Step 4: Upanaya (application) — or fallacy detection
    detected_fallacies = []
    if fallacy_results:
        detected_fallacies = [f for f in fallacy_results if f.detected]

    if detected_fallacies:
        fallacy = detected_fallacies[0]
        steps.append(SyllogismStep(
            step_number=4,
            sanskrit_name="Upanaya",
            english_name="application",
            content=f"HETVĀBHĀSA DETECTED — {fallacy.fallacy_type} ({fallacy.fallacy_english}): {fallacy.explanation}",
            is_fallacy_step=True,
            fallacy_type=fallacy.fallacy_type,
        ))
    else:
        application = context.get("application", None)
        if not application:
            application = f"Applying the evidence to this specific case: the reasoning holds with {len(evidence_list)} supporting source(s)."
        steps.append(SyllogismStep(
            step_number=4,
            sanskrit_name="Upanaya",
            english_name="application",
            content=application,
        ))

    # Step 5: Nigamana (conclusion)
    verdict_messages = {
        "accepted": f"The claim is ACCEPTED. {claim}",
        "rejected": f"The claim is REJECTED. The reasoning contains a fallacy that invalidates the recommendation.",
        "suspended": f"The claim is SUSPENDED. More information is needed before a conclusion can be drawn.",
        "uncertain": f"The claim is UNCERTAIN. Conflicting evidence of comparable strength prevents a definitive conclusion.",
        "revised": f"The belief has been REVISED based on stronger incoming evidence.",
    }
    conclusion = verdict_messages.get(verdict, f"Verdict: {verdict}")
    steps.append(SyllogismStep(
        step_number=5,
        sanskrit_name="Nigamana",
        english_name="conclusion",
        content=conclusion,
        is_fallacy_step=verdict in ("rejected", "suspended"),
    ))

    return steps
