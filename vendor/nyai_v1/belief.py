"""
Belief and BeliefStore - How the agent stores and revises what it knows.

Belief revision rules (sacred - do not change):
1. Stronger pramana overrides weaker -> REVISE
2. Equal strength conflict -> SUSPEND
3. Weaker contradicts stronger -> RETAIN (note but don't apply)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from datetime import datetime
from .pramana import Evidence, PramanaType, PRAMANA_STRENGTH


class BeliefStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVISED = "revised"
    REJECTED = "rejected"


@dataclass
class Belief:
    """A belief held by the agent, with full revision history."""
    claim: str
    evidence: List[Evidence] = field(default_factory=list)
    status: BeliefStatus = BeliefStatus.ACTIVE
    revision_history: List[dict] = field(default_factory=list)
    created_at: Optional[datetime] = None
    evidence_timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def strongest_pramana(self) -> Optional[PramanaType]:
        if not self.evidence:
            return None
        return max(self.evidence, key=lambda e: e.strength).pramana_type

    @property
    def pramana_types(self) -> set:
        return {e.pramana_type for e in self.evidence}

    @property
    def all_tags(self) -> set:
        tags = set()
        for e in self.evidence:
            tags.update(e.tags)
        return tags

    def add_evidence(self, evidence: Evidence):
        self.evidence.append(evidence)

    def revise(self, reason: str, new_status: BeliefStatus):
        self.revision_history.append({
            "from": self.status.value,
            "to": new_status.value,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        })
        self.status = new_status

    def to_dict(self) -> dict:
        return {
            "claim": self.claim,
            "status": self.status.value,
            "evidence": [e.to_dict() for e in self.evidence],
            "pramana_types": [p.value for p in self.pramana_types],
            "strongest_pramana": self.strongest_pramana.value if self.strongest_pramana else None,
            "revision_history": self.revision_history,
            "all_tags": list(self.all_tags),
        }


class BeliefStore:
    """The agent's knowledge base with Nyaya-grounded belief revision."""

    def __init__(self):
        self.beliefs: dict[str, Belief] = {}

    def add_belief(self, key: str, belief: Belief):
        self.beliefs[key] = belief

    def get_belief(self, key: str) -> Optional[Belief]:
        return self.beliefs.get(key)

    def revise_belief(self, key: str, new_evidence: Evidence, existing_belief: Belief) -> dict:
        """
        Apply Nyaya belief revision rules:
        - Stronger pramana overrides weaker -> REVISE
        - Equal strength -> SUSPEND
        - Weaker contradicts stronger -> RETAIN
        """
        existing_strength = max(e.strength for e in existing_belief.evidence)
        new_strength = new_evidence.strength

        if new_strength > existing_strength:
            existing_belief.add_evidence(new_evidence)
            existing_belief.revise("Stronger pramana overrides weaker", BeliefStatus.REVISED)
            action = "revised"
            explanation = (
                f"New evidence ({new_evidence.pramana_type.value}, strength {new_strength}) "
                f"overrides existing (strength {existing_strength}). Belief revised."
            )
        elif new_strength == existing_strength:
            existing_belief.add_evidence(new_evidence)
            existing_belief.revise("Equal strength conflict - suspending", BeliefStatus.SUSPENDED)
            action = "suspended"
            explanation = (
                f"Conflicting evidence at equal strength ({new_strength}). "
                f"Belief suspended pending more information."
            )
        else:
            existing_belief.add_evidence(new_evidence)
            action = "retained"
            explanation = (
                f"New evidence ({new_evidence.pramana_type.value}, strength {new_strength}) "
                f"is weaker than existing (strength {existing_strength}). Belief retained."
            )

        return {
            "action": action,
            "explanation": explanation,
            "belief": existing_belief.to_dict(),
        }

    def to_dict(self) -> dict:
        return {k: v.to_dict() for k, v in self.beliefs.items()}
