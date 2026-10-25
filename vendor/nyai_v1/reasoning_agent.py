"""
NyAI Reasoning Agent - The P2 deliverable.

The agent that reasons, changes its mind, and admits uncertainty.
Also includes NaiveAgent (baseline) for comparison.
"""

from typing import List, Optional
from datetime import datetime
from .pramana import Evidence, PramanaType
from .belief import Belief, BeliefStore, BeliefStatus
from .hetvabhasa import FallacyDetector, FallacyResult
from .pancavayava import generate_pancavayava, SyllogismStep


class NyAIAgent:
    """
    Nyaya-grounded reasoning agent.

    This agent:
    - Labels every piece of knowledge with its source type (pramana)
    - Checks for fallacies before accepting conclusions
    - Revises beliefs when stronger evidence arrives
    - Admits uncertainty when evidence conflicts
    - Produces 5-step reasoning traces for every decision
    """

    def __init__(self):
        self.belief_store = BeliefStore()
        self.fallacy_detector = FallacyDetector()
        self.reasoning_log: List[dict] = []

    def evaluate_claim(
        self,
        claim: str,
        evidence: List[Evidence],
        context: Optional[dict] = None,
        evidence_timestamp: Optional[datetime] = None,
    ) -> dict:
        """
        Evaluate a claim through the full Nyaya reasoning pipeline.

        Returns a complete reasoning trace with verdict, explanation,
        and Pancavayava syllogism.
        """
        context = context or {}

        # Create belief from evidence
        belief = Belief(claim=claim, evidence_timestamp=evidence_timestamp)
        for ev in evidence:
            belief.add_evidence(ev)

        # Run fallacy detection
        fallacy_results = self.fallacy_detector.check_all(belief, evidence_timestamp)
        detected_fallacies = [f for f in fallacy_results if f.detected]

        # Determine verdict
        verdict = self._determine_verdict(belief, detected_fallacies)

        # Apply verdict to belief
        if verdict == "rejected":
            belief.revise("Fallacy detected", BeliefStatus.REJECTED)
        elif verdict == "suspended":
            belief.revise("Evidence stale or insufficient", BeliefStatus.SUSPENDED)

        # Generate Pancavayava trace
        pancavayava = generate_pancavayava(
            belief=belief,
            verdict=verdict,
            fallacy_results=fallacy_results,
            context=context,
        )

        # Store belief
        key = claim[:50].lower().replace(" ", "_")
        self.belief_store.add_belief(key, belief)

        # Build result
        result = {
            "claim": claim,
            "verdict": verdict,
            "belief": belief.to_dict(),
            "fallacy_results": [f.to_dict() for f in fallacy_results],
            "detected_fallacies": [f.to_dict() for f in detected_fallacies],
            "pancavayava": [s.to_dict() for s in pancavayava],
            "pramana_gate": self._pramana_gate(belief),
            "evidence_count": len(evidence),
            "pramana_types_used": [p.value for p in belief.pramana_types],
        }

        self.reasoning_log.append(result)
        return result

    def revise_belief(
        self,
        claim: str,
        existing_evidence: List[Evidence],
        new_evidence: Evidence,
        context: Optional[dict] = None,
    ) -> dict:
        """Handle belief revision when new contradicting evidence arrives."""
        context = context or {}

        # Create existing belief
        existing_belief = Belief(claim=claim)
        for ev in existing_evidence:
            existing_belief.add_evidence(ev)

        # Apply revision
        revision_result = self.belief_store.revise_belief(
            key=claim[:50].lower().replace(" ", "_"),
            new_evidence=new_evidence,
            existing_belief=existing_belief,
        )

        # Generate updated pancavayava
        verdict = revision_result["action"]
        pancavayava = generate_pancavayava(
            belief=existing_belief,
            verdict=verdict,
            context=context,
        )

        result = {
            "claim": claim,
            "verdict": verdict,
            "revision": revision_result,
            "belief": existing_belief.to_dict(),
            "pancavayava": [s.to_dict() for s in pancavayava],
            "pramana_gate": self._pramana_gate(existing_belief),
        }

        self.reasoning_log.append(result)
        return result

    def _determine_verdict(self, belief: Belief, detected_fallacies: List[FallacyResult]) -> str:
        """Determine the verdict based on fallacy checks and pramana gate."""
        # Check for Kalatita (stale) -> SUSPENDED
        for f in detected_fallacies:
            if f.fallacy_type == "kalatita":
                return "suspended"

        # Check for Satpratipaksha (equal-force conflict) -> UNCERTAIN
        for f in detected_fallacies:
            if f.fallacy_type == "satpratipaksha":
                return "uncertain"

        # Check for logical fallacies -> REJECTED
        logical_fallacies = [f for f in detected_fallacies
                            if f.fallacy_type in ("savyabhichara", "viruddha", "asiddha")]
        if logical_fallacies:
            return "rejected"

        # Pramana gate check
        gate = self._pramana_gate(belief)
        if not gate["passed"]:
            return "uncertain"

        return "accepted"

    def _pramana_gate(self, belief: Belief) -> dict:
        """
        Pramana gate: requires at least 2 different pramana types
        and at least 1 strong source (strength >= 3).
        """
        types = belief.pramana_types
        has_strong = any(e.strength >= 3 for e in belief.evidence)
        passed = len(types) >= 2 and has_strong

        return {
            "passed": passed,
            "pramana_count": len(types),
            "has_strong_source": has_strong,
            "explanation": (
                f"{'PASSED' if passed else 'FAILED'}: "
                f"{len(types)} pramana type(s) present "
                f"(need ≥2), strong source {'found' if has_strong else 'missing'} "
                f"(need ≥1 with strength ≥3)."
            ),
        }


class NaiveAgent:
    """
    Source-agnostic baseline agent.

    Accepts everything without checking sources, fallacies, or evidence quality.
    Used to demonstrate what NyAI catches that a naive approach misses.
    """

    def evaluate_claim(self, claim: str, evidence: List[Evidence], **kwargs) -> dict:
        """Always accepts if any evidence exists."""
        has_evidence = len(evidence) > 0
        return {
            "claim": claim,
            "verdict": "accepted" if has_evidence else "rejected",
            "explanation": (
                f"Found {len(evidence)} piece(s) of evidence. "
                f"{'Accepting claim.' if has_evidence else 'No evidence found.'}"
            ),
            "checks_performed": {
                "source_tracking": False,
                "fallacy_detection": False,
                "belief_revision": False,
                "pramana_gate": False,
                "staleness_check": False,
            },
            "what_it_missed": [],
        }
