"""
NyAI - A Nyaya-Grounded Artificial Human-Like Reasoning Agent

Built for Problem Statement P2: Unriddling Inference 2026, IIT Delhi
"""

from .pramana import PramanaType, Evidence, PRAMANA_STRENGTH, PRAMANA_ENGLISH
from .belief import Belief, BeliefStore, BeliefStatus
from .hetvabhasa import FallacyDetector, FallacyResult
from .pancavayava import generate_pancavayava, SyllogismStep
from .reasoning_agent import NyAIAgent, NaiveAgent

__all__ = [
    "PramanaType", "Evidence", "PRAMANA_STRENGTH", "PRAMANA_ENGLISH",
    "Belief", "BeliefStore", "BeliefStatus",
    "FallacyDetector", "FallacyResult",
    "generate_pancavayava", "SyllogismStep",
    "NyAIAgent", "NaiveAgent",
]
