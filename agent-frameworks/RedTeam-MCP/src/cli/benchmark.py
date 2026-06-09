"""
Performance benchmarking CLI interface
"""

import sys
import time

from src.agents import MultiAgentCoordinator, CoordinationMode
from src.cli.utils import get_or_create_cli_agent


def benchmark_cli():
    """CLI interface for running performance benchmarks"""
    print("📊 Performance Benchmarks")
    print("=" * 30)

    # Parse command line arguments
    args = sys.argv[2:]  # Skip 'main.py benchmark'
    benchmark_type = "single"
    model_id = None
    provider = None
    num_runs = 3

    i = 0
    while i < len(args):
        if args[i] == "--type" and i + 1 < len(args):
            benchmark_type = args[i + 1]
            i += 2
        elif args[i] == "--model" and i + 1 < len(args):
            model_id = args[i + 1]
            i += 2
        elif args[i] == "--provider" and i + 1 < len(args):
            provider = args[i + 1]
            i += 2
        elif args[i] == "--runs" and i + 1 < len(args):
            num_runs = int(args[i + 1])
            i += 2
        else:
            print(f"Unknown argument: {args[i]}")
            i += 1

    if benchmark_type not in ["single", "multi-agent"]:
        print(f"❌ Unknown benchmark type: {benchmark_type}")
        print("Available types: single, multi-agent")
        return

    # Set defaults
    if not model_id:
        model_id = "gpt-3.5-turbo"
    if not provider:
        provider = "openai"

    print(f"Running {benchmark_type} benchmark with {num_runs} runs...")
    print(f"Model: {model_id} ({provider})")

    if benchmark_type == "single":
        # Single agent benchmark
        try:
            agent = get_or_create_cli_agent(
                model_id=model_id,
                provider=provider,
                role="Benchmark Agent",
                goal="Respond to queries efficiently",
                backstory="A fast and accurate AI assistant"
            )

            test_query = "What is the capital of France?"
            times = []

            for run in range(num_runs):
                print(f"Run {run + 1}/{num_runs}...", end=" ", flush=True)
                start_time = time.time()
                response = agent.process_request(test_query, stream=False)
                end_time = time.time()
                elapsed = end_time - start_time
                times.append(elapsed)
                print(f"{elapsed:.2f}s")

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print("\n📈 Results:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  Min: {min_time:.2f}s")
            print(f"  Max: {max_time:.2f}s")
        except Exception as e:
            print(f"❌ Benchmark failed: {e}")

    elif benchmark_type == "multi-agent":
        # Multi-agent benchmark
        try:
            agents = [
                get_or_create_cli_agent(
                    model_id="gpt-3.5-turbo",
                    provider="openai",
                    role="Agent 1",
                    goal="Help with tasks",
                    backstory="AI assistant"
                ),
                get_or_create_cli_agent(
                    model_id="claude-3-haiku-20240307",
                    provider="anthropic",
                    role="Agent 2",
                    goal="Help with tasks",
                    backstory="AI assistant"
                )
            ]

            coordinator = MultiAgentCoordinator(agents)
            test_query = "What is 2+2?"
            times = []

            for run in range(num_runs):
                print(f"Run {run + 1}/{num_runs}...", end=" ", flush=True)
                start_time = time.time()
                response = coordinator.coordinate(CoordinationMode.ENSEMBLE, test_query, stream=False)
                end_time = time.time()
                elapsed = end_time - start_time
                times.append(elapsed)
                print(f"{elapsed:.2f}s")

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print("\n📈 Results:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  Min: {min_time:.2f}s")
            print(f"  Max: {max_time:.2f}s")
        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
