#!/usr/bin/env python3
"""
Dynamic MCP Server for Red Team MCP

A single MCP server that dynamically exposes all predefined agents,
teams, and coordination modes as tools. No code generation required -
agents are loaded from config at runtime.

Usage:
  python -m src.mcp_server_dynamic
  
Or add to Claude Desktop config:
  {
    "mcpServers": {
      "multi-llm-agents": {
        "command": "python",
        "args": ["-m", "src.mcp_server_dynamic"]
      }
    }
  }
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any

from mcp.server.fastmcp import FastMCP

from src.config import config
from src.agents import ConfigurableAgent, MultiAgentCoordinator, CoordinationMode

logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("multi-llm-agents")

# Agent and coordinator caches
_agent_cache: Dict[str, ConfigurableAgent] = {}
_coordinator_cache: Dict[str, MultiAgentCoordinator] = {}


def _get_or_create_agent(agent_id: str) -> ConfigurableAgent:
    """Get or create an agent instance from predefined config"""
    if agent_id not in _agent_cache:
        predefined = config.get_predefined_agents()
        if agent_id not in predefined:
            raise ValueError(f"Agent '{agent_id}' not found in configuration")
        
        agent_config = predefined[agent_id]
        _agent_cache[agent_id] = ConfigurableAgent(
            model_id=agent_config["model_id"],
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            provider=agent_config["provider"],
            enable_memory=agent_config.get("enable_memory", True),
            session_id=f"mcp_{agent_id}",
            **agent_config.get("sampling_params", {})
        )
    return _agent_cache[agent_id]


# ============== Agent Discovery Tools ==============

@mcp.tool()
async def list_agents() -> str:
    """List all available AI agents with their roles and capabilities.
    
    Returns a formatted list of all predefined agents that can be used
    for chat, coordination, or team tasks.
    """
    try:
        predefined = config.get_predefined_agents()
        if not predefined:
            return "No agents configured. Add agents to config/config.yaml"
        
        lines = ["# Available Agents\n"]
        for agent_id, cfg in predefined.items():
            lines.append(f"## {agent_id}")
            lines.append(f"- **Role**: {cfg.get('role', 'N/A')}")
            lines.append(f"- **Goal**: {cfg.get('goal', 'N/A')}")
            lines.append(f"- **Model**: {cfg.get('model_id', 'N/A')} ({cfg.get('provider', 'N/A')})")
            lines.append("")
        
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
async def list_teams() -> str:
    """List all available agent teams with their members and default modes.
    
    Teams are pre-configured groups of agents that work well together
    on specific types of tasks.
    """
    try:
        teams = config.get_teams()
        if not teams:
            return "No teams configured. Add teams to config/config.yaml"
        
        lines = ["# Available Teams\n"]
        for team_id, team in teams.items():
            lines.append(f"## {team.get('name', team_id)}")
            lines.append(f"- **ID**: `{team_id}`")
            lines.append(f"- **Description**: {team.get('description', 'N/A')}")
            lines.append(f"- **Members**: {', '.join(team.get('members', []))}")
            lines.append(f"- **Default Mode**: {team.get('default_mode', 'ensemble')}")
            lines.append("")
        
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
async def get_agent_info(agent_id: str) -> str:
    """Get detailed information about a specific agent.
    
    Args:
        agent_id: The ID of the agent to get info about
    """
    try:
        predefined = config.get_predefined_agents()
        if agent_id not in predefined:
            available = ", ".join(predefined.keys())
            return f"❌ Agent '{agent_id}' not found. Available: {available}"
        
        cfg = predefined[agent_id]
        return f"""# {agent_id} Agent

- **Role**: {cfg.get('role', 'N/A')}
- **Goal**: {cfg.get('goal', 'N/A')}
- **Backstory**: {cfg.get('backstory', 'N/A')}
- **Model**: {cfg.get('model_id', 'N/A')}
- **Provider**: {cfg.get('provider', 'N/A')}
- **Memory**: {'Enabled' if cfg.get('enable_memory', True) else 'Disabled'}
"""
    except Exception as e:
        return f"❌ Error: {e}"


# ============== Single Agent Chat ==============

@mcp.tool()
async def chat(
    agent_id: str,
    message: str,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> str:
    """Chat with a specific AI agent.
    
    Args:
        agent_id: The ID of the agent to chat with (use list_agents to see available)
        message: Your message or question for the agent
        temperature: Optional temperature override (0.0-2.0)
        max_tokens: Optional max tokens override
    """
    try:
        predefined = config.get_predefined_agents()
        if agent_id not in predefined:
            available = ", ".join(predefined.keys())
            return f"❌ Agent '{agent_id}' not found. Available: {available}"
        
        # Get or create agent (possibly with overridden params)
        if temperature is not None or max_tokens is not None:
            # Create fresh agent with custom params
            cfg = predefined[agent_id]
            sampling_params = cfg.get("sampling_params", {}).copy()
            if temperature is not None:
                sampling_params["temperature"] = temperature
            if max_tokens is not None:
                sampling_params["max_tokens"] = max_tokens
            
            agent = ConfigurableAgent(
                model_id=cfg["model_id"],
                role=cfg["role"],
                goal=cfg["goal"],
                backstory=cfg["backstory"],
                provider=cfg["provider"],
                enable_memory=cfg.get("enable_memory", True),
                session_id=f"mcp_{agent_id}_custom",
                **sampling_params
            )
        else:
            agent = _get_or_create_agent(agent_id)
        
        response = agent.process_request(message)
        return str(response)
    except Exception as e:
        return f"❌ Error: {e}"


# ============== Multi-Agent Coordination ==============

@mcp.tool()
async def coordinate(
    agent_ids: List[str],
    query: str,
    mode: str = "ensemble",
    rebuttal_limit: int = 3
) -> str:
    """Coordinate multiple agents to work on a task together.
    
    Args:
        agent_ids: List of agent IDs to coordinate (e.g., ["data_scientist", "strategy_consultant"])
        query: The task or question for the agents
        mode: Coordination mode - one of:
            - "pipeline": Agents work sequentially, each building on previous output
            - "ensemble": All agents respond, then synthesize results
            - "debate": Agents discuss and refine answers through rebuttals
            - "swarm": Dynamic task decomposition and assignment
            - "hierarchical": One agent leads, others support
        rebuttal_limit: For debate mode, max number of rebuttals (default: 3)
    """
    try:
        # Validate mode
        mode_map = {
            "pipeline": CoordinationMode.PIPELINE,
            "ensemble": CoordinationMode.ENSEMBLE,
            "debate": CoordinationMode.DEBATE,
            "swarm": CoordinationMode.SWARM,
            "hierarchical": CoordinationMode.HIERARCHICAL
        }
        
        if mode not in mode_map:
            return f"❌ Invalid mode '{mode}'. Available: {', '.join(mode_map.keys())}"
        
        # Get agents
        predefined = config.get_predefined_agents()
        agents = []
        for agent_id in agent_ids:
            if agent_id not in predefined:
                available = ", ".join(predefined.keys())
                return f"❌ Agent '{agent_id}' not found. Available: {available}"
            agents.append(_get_or_create_agent(agent_id))
        
        if len(agents) < 2:
            return "❌ Coordination requires at least 2 agents"
        
        # Create coordinator and run
        coordinator = MultiAgentCoordinator(agents)
        response = coordinator.coordinate(
            mode=mode_map[mode],
            query=query,
            rebuttal_limit=rebuttal_limit
        )
        
        return f"**Coordination Result** ({mode} mode with {len(agents)} agents)\n\n{response}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
async def run_team(
    team_id: str,
    query: str,
    mode: Optional[str] = None,
    rebuttal_limit: int = 3
) -> str:
    """Run a predefined team of agents on a task.
    
    Teams are pre-configured groups that work well together. This is the 
    easiest way to use multiple agents - just pick a team and give it a task.
    
    Args:
        team_id: The team to use (use list_teams to see available)
        query: The task or question for the team
        mode: Optional override for coordination mode (uses team default if not specified)
        rebuttal_limit: For debate mode, max rebuttals (default: 3)
    """
    try:
        team = config.get_team(team_id)
        if not team:
            teams = config.get_teams()
            available = ", ".join(teams.keys()) if teams else "none"
            return f"❌ Team '{team_id}' not found. Available: {available}"
        
        # Get agent IDs from team (support both 'members' and 'agents' keys)
        agent_ids = team.get("members", team.get("agents", []))
        if not agent_ids:
            return f"❌ Team '{team_id}' has no members configured"
        
        # Use team's default mode if not specified
        effective_mode = mode or team.get("default_mode", "ensemble")
        
        # Delegate to coordinate
        return await coordinate(
            agent_ids=agent_ids,
            query=query,
            mode=effective_mode,
            rebuttal_limit=rebuttal_limit
        )
    except Exception as e:
        return f"❌ Error: {e}"


# ============== Quick Access Tools ==============

@mcp.tool()
async def ask_expert(
    expertise: str,
    question: str
) -> str:
    """Ask a question to the most relevant expert agent.
    
    This tool automatically selects the best agent based on the expertise area.
    
    Args:
        expertise: Area of expertise needed - e.g., "financial", "technical", 
                   "creative", "data", "strategy", "marketing", "sales"
        question: Your question
    """
    try:
        predefined = config.get_predefined_agents()
        
        # Simple keyword matching to find relevant agent
        expertise_lower = expertise.lower()
        
        # Priority mappings
        expertise_map = {
            "financial": ["financial_analyst"],
            "finance": ["financial_analyst"],
            "money": ["financial_analyst"],
            "investment": ["financial_analyst"],
            "technical": ["technical_expert", "solutions_architect"],
            "tech": ["technical_expert", "solutions_architect"],
            "code": ["technical_expert"],
            "architecture": ["solutions_architect"],
            "security": ["security_analyst"],
            "creative": ["creative_writer", "editor"],
            "writing": ["creative_writer", "editor"],
            "content": ["creative_writer", "editor", "seo_specialist"],
            "data": ["data_scientist", "competitive_analyst"],
            "analysis": ["data_scientist", "competitive_analyst", "market_researcher"],
            "strategy": ["strategy_consultant", "marketing_strategist"],
            "marketing": ["marketing_strategist", "brand_manager", "seo_specialist"],
            "brand": ["brand_manager"],
            "social": ["social_media_manager"],
            "sales": ["sales_strategist", "account_executive", "sales_analyst"],
            "market": ["market_researcher", "competitive_analyst"],
            "research": ["market_researcher", "data_scientist"],
            "operations": ["operations_manager"],
            "seo": ["seo_specialist"],
        }
        
        # Find matching agent
        agent_id = None
        for key, candidates in expertise_map.items():
            if key in expertise_lower:
                for candidate in candidates:
                    if candidate in predefined:
                        agent_id = candidate
                        break
                if agent_id:
                    break
        
        if not agent_id:
            # Fall back to first available agent or strategy consultant
            agent_id = "strategy_consultant" if "strategy_consultant" in predefined else list(predefined.keys())[0]
        
        # Chat with the selected agent
        return await chat(agent_id=agent_id, message=question)
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool() 
async def brainstorm(
    topic: str,
    perspectives: int = 3
) -> str:
    """Get multiple perspectives on a topic from different agents.
    
    Automatically selects diverse agents to provide varied viewpoints.
    
    Args:
        topic: The topic or question to brainstorm about
        perspectives: Number of different perspectives to get (2-5, default: 3)
    """
    try:
        predefined = config.get_predefined_agents()
        
        # Select diverse agents
        diversity_order = [
            "strategy_consultant",
            "technical_expert", 
            "creative_writer",
            "data_scientist",
            "financial_analyst",
            "marketing_strategist",
            "operations_manager",
        ]
        
        selected = []
        for agent_id in diversity_order:
            if agent_id in predefined and len(selected) < perspectives:
                selected.append(agent_id)
        
        # Fill remaining with any available agents
        for agent_id in predefined:
            if agent_id not in selected and len(selected) < perspectives:
                selected.append(agent_id)
        
        if len(selected) < 2:
            return "❌ Need at least 2 agents for brainstorming"
        
        # Use ensemble mode for parallel perspectives
        return await coordinate(
            agent_ids=selected[:perspectives],
            query=f"Please provide your unique perspective on: {topic}",
            mode="ensemble"
        )
    except Exception as e:
        return f"❌ Error: {e}"


# ============== Session Management ==============

@mcp.tool()
async def clear_agent_cache() -> str:
    """Clear all cached agent instances.
    
    Use this to reset agent memory/state or after config changes.
    """
    global _agent_cache, _coordinator_cache
    count = len(_agent_cache)
    _agent_cache.clear()
    _coordinator_cache.clear()
    return f"✅ Cleared {count} cached agent(s)"


@mcp.tool()
async def reload_config() -> str:
    """Reload agent configuration from disk.
    
    Use this after editing config.yaml to pick up changes.
    """
    try:
        # Clear caches
        await clear_agent_cache()
        
        # Reload config
        config.reload()
        
        agents = config.get_predefined_agents()
        teams = config.get_teams()
        
        return f"✅ Config reloaded: {len(agents)} agents, {len(teams)} teams"
    except Exception as e:
        return f"❌ Error reloading config: {e}"


# ============== Resources ==============

@mcp.resource("agents://list")
async def resource_agents_list() -> str:
    """Resource listing all available agents"""
    return await list_agents()


@mcp.resource("teams://list")
async def resource_teams_list() -> str:
    """Resource listing all available teams"""
    return await list_teams()


@mcp.resource("agents://{agent_id}")
async def resource_agent_info(agent_id: str) -> str:
    """Resource for specific agent info"""
    return await get_agent_info(agent_id)


# ============== Entry Point ==============

def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
