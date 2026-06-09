#!/usr/bin/env python3
"""
Red Team MCP

A multi-agent collaboration platform supporting all models from models.dev
with advanced features including fine-tuning, sampling parameters, and more.
"""

import sys
import logging

# Setup logging
from src.config import config, setup_logging

# Import core modules
from src.models import model_selector
from src.agents import ConfigurableAgent, MultiAgentCoordinator, CoordinationMode

# Import CLI modules
from src.cli import (
    chat_cli,
    multi_agent_cli,
    team_cli,
    benchmark_cli,
    history_cli,
    generate_mcp_cli,
    get_or_create_cli_agent,
)

# Import API (creates app if FastAPI available)
from src.api import app, FASTAPI_AVAILABLE

# Import FastAPI only if available
try:
    import uvicorn
except ImportError:
    pass


def main():
    """Main entry point for the application"""
    # Setup logging
    setup_logging(
        log_level=config.get('logging.level', 'INFO'),
        log_file=config.get('logging.file', 'agent.log')
    )

    logger = logging.getLogger(__name__)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "serve":
            # Start the API server
            if not FASTAPI_AVAILABLE:
                logger.error("FastAPI dependencies not available. Install with: pip install fastapi uvicorn")
                sys.exit(1)

            host = config.get('api.host', '0.0.0.0')
            port = config.get('api.port', 8000)

            logger.info(f"Starting API server on {host}:{port}")
            uvicorn.run(
                "src.main:app",
                host=host,
                port=port,
                reload=False,
                log_level=config.get('logging.level', 'info').lower()
            )

        elif command == "mcp":
            # Start the dynamic MCP server
            from src.mcp_server_dynamic import main as mcp_main
            logger.info("Starting dynamic MCP server...")
            mcp_main()

        elif command == "models":
            # List available models
            models_data = model_selector.list_available_models()
            total_models = sum(len(provider['models']) for provider in models_data.values())

            print(f"Available models: {total_models} from {len(models_data)} providers")
            print("\nProviders:")
            for provider_id, provider in models_data.items():
                model_count = len(provider['models'])
                print(f"  {provider_id}: {provider['name']} ({model_count} models)")

        elif command == "chat":
            # Interactive chat with an agent
            chat_cli()

        elif command == "multi-agent":
            # Multi-agent coordination
            multi_agent_cli()

        elif command == "team":
            # Team-based coordination
            team_cli()

        elif command == "teams":
            # List teams
            teams_data = config.get_teams()
            print(f"Available Teams: {len(teams_data)}")
            print("\nTeams:")
            for team_id, team in teams_data.items():
                print(f"\n  📋 {team_id}: {team.get('name', team_id)}")
                print(f"     Description: {team.get('description', 'N/A')}")
                print(f"     Default Mode: {team.get('default_mode', 'ensemble')}")
                print(f"     Members: {', '.join(team.get('members', []))}")

        elif command == "agents":
            # List predefined agents
            agents_data = config.get_predefined_agents()
            print(f"Predefined agents: {len(agents_data)}")
            print("\nAgents:")
            for agent_id, agent in agents_data.items():
                print(f"  {agent_id}: {agent.get('name', agent_id)}")
                print(f"    Role: {agent.get('role', 'N/A')}")
                print(f"    Goal: {agent.get('goal', 'N/A')}")
                print(f"    Model: {agent.get('model_id', 'N/A')} ({agent.get('provider', 'N/A')})")
                print()

        elif command == "health":
            # Health check
            print("Health Check:")
            print("✅ CLI interface available")

            # Test model loading
            try:
                models_data = model_selector.list_available_models()
                total_models = sum(len(provider['models']) for provider in models_data.values())
                print(f"✅ Models loaded: {total_models} from {len(models_data)} providers")
            except Exception as e:
                print(f"❌ Model loading failed: {e}")

            # Test API availability
            if FASTAPI_AVAILABLE:
                print("✅ FastAPI available for server mode")
            else:
                print("❌ FastAPI not available")

        elif command == "benchmark":
            # Run performance benchmarks
            benchmark_cli()

        elif command == "history":
            # Manage conversation history
            history_cli()

        elif command == "generate-mcp":
            # Generate MCP servers for agents
            generate_mcp_cli()

        elif command == "admin":
            # Admin commands for database and token management
            from src.db import get_db, init_db
            
            db = init_db()
            
            if len(sys.argv) > 2:
                subcommand = sys.argv[2]
                
                if subcommand == "token":
                    # Show or regenerate token
                    if len(sys.argv) > 3 and sys.argv[3] == "--regenerate":
                        new_token = db.regenerate_token()
                        print("=" * 60)
                        print("New API token generated:")
                        print(f"  {new_token}")
                        print("=" * 60)
                        print("\nSave this token! It won't be shown again.")
                    else:
                        info = db.get_token_info()
                        if info["exists"]:
                            print("Token Info:")
                            print(f"  Prefix: {info['prefix']}...")
                            print(f"  Created: {info['created_at']}")
                            print("\nTo regenerate: python main.py admin token --regenerate")
                        else:
                            token = db.get_or_create_token()
                            print("=" * 60)
                            print("New API token generated:")
                            print(f"  {token}")
                            print("=" * 60)
                
                elif subcommand == "stats":
                    # Show database stats
                    agents = db.get_agents()
                    teams = db.get_teams()
                    settings = db.get_all_settings()
                    
                    print("Database Statistics:")
                    print(f"  Agents: {len(agents)}")
                    print(f"  Teams: {len(teams)}")
                    print(f"  Settings: {len(settings)}")
                    print(f"  Database: {db.db_path}")
                
                elif subcommand == "export":
                    # Export to JSON
                    import json
                    output = sys.argv[3] if len(sys.argv) > 3 else "export.json"
                    data = db.export_all()
                    with open(output, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"Exported to {output}")
                
                elif subcommand == "import":
                    # Import from JSON
                    import json
                    if len(sys.argv) < 4:
                        print("Usage: python main.py admin import <file.json> [--replace]")
                        sys.exit(1)
                    input_file = sys.argv[3]
                    replace = "--replace" in sys.argv
                    with open(input_file, 'r') as f:
                        data = json.load(f)
                    db.import_all(data, replace=replace)
                    print(f"Imported from {input_file}")
                    print(f"  Agents: {len(db.get_agents())}")
                    print(f"  Teams: {len(db.get_teams())}")
                
                elif subcommand == "migrate":
                    # Force migration from YAML
                    db.import_from_yaml_config(config)
                    print("Migrated from YAML config")
                    print(f"  Agents: {len(db.get_agents())}")
                    print(f"  Teams: {len(db.get_teams())}")
                
                else:
                    print(f"Unknown admin subcommand: {subcommand}")
                    print("Available: token, stats, export, import, migrate")
            else:
                # Default: show token and stats
                info = db.get_token_info()
                if info["exists"]:
                    print("API Token:")
                    print(f"  Prefix: {info['prefix']}...")
                    print(f"  Created: {info['created_at']}")
                else:
                    token = db.get_or_create_token()
                    print("=" * 60)
                    print("New API token generated:")
                    print(f"  {token}")
                    print("=" * 60)
                
                print("\nDatabase:")
                print(f"  Agents: {len(db.get_agents())}")
                print(f"  Teams: {len(db.get_teams())}")
                print(f"  Path: {db.db_path}")
                print("\nWeb UI: http://localhost:8000/ui/")
                print("\nAdmin commands:")
                print("  python main.py admin token              - Show token info")
                print("  python main.py admin token --regenerate - Generate new token")
                print("  python main.py admin stats              - Show statistics")
                print("  python main.py admin export [file]      - Export to JSON")
                print("  python main.py admin import <file>      - Import from JSON")
                print("  python main.py admin migrate            - Migrate from YAML")

        elif command == "test":
            # Test basic functionality
            print("Testing basic functionality...")

            # Test model loading
            models_data = model_selector.list_available_models()
            total_models = sum(len(provider['models']) for provider in models_data.values())
            print(f"✅ Loaded {total_models} models from {len(models_data)} providers")

            # Test a simple agent creation (will fail without API keys, but tests the code path)
            try:
                test_model = config.get('models.default')
                if test_model:
                    print(f"Testing agent creation with model: {test_model}")
                    agent = get_or_create_cli_agent(
                        model_id=str(test_model),
                        provider="openai",  # Default provider
                        role="Test Agent",
                        goal="Test goal",
                        backstory="Test backstory"
                    )
                    print("✅ Agent creation successful (may fail at runtime without API keys)")
                else:
                    print("❌ No default model configured")
            except Exception as e:
                print(f"❌ Agent creation failed: {e}")

            print("Basic functionality test completed.")

        else:
            print(f"Unknown command: {command}")
            print("Available commands: serve, mcp, admin, models, agents, teams, health, chat, multi-agent, team, benchmark, history, generate-mcp, test")

    else:
        # Interactive mode or default behavior
        print("Red Team MCP")
        print("======================")
        print()
        print("Commands:")
        print("  python main.py serve        - Start the API server (includes web UI)")
        print("  python main.py mcp          - Start dynamic MCP server (recommended)")
        print("  python main.py admin        - Manage tokens, database, and settings")
        print("  python main.py models       - List available models")
        print("  python main.py agents       - List predefined agents")
        print("  python main.py teams        - List available teams")
        print("  python main.py health       - Run health check")
        print("  python main.py chat [...]   - Chat with a single agent")
        print("  python main.py multi-agent  - Multi-agent coordination")
        print("  python main.py team [...]   - Team-based coordination")
        print("  python main.py benchmark    - Run performance benchmarks")
        print("  python main.py history      - Manage conversation history")
        print("  python main.py generate-mcp - Generate static MCP server files")
        print("  python main.py test         - Test basic functionality")
        print()
        print("Web Admin UI:")
        print("  Run 'python main.py serve' and visit http://localhost:8000/ui/")
        print("  Use 'python main.py admin' to see your API token for login.")
        print()
        print("MCP Integration:")
        print("  The 'mcp' command starts a single dynamic server exposing all agents.")
        print("  Add to Claude Desktop config (~/.config/claude/claude_desktop_config.json):")
        print('    {"mcpServers": {"agents": {"command": "python", "args": ["-m", "src.main", "mcp"]}}}')
        print()
        print("For detailed help on chat/multi-agent/team/benchmark commands, run them without arguments.")


if __name__ == "__main__":
    main()
