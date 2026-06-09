"""
Team-based coordination CLI interface
"""

import sys

from src.config import config
from src.agents import MultiAgentCoordinator, CoordinationMode
from src.cli.utils import get_or_create_cli_agent


def team_cli():
    """CLI interface for team-based agent coordination"""
    print("🏢 Team Coordination")
    print("=" * 30)

    # Parse command line arguments
    args = sys.argv[2:]  # Skip 'main.py team'
    query = None
    team_id = None
    mode = None  # Will use team's default mode if not specified
    stream = False

    i = 0
    while i < len(args):
        if args[i] == "--team" and i + 1 < len(args):
            team_id = args[i + 1]
            i += 2
        elif args[i] == "--mode" and i + 1 < len(args):
            mode = args[i + 1]
            i += 2
        elif args[i] == "--stream":
            stream = True
            i += 1
        elif args[i] == "--list":
            # List available teams
            teams_data = config.get_teams()
            print("\nAvailable Teams:")
            for tid, team in teams_data.items():
                print(f"\n  📋 {tid}: {team.get('name', tid)}")
                print(f"     Description: {team.get('description', 'N/A')}")
                print(f"     Default Mode: {team.get('default_mode', 'ensemble')}")
                print(f"     Members: {', '.join(team.get('members', []))}")
            return
        else:
            # Assume it's the query
            query = " ".join(args[i:])
            break

    if not team_id:
        print("Usage: python main.py team --team TEAM_ID [options] \"your query\"")
        print("\nOptions:")
        print("  --team TEAM_ID    Team to use (required)")
        print("  --mode MODE       Override coordination mode: pipeline, ensemble, debate, swarm, hierarchical")
        print("  --stream         Enable streaming response")
        print("  --list           List all available teams")
        print("\nExamples:")
        print("  python main.py team --list")
        print("  python main.py team --team writing_team \"Write a blog post about AI trends\"")
        print("  python main.py team --team research_team --mode debate --stream \"What are the best ML frameworks?\"")
        return

    if not query:
        print("❌ Please provide a query after the options")
        return

    # Get team configuration
    team_data = config.get_team(team_id)
    if not team_data:
        print(f"❌ Team '{team_id}' not found")
        teams_data = config.get_teams()
        print(f"\nAvailable teams: {', '.join(teams_data.keys())}")
        return

    # Use team's default mode if not specified
    if not mode:
        mode = team_data.get('default_mode', 'ensemble')

    # Get team agents
    agent_configs = config.get_team_agents(team_id)
    if not agent_configs:
        print(f"❌ No agents found for team '{team_id}'")
        return

    try:
        agents = []
        agent_ids = []

        for agent_id, agent_config in agent_configs.items():
            agent = get_or_create_cli_agent(
                model_id=str(agent_config.get("model_id", "gpt-3.5-turbo")),
                provider=str(agent_config.get("provider", "openai")),
                role=str(agent_config.get("role", "Assistant")),
                goal=str(agent_config.get("goal", "Help with tasks")),
                backstory=str(agent_config.get("backstory", "An AI assistant")),
                enable_memory=agent_config.get("enable_memory", True),
                session_id=agent_config.get("session_id"),
            )
            agents.append(agent)
            agent_ids.append(agent_id)

        if len(agents) < 2:
            print("❌ Team needs at least 2 agents for coordination")
            return

        # Create coordinator
        coordinator = MultiAgentCoordinator(agents)

        # Map mode string to enum
        mode_map = {
            "pipeline": CoordinationMode.PIPELINE,
            "ensemble": CoordinationMode.ENSEMBLE,
            "debate": CoordinationMode.DEBATE,
            "swarm": CoordinationMode.SWARM,
            "hierarchical": CoordinationMode.HIERARCHICAL
        }

        if mode not in mode_map:
            print(f"❌ Unknown mode: {mode}")
            print(f"Available modes: {', '.join(mode_map.keys())}")
            return

        coord_mode = mode_map[mode]

        # Process query
        print(f"🏢 Team: {team_data.get('name', team_id)}")
        print(f"🤝 Mode: {mode}")
        print(f"👥 Agents: {', '.join(agent_ids)}")
        print(f"💭 Query: {query}")
        if stream:
            print("🤖 Response (streaming): ", end="", flush=True)
        else:
            print("🤖 Response: ", end="", flush=True)

        response = coordinator.coordinate(coord_mode, query, stream=stream)
        if stream:
            # Handle streaming response
            for chunk in response:
                print(chunk, end="", flush=True)
            print()  # New line after streaming
        else:
            print(response)

    except Exception as e:
        print(f"❌ Error: {e}")
