"""
CLI module for Red Team MCP

Contains command-line interface implementations for:
- Single agent chat
- Multi-agent coordination
- Team-based coordination
- Benchmarking
- History management
- MCP server generation
"""

from src.cli.chat import chat_cli
from src.cli.multi_agent import multi_agent_cli
from src.cli.team import team_cli
from src.cli.benchmark import benchmark_cli
from src.cli.history import history_cli
from src.cli.generate_mcp import generate_mcp_cli
from src.cli.utils import get_or_create_cli_agent, cli_agent_cache

__all__ = [
    "chat_cli",
    "multi_agent_cli",
    "team_cli",
    "benchmark_cli",
    "history_cli",
    "generate_mcp_cli",
    "get_or_create_cli_agent",
    "cli_agent_cache",
]
