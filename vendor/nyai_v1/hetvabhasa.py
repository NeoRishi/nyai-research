"""
Hetvabhasa (fallacious reasons) - The agent's internal fallacy detector.

Five fallacy types implemented:
1. Savyabhichara (overgeneralization) - rule has counter-cases
2. Viruddha (contradiction) - evidence contradicts itself
3. Asiddha (unestablished) - no pramana backing
4. Prakaranasama (circular) - word-overlap heuristic
5. Kalatita (stale) - evidence too old (extension of Badhita)

Kalatita is our declared extension. Classical lists have Badhita.
We adapted the freshness concept for practical AI use.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta
from .pramana import Evidence, PramanaType
from .belief import Belief


@dataclass
class FallacyResult:
    """Result of a fallacy check."""
    fallacy_type: str
    fallacy_english: str
    detected: bool
    explanation: str
    is_extension: bool = False  # True for Kalatita (our extension)

    def to_dict(self) -> dict:
        return {
            "fallacy_type": self.fallacy_type,
            "fallacy_english": self.fallacy_english,
            "detected": self.detected,
            "explanation": self.explanation,
            "is_extension": self.is_extension,
        }


class FallacyDetector:
    """Checks for hetvabhasa (fallacious reasoning) in beliefs."""

    def __init__(self):
        # Ayurvedic contradiction rules (tag-based)
        self.contradiction_rules = {
            ("pitta", "heating"): "Heating substances aggravate Pitta dosha",
            ("kapha", "heavy"): "Heavy substances aggravate Kapha dosha",
            ("vata", "cold"): "Cold substances aggravate Vata dosha (in excess)",
            ("pitta", "ginger"): "Ginger is heating and can aggravate Pitta",
            ("acid_reflux", "ginger"): "Ginger can worsen acid reflux symptoms",
            ("acid_reflux", "heating"): "Heating substances can worsen acid reflux",
        }

        # Counter-case rules for overgeneralization
        self.counter_case_rules = {
            "ginger": {
                "counter_tags": ["pitta", "acid_reflux"],
                "explanation": "Ginger helps digestion generally, but aggravates Pitta and worsens acid reflux",
            },
            "cold_food": {
                "counter_tags": ["vata"],
                "explanation": "Cold foods may cool Pitta but aggravate Vata",
            },
            "heavy_food": {
                "counter_tags": ["kapha"],
                "explanation": "Heavy foods ground Vata but aggravate Kapha",
            },
        }

        self.staleness_threshold = timedelta(days=7)

    def check_all(self, belief: Belief, evidence_timestamp: Optional[datetime] = None) -> List[FallacyResult]:
        """Run all five fallacy checks on a belief."""
        results = []
        results.append(self.check_savyabhichara(belief))
        results.append(self.check_viruddha(belief))
        results.append(self.check_asiddha(belief))
        results.append(self.check_satpratipaksha(belief))
        results.append(self.check_kalatita(belief, evidence_timestamp))
        return results

    def check_savyabhichara(self, belief: Belief) -> FallacyResult:
        """
        Savyabhichara (overgeneralization):
        The reason applies in some cases but not all.
        Check if any evidence tags trigger counter-case rules.
        """
        tags = belief.all_tags
        for item_tag, rule in self.counter_case_rules.items():
            if item_tag in tags:
                counter_tags = set(rule["counter_tags"])
                overlap = tags & counter_tags
                if overlap:
                    overlap_str = ", ".join(sorted(overlap))
                    return FallacyResult(
                        fallacy_type="savyabhichara",
                        fallacy_english="overgeneralization",
                        detected=True,
                        explanation=(
                            f"Counter-case detected: '{item_tag}' has known exceptions "
                            f"when these conditions are present: {overlap_str}. "
                            f"{rule['explanation']}."
                        ),
                    )
        return FallacyResult(
            fallacy_type="savyabhichara",
            fallacy_english="overgeneralization",
            detected=False,
            explanation="No counter-cases found for the given evidence tags.",
        )

    def check_viruddha(self, belief: Belief) -> FallacyResult:
        """
        Viruddha (contradiction):
        Evidence contains contradictory tags (e.g., pitta + heating).
        """
        tags = belief.all_tags
        for (tag_a, tag_b), reason in self.contradiction_rules.items():
            if tag_a in tags and tag_b in tags:
                return FallacyResult(
                    fallacy_type="viruddha",
                    fallacy_english="contradiction",
                    detected=True,
                    explanation=f"Contradictory tags '{tag_a}' and '{tag_b}': {reason}.",
                )
        return FallacyResult(
            fallacy_type="viruddha",
            fallacy_english="contradiction",
            detected=False,
            explanation="No contradictions found in evidence tags.",
        )

    def check_asiddha(self, belief: Belief) -> FallacyResult:
        """
        Asiddha (unestablished):
        The claim has no pramana backing at all.
        """
        if not belief.evidence:
            return FallacyResult(
                fallacy_type="asiddha",
                fallacy_english="unestablished",
                detected=True,
                explanation="No evidence (pramana) supports this belief.",
            )
        return FallacyResult(
            fallacy_type="asiddha",
            fallacy_english="unestablished",
            detected=False,
            explanation=f"Belief is supported by {len(belief.evidence)} piece(s) of evidence.",
        )

    def check_satpratipaksha(self, belief: Belief) -> FallacyResult:
        """
        Satpratipaksha (equal-force counterargument):
        When evidence items within the same belief directly conflict,
        and neither is strong enough to override the other.
        Detected via contradictory tag pairs across evidence items.
        """
        contradiction_tag_pairs = [
            ("harmful", "harmless"),
            ("safe", "unsafe"),
            ("heating", "cooling"),
            ("beneficial", "detrimental"),
        ]

        all_tags = belief.all_tags
        for tag_a, tag_b in contradiction_tag_pairs:
            if tag_a in all_tags and tag_b in all_tags:
                return FallacyResult(
                    fallacy_type="satpratipaksha",
                    fallacy_english="equal-force counterargument",
                    detected=True,
                    explanation=(
                        f"Evidence contains contradictory positions: "
                        f"'{tag_a}' and '{tag_b}' are present. "
                        f"Neither side has sufficient strength to override the other."
                    ),
                )
        return FallacyResult(
            fallacy_type="satpratipaksha",
            fallacy_english="equal-force counterargument",
            detected=False,
            explanation="No equal-force counterarguments detected.",
        )

    def check_kalatita(self, belief: Belief, evidence_timestamp: Optional[datetime] = None) -> FallacyResult:
        """
        Kalatita (stale evidence) - Our extension of Badhita.
        Pratyaksha evidence older than 7 days is flagged as stale.
        Stale -> SUSPENDED (need fresh data), not REJECTED (logic is wrong).

        This is an acknowledged extension of classical Nyaya.
        """
        check_time = datetime.now()

        for ev in belief.evidence:
            if ev.pramana_type == PramanaType.PRATYAKSHA:
                ts = evidence_timestamp or ev.timestamp
                if ts and (check_time - ts) > self.staleness_threshold:
                    age_days = (check_time - ts).days
                    return FallacyResult(
                        fallacy_type="kalatita",
                        fallacy_english="stale evidence",
                        detected=True,
                        explanation=(
                            f"Pratyaksha evidence is {age_days} days old "
                            f"(threshold: {self.staleness_threshold.days} days). "
                            f"Fresh observation needed before proceeding."
                        ),
                        is_extension=True,
                    )
        return FallacyResult(
            fallacy_type="kalatita",
            fallacy_english="stale evidence",
            detected=False,
            explanation="All Pratyaksha evidence is within freshness threshold.",
            is_extension=True,
        )
