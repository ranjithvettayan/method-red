"""
MCP Server Generator CLI

Generates individual MCP servers for predefined agents,
allowing them to be used as standalone tools.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from src.config import config


def generate_agent_mcp_server(agent_id: str, agent_config: Dict[str, Any]) -> str:
    """Generate MCP server code for a specific agent"""

    server_code = f'''#!/usr/bin/env python3
"""
MCP Server for {agent_id} Agent

Auto-generated MCP server for the {agent_id} agent.
"""

import asyncio
import logging
from typing import Optional

from mcp.server import FastMCP

from src.config import config
from src.agents import ConfigurableAgent

logger = logging.getLogger(__name__)

# Initialize the MCP server
app = FastMCP("{agent_id}")

# Agent configuration
AGENT_CONFIG = {repr(agent_config)}

def get_agent() -> ConfigurableAgent:
    """Get or create the agent instance"""
    # Use agent configuration with defaults
    config_data = AGENT_CONFIG.copy()

    # Override with any environment-specific settings
    config_data.setdefault("enable_memory", True)
    config_data.setdefault("session_id", f"mcp_{agent_id}")

    return ConfigurableAgent(
        model_id=config_data["model_id"],
        role=config_data["role"],
        goal=config_data["goal"],
        backstory=config_data["backstory"],
        provider=config_data["provider"],
        enable_memory=config_data.get("enable_memory", True),
        session_id=config_data.get("session_id", f"mcp_{agent_id}"),
        **config_data.get("sampling_params", {{}})
    )

@app.tool()
async def chat(
    query: str,
    stream: bool = False,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> str:
    """Chat with the {agent_id} agent"""
    try:
        agent = get_agent()

        # Override sampling params if provided
        if temperature is not None or max_tokens is not None:
            # Create new agent with updated params
            config_data = AGENT_CONFIG.copy()
            sampling_params = config_data.get("sampling_params", {{}})
            if temperature is not None:
                sampling_params["temperature"] = temperature
            if max_tokens is not None:
                sampling_params["max_tokens"] = max_tokens

            agent = ConfigurableAgent(
                model_id=config_data["model_id"],
                role=config_data["role"],
                goal=config_data["goal"],
                backstory=config_data["backstory"],
                provider=config_data["provider"],
                enable_memory=config_data.get("enable_memory", True),
                session_id=config_data.get("session_id", f"mcp_{agent_id}"),
                **sampling_params
            )

        response = agent.process_request(query, stream=stream)

        if stream:
            # For streaming, collect all chunks
            chunks = []
            for chunk in response:
                chunks.append(chunk)
            return "".join(chunks)
        else:
            return str(response)

    except Exception as e:
        return f"❌ Error: {{str(e)}}"

@app.tool()
async def get_agent_info() -> str:
    """Get information about this agent"""
    config_data = AGENT_CONFIG
    return f"""**{agent_id} Agent**

- **Role**: {{config_data.get('role', 'Unknown')}}
- **Goal**: {{config_data.get('goal', 'Unknown')}}
- **Model**: {{config_data.get('model_id', 'Unknown')}} ({{config_data.get('provider', 'Unknown')}})
- **Backstory**: {{config_data.get('backstory', 'Unknown')}}
- **Memory**: {{'Enabled' if config_data.get('enable_memory', True) else 'Disabled'}}
"""

if __name__ == "__main__":
    app.run()
'''

    return server_code


def generate_multi_agent_mcp_server() -> str:
    """Generate MCP server for multi-agent coordination"""

    server_code = '''#!/usr/bin/env python3
"""
MCP Server for Multi-Agent Coordination

Provides tools for coordinating multiple agents on complex tasks.
"""

import asyncio
import json
import logging
from typing import List, Optional, Dict, Any

from mcp.server.fastmcp import FastMCP

from src.config import config
from src.agents import ConfigurableAgent, MultiAgentCoordinator, CoordinationMode

logger = logging.getLogger(__name__)

# Initialize the MCP server
app = FastMCP("multi-agent-coordinator")

# Global agent cache
agents = {}
coordinators = {}

def get_or_create_agent(agent_id: str, agent_config: Dict[str, Any]) -> ConfigurableAgent:
    """Get or create an agent from predefined config"""
    if agent_id not in agents:
        agents[agent_id] = ConfigurableAgent(
            model_id=agent_config["model_id"],
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            provider=agent_config["provider"],
            enable_memory=agent_config.get("enable_memory", True),
            session_id=f"multi_agent_{agent_id}",
            **agent_config.get("sampling_params", {})
        )
    return agents[agent_id]

@app.tool()
async def list_available_agents() -> str:
    """List all predefined agents available for coordination"""
    try:
        predefined_agents = config.get_predefined_agents()
        if not predefined_agents:
            return "No predefined agents configured."

        result = []
        for agent_id, agent_config in predefined_agents.items():
            result.append(f"**{agent_id}**: {agent_config.get('role', 'Unknown')} - {agent_config.get('goal', 'No goal')}")

        return "\\n".join(result)
    except Exception as e:
        return f"❌ Error listing agents: {str(e)}"

@app.tool()
async def create_coordinator(
    coord_id: str,
    agent_ids: List[str],
    coordination_mode: str = "ensemble"
) -> str:
    """Create a multi-agent coordinator with specified agents"""
    try:
        # Validate coordination mode
        mode_map = {
            "pipeline": CoordinationMode.PIPELINE,
            "ensemble": CoordinationMode.ENSEMBLE,
            "debate": CoordinationMode.DEBATE,
            "swarm": CoordinationMode.SWARM,
            "hierarchical": CoordinationMode.HIERARCHICAL
        }

        if coordination_mode not in mode_map:
            return f"❌ Invalid coordination mode. Available: {', '.join(mode_map.keys())}"

        # Get predefined agents
        predefined_agents = config.get_predefined_agents()

        # Create agent instances
        agent_instances = []
        for agent_id in agent_ids:
            if agent_id not in predefined_agents:
                return f"❌ Agent '{agent_id}' not found in predefined agents"

            agent_config = predefined_agents[agent_id]
            agent = get_or_create_agent(agent_id, agent_config)
            agent_instances.append(agent)

        # Create coordinator
        coordinator = MultiAgentCoordinator(agent_instances)
        coordinators[coord_id] = coordinator

        return f"✅ Coordinator '{coord_id}' created with {len(agent_instances)} agents using {coordination_mode} mode"
    except Exception as e:
        return f"❌ Failed to create coordinator: {str(e)}"

@app.tool()
async def coordinate_task(
    coord_id: str,
    query: str,
    coordination_mode: str = "ensemble",
    stream: bool = False,
    rebuttal_limit: int = 3
) -> str:
    """Execute a task using the multi-agent coordinator"""
    try:
        if coord_id not in coordinators:
            return f"❌ Coordinator '{coord_id}' not found. Create it first with create_coordinator."

        coordinator = coordinators[coord_id]
        
        # Map coordination mode string to enum
        mode_map = {
            "pipeline": CoordinationMode.PIPELINE,
            "ensemble": CoordinationMode.ENSEMBLE,
            "debate": CoordinationMode.DEBATE,
            "swarm": CoordinationMode.SWARM,
            "hierarchical": CoordinationMode.HIERARCHICAL
        }
        mode = mode_map.get(coordination_mode, CoordinationMode.ENSEMBLE)

        response = coordinator.coordinate(
            mode=mode,
            query=query,
            stream=stream,
            rebuttal_limit=rebuttal_limit
        )

        if stream:
            chunks = []
            for chunk in response:
                chunks.append(chunk)
            return "".join(chunks)
        else:
            return str(response)

    except Exception as e:
        return f"❌ Error coordinating task: {str(e)}"

@app.tool()
async def list_active_coordinators() -> str:
    """List currently active coordinators"""
    try:
        if not coordinators:
            return "No active coordinators"

        result = []
        for coord_id, coordinator in coordinators.items():
            agent_count = len(coordinator.agents) if hasattr(coordinator, 'agents') else "unknown"
            result.append(f"**{coord_id}**: {agent_count} agents")

        return "\\n".join(result)
    except Exception as e:
        return f"❌ Error listing coordinators: {str(e)}"

@app.tool()
async def delete_coordinator(coord_id: str) -> str:
    """Delete a coordinator"""
    try:
        if coord_id in coordinators:
            del coordinators[coord_id]
            return f"✅ Coordinator '{coord_id}' deleted"
        else:
            return f"❌ Coordinator '{coord_id}' not found"
    except Exception as e:
        return f"❌ Error deleting coordinator: {str(e)}"


# ============== Team Tools ==============

@app.tool()
async def list_teams() -> str:
    """List all available agent teams"""
    try:
        teams = config.get_teams()
        if not teams:
            return "No teams configured."

        result = []
        for team_id, team_config in teams.items():
            team_agents = ", ".join(team_config.get("agents", []))
            result.append(
                f"**{team_id}** ({team_config.get('name', 'Unknown')})\\n"
                f"  - Description: {team_config.get('description', 'No description')}\\n"
                f"  - Agents: {team_agents}\\n"
                f"  - Default Mode: {team_config.get('default_mode', 'ensemble')}"
            )

        return "\\n\\n".join(result)
    except Exception as e:
        return f"❌ Error listing teams: {str(e)}"


@app.tool()
async def run_team(
    team_id: str,
    query: str,
    coordination_mode: Optional[str] = None,
    stream: bool = False,
    rebuttal_limit: int = 3
) -> str:
    """Run a task using a predefined team of agents. Easiest way to use multiple agents together."""
    try:
        # Get team configuration
        team = config.get_team(team_id)
        if not team:
            return f"❌ Team '{team_id}' not found. Use list_teams to see available teams."

        agent_ids = team.get("agents", [])
        if not agent_ids:
            return f"❌ Team '{team_id}' has no agents configured."

        # Use team's default mode if not specified
        mode_str = coordination_mode or team.get("default_mode", "ensemble")

        # Map coordination mode string to enum
        mode_map = {
            "pipeline": CoordinationMode.PIPELINE,
            "ensemble": CoordinationMode.ENSEMBLE,
            "debate": CoordinationMode.DEBATE,
            "swarm": CoordinationMode.SWARM,
            "hierarchical": CoordinationMode.HIERARCHICAL
        }

        if mode_str not in mode_map:
            return f"❌ Invalid coordination mode '{mode_str}'. Available: {', '.join(mode_map.keys())}"

        mode = mode_map[mode_str]

        # Get predefined agents and create them
        predefined_agents = config.get_predefined_agents()
        agent_instances = []

        for agent_id in agent_ids:
            if agent_id not in predefined_agents:
                return f"❌ Agent '{agent_id}' from team '{team_id}' not found."

            agent_config = predefined_agents[agent_id]
            agent = get_or_create_agent(agent_id, agent_config)
            agent_instances.append(agent)

        # Create a coordinator for this team
        coord_id = f"team_{team_id}"
        coordinator = MultiAgentCoordinator(agent_instances)
        coordinators[coord_id] = coordinator

        # Run the coordination
        response = coordinator.coordinate(
            mode=mode,
            query=query,
            stream=stream,
            rebuttal_limit=rebuttal_limit
        )

        if stream:
            chunks = []
            for chunk in response:
                chunks.append(chunk)
            result = "".join(chunks)
        else:
            result = str(response)

        team_name = team.get("name", team_id)
        return f"**{team_name}** ({mode_str} mode)\\n\\n{result}"

    except Exception as e:
        return f"❌ Error running team '{team_id}': {str(e)}"


if __name__ == "__main__":
    app.run()
'''

    return server_code


def generate_mcp_cli():
    """CLI interface for generating MCP servers"""
    print("🔧 MCP Server Generator")
    print("=" * 30)

    # Parse command line arguments
    args = sys.argv[2:]  # Skip 'main.py generate-mcp'

    output_dir = "mcp_servers"
    generate_multi_agent = False
    agent_filter = None

    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        elif args[i] == "--multi-agent":
            generate_multi_agent = True
            i += 1
        elif args[i] == "--agent" and i + 1 < len(args):
            agent_filter = args[i + 1]
            i += 2
        elif args[i] == "--all":
            generate_multi_agent = True
            i += 1
        elif args[i] in ("--help", "-h"):
            print_generate_mcp_help()
            return
        else:
            i += 1

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Get predefined agents
    predefined_agents = config.get_predefined_agents()

    if not predefined_agents:
        print("❌ No predefined agents found in configuration")
        return

    # Filter agents if specified
    if agent_filter:
        if agent_filter not in predefined_agents:
            print(f"❌ Agent '{agent_filter}' not found")
            print(f"Available agents: {', '.join(predefined_agents.keys())}")
            return
        agents_to_generate = {agent_filter: predefined_agents[agent_filter]}
    else:
        agents_to_generate = predefined_agents

    print(f"📦 Generating MCP servers for {len(agents_to_generate)} agent(s)...")
    print(f"📂 Output directory: {output_path.absolute()}")
    print()

    # Generate individual agent servers
    for agent_id, agent_config in agents_to_generate.items():
        server_code = generate_agent_mcp_server(agent_id, agent_config)

        filename = f"mcp_server_{agent_id}.py"
        filepath = output_path / filename

        with open(filepath, 'w') as f:
            f.write(server_code)

        print(f"  ✅ {filename}")

    # Generate multi-agent server if requested
    if generate_multi_agent:
        server_code = generate_multi_agent_mcp_server()
        filepath = output_path / "mcp_server_multi_agent.py"

        with open(filepath, 'w') as f:
            f.write(server_code)

        print(f"  ✅ mcp_server_multi_agent.py")

    # Generate __init__.py
    init_content = '''"""
MCP Servers for Red Team MCP

This package contains individual MCP servers for each predefined agent,
plus a multi-agent coordinator server.
"""

__version__ = "0.1.0"
'''
    with open(output_path / "__init__.py", 'w') as f:
        f.write(init_content)

    # Generate README
    readme_content = generate_mcp_readme(agents_to_generate, output_path)
    with open(output_path / "README.md", 'w') as f:
        f.write(readme_content)

    print()
    print(f"🎉 MCP servers generated in {output_path}/")
    print()
    print("To use these servers, add them to your MCP configuration.")
    print("Run 'python main.py generate-mcp --help' for configuration examples.")


def generate_mcp_readme(agents: Dict[str, Any], output_path: Path) -> str:
    """Generate README for generated MCP servers"""
    agent_list = "\n".join([
        f"- `mcp_server_{agent_id}.py` - {agent_config.get('role', agent_id)}"
        for agent_id, agent_config in agents.items()
    ])

    return f'''# Generated MCP Servers

This directory contains auto-generated MCP servers for Red Team MCP.

## Available Servers

{agent_list}
- `mcp_server_multi_agent.py` - Multi-agent coordination server

## Usage

### Claude Desktop Configuration

Add to `~/.config/claude/claude_desktop_config.json` (macOS/Linux) or 
`%APPDATA%\\Claude\\claude_desktop_config.json` (Windows):

```json
{{
  "mcpServers": {{
    "financial_analyst": {{
      "command": "python",
      "args": ["{output_path.absolute()}/mcp_server_financial_analyst.py"]
    }},
    "multi_agent": {{
      "command": "python",
      "args": ["{output_path.absolute()}/mcp_server_multi_agent.py"]
    }}
  }}
}}
```

### VS Code Configuration

Add to `.vscode/mcp.json`:

```json
{{
  "servers": {{
    "financial_analyst": {{
      "type": "stdio",
      "command": "python",
      "args": ["{output_path.absolute()}/mcp_server_financial_analyst.py"]
    }}
  }}
}}
```

## Regenerating

To regenerate these servers after updating agent configurations:

```bash
python main.py generate-mcp --all
```

To generate for a specific agent:

```bash
python main.py generate-mcp --agent financial_analyst
```
'''


def print_generate_mcp_help():
    """Print help for generate-mcp command"""
    print("""
Usage: python main.py generate-mcp [OPTIONS]

Generate MCP servers for predefined agents.

Options:
  --output-dir DIR    Output directory (default: mcp_servers)
  --agent AGENT_ID    Generate server for a specific agent only
  --multi-agent       Also generate multi-agent coordinator server
  --all               Generate all servers including multi-agent
  --help, -h          Show this help message

Examples:
  # Generate all agent servers
  python main.py generate-mcp

  # Generate all servers including multi-agent coordinator
  python main.py generate-mcp --all

  # Generate for a specific agent
  python main.py generate-mcp --agent financial_analyst

  # Generate to a custom directory
  python main.py generate-mcp --output-dir ./my_mcp_servers --all

Claude Desktop Configuration Example:
  Add to ~/.config/claude/claude_desktop_config.json:

  {
    "mcpServers": {
      "financial_analyst": {
        "command": "python",
        "args": ["/path/to/mcp_servers/mcp_server_financial_analyst.py"]
      },
      "multi_agent": {
        "command": "python",
        "args": ["/path/to/mcp_servers/mcp_server_multi_agent.py"]
      }
    }
  }

VS Code Configuration Example:
  Add to .vscode/mcp.json:

  {
    "servers": {
      "financial_analyst": {
        "type": "stdio",
        "command": "python",
        "args": ["./mcp_servers/mcp_server_financial_analyst.py"]
      }
    }
  }
""")
