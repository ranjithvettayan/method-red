"""
Multi-agent coordination modes
"""

from enum import Enum


class CoordinationMode(Enum):
    """Multi-agent coordination modes"""

    PIPELINE = "pipeline"
    ENSEMBLE = "ensemble"
    DEBATE = "debate"
    SWARM = "swarm"
    HIERARCHICAL = "hierarchical"
