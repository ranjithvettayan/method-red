"""
Agent module for Red Team MCP

Contains:
- ConfigurableAgent: Single agent implementation
- MultiAgentCoordinator: Multi-agent coordination
- CoordinationMode: Enum for coordination modes
"""

from src.agents.configurable_agent import ConfigurableAgent
from src.agents.coordinator import MultiAgentCoordinator
from src.agents.modes import CoordinationMode

__all__ = [
    "ConfigurableAgent",
    "MultiAgentCoordinator",
    "CoordinationMode",
]
