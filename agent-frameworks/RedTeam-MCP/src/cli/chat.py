"""
Single agent chat CLI interface
"""

import sys

from src.config import config
from src.cli.utils import get_or_create_cli_agent


def chat_cli():
    """CLI interface for single agent chat"""
    print("🤖 Single Agent Chat")
    print("=" * 30)

    # Get parameters from command line or interactively
    model_id = None
    provider = None
    role = "Assistant"
    goal = "Help users with their requests"
    backstory = "A helpful AI assistant"
    agent_id = None
    session_id = None
    enable_memory = True
    user_id = "cli_user"

    # Sampling parameters
    temperature = None
    top_p = None
    top_k = None
    max_tokens = None
    presence_penalty = None
    frequency_penalty = None
    stop = None
    seed = None
    logprobs = None
    reasoning_effort = None

    # Parse command line arguments
    args = sys.argv[2:]  # Skip 'main.py chat'
    query = None
    stream = False

    i = 0
    while i < len(args):
        if args[i] == "--model" and i + 1 < len(args):
            model_id = args[i + 1]
            i += 2
        elif args[i] == "--provider" and i + 1 < len(args):
            provider = args[i + 1]
            i += 2
        elif args[i] == "--role" and i + 1 < len(args):
            role = args[i + 1]
            i += 2
        elif args[i] == "--goal" and i + 1 < len(args):
            goal = args[i + 1]
            i += 2
        elif args[i] == "--backstory" and i + 1 < len(args):
            backstory = args[i + 1]
            i += 2
        elif args[i] == "--agent-id" and i + 1 < len(args):
            agent_id = args[i + 1]
            i += 2
        elif args[i] == "--session-id" and i + 1 < len(args):
            session_id = args[i + 1]
            i += 2
        elif args[i] == "--user-id" and i + 1 < len(args):
            user_id = args[i + 1]
            i += 2
        elif args[i] == "--no-memory":
            enable_memory = False
            i += 1
        elif args[i] == "--stream":
            stream = True
            i += 1
        # Sampling parameters
        elif args[i] == "--temperature" and i + 1 < len(args):
            temperature = float(args[i + 1])
            i += 2
        elif args[i] == "--top-p" and i + 1 < len(args):
            top_p = float(args[i + 1])
            i += 2
        elif args[i] == "--top-k" and i + 1 < len(args):
            top_k = int(args[i + 1])
            i += 2
        elif args[i] == "--max-tokens" and i + 1 < len(args):
            max_tokens = int(args[i + 1])
            i += 2
        elif args[i] == "--presence-penalty" and i + 1 < len(args):
            presence_penalty = float(args[i + 1])
            i += 2
        elif args[i] == "--frequency-penalty" and i + 1 < len(args):
            frequency_penalty = float(args[i + 1])
            i += 2
        elif args[i] == "--stop" and i + 1 < len(args):
            stop = args[i + 1]
            i += 2
        elif args[i] == "--seed" and i + 1 < len(args):
            seed = int(args[i + 1])
            i += 2
        elif args[i] == "--logprobs" and i + 1 < len(args):
            logprobs = int(args[i + 1])
            i += 2
        elif args[i] == "--reasoning-effort" and i + 1 < len(args):
            reasoning_effort = args[i + 1]
            i += 2
        else:
            # Assume it's the query
            query = " ".join(args[i:])
            break

    # Handle predefined agent
    if agent_id:
        predefined_agents = config.get_predefined_agents()
        if agent_id in predefined_agents:
            agent_config = predefined_agents[agent_id]
            model_id = agent_config.get("model_id", model_id)
            provider = agent_config.get("provider", provider)
            role = agent_config.get("role", role)
            goal = agent_config.get("goal", goal)
            backstory = agent_config.get("backstory", backstory)
            enable_memory = agent_config.get("enable_memory", enable_memory)
        else:
            print(f"❌ Predefined agent '{agent_id}' not found")
            return

    # Set defaults if not provided
    if not model_id:
        model_id = str(config.get('models.default', 'gpt-3.5-turbo'))
    if not provider:
        provider = "openai"  # Default provider

    if not query:
        print("Usage: python main.py chat [options] \"your query\"")
        print("\nOptions:")
        print("  --model MODEL_ID           Model to use (default: gpt-3.5-turbo)")
        print("  --provider PROVIDER        Provider (default: openai)")
        print("  --agent-id AGENT_ID        Use predefined agent configuration")
        print("  --role ROLE               Agent role")
        print("  --goal GOAL               Agent goal")
        print("  --backstory BACKSTORY     Agent backstory")
        print("  --session-id SESSION_ID   Session identifier for memory")
        print("  --user-id USER_ID         User identifier (default: cli_user)")
        print("  --no-memory              Disable memory for the agent")
        print("  --stream                  Enable streaming response")
        print("\nSampling Parameters:")
        print("  --temperature TEMP        Controls randomness (0.0-2.0)")
        print("  --top-p P                Nucleus sampling (0.0-1.0)")
        print("  --top-k K                Top-k sampling (1-1000)")
        print("  --max-tokens TOKENS      Maximum tokens to generate")
        print("  --presence-penalty P     Presence penalty (-2.0-2.0)")
        print("  --frequency-penalty P    Frequency penalty (-2.0-2.0)")
        print("  --stop WORD              Stop sequence")
        print("  --seed SEED              Random seed for reproducibility")
        print("  --logprobs N             Return log probabilities")
        print("  --reasoning-effort EFFORT Reasoning effort (low/medium/high)")
        print("\nExamples:")
        print("  python main.py chat --model claude-3-haiku-20240307 --provider anthropic \"Hello, how are you?\"")
        print("  python main.py chat --stream --temperature 0.7 --max-tokens 100 \"Tell me a story\"")
        print("  python main.py chat --agent-id financial_analyst \"Analyze this market trend\"")
        return

    try:
        # Create agent with full sampling parameters
        print(f"Creating agent with model: {model_id} ({provider})")
        if agent_id:
            print(f"Using predefined agent: {agent_id}")
        
        agent = get_or_create_cli_agent(
            model_id=model_id,
            provider=provider,
            role=role,
            goal=goal,
            backstory=backstory,
            enable_memory=enable_memory,
            session_id=session_id,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            stop=stop,
            seed=seed,
            logprobs=logprobs,
            reasoning_effort=reasoning_effort,
        )

        # Process query
        print(f"\n💭 Query: {query}")
        if stream:
            print("🤖 Response (streaming): ", end="", flush=True)
        else:
            print("🤖 Response: ", end="", flush=True)

        response = agent.process_request(query, stream=stream)
        if stream:
            # Handle streaming response
            for chunk in response:
                print(chunk, end="", flush=True)
            print()  # New line after streaming
        else:
            print(response)

    except Exception as e:
        print(f"❌ Error: {e}")
