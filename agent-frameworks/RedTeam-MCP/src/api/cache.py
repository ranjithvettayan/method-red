"""
Agent caching utilities for API
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Global agent cache for reuse
_agent_cache: Dict[str, Any] = {}


def get_or_create_agent(
    model_id: str,
    provider: str,
    role: str,
    goal: str,
    backstory: str,
    session_id: Optional[str] = None,
    enable_memory: bool = True,
    sampling_params: Optional[Dict[str, Any]] = None,
):
    """Get cached agent or create new one with sampling parameters"""
    from src.agents import ConfigurableAgent
    
    # Create a simple cache key
    params_str = str(sorted((sampling_params or {}).items()))
    cache_key = f"{model_id}_{role}_{session_id or 'default'}_{hash(params_str)}"

    if cache_key not in _agent_cache:
        try:
            _agent_cache[cache_key] = ConfigurableAgent(
                model_id,
                role,
                goal,
                backstory,
                provider=provider,
                enable_memory=enable_memory,
                session_id=session_id,
                **(sampling_params or {}),
            )
        except Exception as e:
            raise ValueError(f"Failed to create agent: {str(e)}")

    return _agent_cache[cache_key]


def clear_agent_cache():
    """Clear the agent cache"""
    global _agent_cache
    _agent_cache = {}
