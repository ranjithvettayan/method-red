"""
Multi-agent coordination CLI interface
"""

import sys

from src.config import config
from src.agents import MultiAgentCoordinator, CoordinationMode
from src.cli.utils import get_or_create_cli_agent


def multi_agent_cli():
    """CLI interface for multi-agent coordination"""
    print("👥 Multi-Agent Coordination")
    print("=" * 35)

    # Parse command line arguments
    args = sys.argv[2:]  # Skip 'main.py multi-agent'
    query = None
    mode = "ensemble"
    rebuttal_limit = 3
    agent_ids = []
    stream = False

    i = 0
    while i < len(args):
        if args[i] == "--mode" and i + 1 < len(args):
            mode = args[i + 1]
            i += 2
        elif args[i] == "--rebuttal-limit" and i + 1 < len(args):
            rebuttal_limit = int(args[i + 1])
            i += 2
        elif args[i] == "--agents" and i + 1 < len(args):
            agent_ids = args[i + 1].split(",")
            i += 2
        elif args[i] == "--stream":
            stream = True
            i += 1
        else:
            # Assume it's the query
            query = " ".join(args[i:])
            break

    if not query:
        print("Usage: python main.py multi-agent [options] \"your query\"")
        print("\nOptions:")
        print("  --mode MODE             Coordination mode: pipeline, ensemble, debate, swarm, hierarchical (default: ensemble)")
        print("  --rebuttal-limit NUM    Max rebuttals for debate mode (default: 3)")
        print("  --agents ID1,ID2,...    Comma-separated agent IDs (default: financial_analyst,strategy_consultant)")
        print("  --stream               Enable streaming response")
        print("\nAvailable agents:")
        agents_data = config.get_predefined_agents()
        for agent_id in agents_data.keys():
            print(f"  - {agent_id}")
        print("\nExamples:")
        print("  python main.py multi-agent --mode debate --agents financial_analyst,strategy_consultant \"Should companies prioritize profit or sustainability?\"")
        print("  python main.py multi-agent --stream --mode ensemble --agents technical_expert,data_scientist \"Analyze this dataset\"")
        return

    # Set default agents if not specified
    if not agent_ids:
        agents_data = config.get_predefined_agents()
        agent_ids = list(agents_data.keys())[:2]  # Use first 2 agents

    try:
        # Get predefined agents
        agents_data = config.get_predefined_agents()
        agents = []

        for agent_id in agent_ids:
            if agent_id not in agents_data:
                print(f"❌ Agent '{agent_id}' not found")
                return

            agent_config = agents_data[agent_id]
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

        if len(agents) < 2:
            print("❌ Need at least 2 agents for multi-agent coordination")
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

        # Check for streaming option
        stream = "--stream" in args

        # Process query
        print(f"🤝 Mode: {mode}")
        print(f"👥 Agents: {', '.join(agent_ids)}")
        print(f"💭 Query: {query}")
        if stream:
            print("🤖 Response (streaming): ", end="", flush=True)
        else:
            print("🤖 Response: ", end="", flush=True)

        kwargs = {}
        if mode == "debate":
            kwargs["rebuttal_limit"] = rebuttal_limit

        response = coordinator.coordinate(coord_mode, query, stream=stream, **kwargs)
        if stream:
            # Handle streaming response
            for chunk in response:
                print(chunk, end="", flush=True)
            print()  # New line after streaming
        else:
            print(response)

    except Exception as e:
        print(f"❌ Error: {e}")
