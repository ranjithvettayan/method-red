"""
Red Team MCP

A multi-agent collaboration platform supporting all models from models.dev
with advanced features including fine-tuning, sampling parameters, and more.

Modules:
- agents: ConfigurableAgent, MultiAgentCoordinator, CoordinationMode
- api: FastAPI REST/WebSocket endpoints
- cli: Command-line interfaces
- config: Configuration management
- models: Model selection and management
- providers: Provider registry and implementations
- mcp_server: MCP server implementation
"""

# Re-export main components for convenience
from src.agents import ConfigurableAgent, MultiAgentCoordinator, CoordinationMode
from src.config import config, setup_logging
from src.models import model_selector

__all__ = [
    "ConfigurableAgent",
    "MultiAgentCoordinator",
    "CoordinationMode",
    "config",
    "setup_logging",
    "model_selector",
]
