"""
Pramana (means of valid knowledge) - The four ways we know things.

Hierarchy: Pratyaksha(4) > Anumana(3) > Shabda(2) > Upamana(1)
Higher strength = more trustworthy evidence.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class PramanaType(Enum):
    PRATYAKSHA = "pratyaksha"   # Direct perception (user-reported data)
    ANUMANA = "anumana"         # Inference (derived conclusions)
    SHABDA = "shabda"           # Testimony (authoritative texts/sources)
    UPAMANA = "upamana"         # Analogy (comparison with similar cases)


# Strength hierarchy - confirmed as philosophically correct
PRAMANA_STRENGTH = {
    PramanaType.PRATYAKSHA: 4,  # Strongest - direct experience
    PramanaType.ANUMANA: 3,     # Strong - logical inference
    PramanaType.SHABDA: 2,      # Moderate - scriptural/expert testimony
    PramanaType.UPAMANA: 1,     # Weakest - reasoning by analogy
}

PRAMANA_ENGLISH = {
    PramanaType.PRATYAKSHA: "direct perception",
    PramanaType.ANUMANA: "inference",
    PramanaType.SHABDA: "testimony",
    PramanaType.UPAMANA: "analogy",
}


@dataclass
class Evidence:
    """A single piece of evidence with its source type and metadata."""
    content: str
    pramana_type: PramanaType
    source: str = ""
    tags: list = field(default_factory=list)
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def strength(self) -> int:
        return PRAMANA_STRENGTH[self.pramana_type]

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "pramana_type": self.pramana_type.value,
            "pramana_english": PRAMANA_ENGLISH[self.pramana_type],
            "source": self.source,
            "tags": self.tags,
            "strength": self.strength,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
