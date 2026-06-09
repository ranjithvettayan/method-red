"""
API module for Red Team MCP

Contains FastAPI REST and WebSocket endpoints organized into:
- models: Pydantic request/response models
- endpoints: REST API endpoints
- websockets: WebSocket handlers
"""

from src.api.app import app, create_app, FASTAPI_AVAILABLE
from src.api.models import ChatRequest, MultiAgentRequest, TeamRequest

__all__ = [
    "app",
    "create_app",
    "FASTAPI_AVAILABLE",
    "ChatRequest",
    "MultiAgentRequest",
    "TeamRequest",
]
