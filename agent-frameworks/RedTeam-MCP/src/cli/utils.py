"""
CLI utility functions and shared state
"""

from typing import Optional

from src.agents import ConfigurableAgent


# Global agent cache for CLI performance (similar to server mode)
cli_agent_cache: dict = {}


def get_or_create_cli_agent(
    model_id: str,
    provider: str,
    role: str,
    goal: str,
    backstory: str,
    enable_memory: bool = True,
    session_id: Optional[str] = None,
    temperature=None,
    top_p=None,
    top_k=None,
    max_tokens=None,
    presence_penalty=None,
    frequency_penalty=None,
    stop=None,
    seed=None,
    logprobs=None,
    reasoning_effort=None,
) -> ConfigurableAgent:
    """Get cached agent or create new one with sampling parameters (CLI version)"""
    # Create a simple cache key
    params_str = str(sorted({
        'temperature': temperature,
        'top_p': top_p,
        'top_k': top_k,
        'max_tokens': max_tokens,
        'presence_penalty': presence_penalty,
        'frequency_penalty': frequency_penalty,
        'stop': stop,
        'seed': seed,
        'logprobs': logprobs,
        'reasoning_effort': reasoning_effort,
    }.items()))
    cache_key = f"{model_id}_{provider}_{role}_{session_id or 'default'}_{hash(params_str)}"

    if cache_key not in cli_agent_cache:
        try:
            cli_agent_cache[cache_key] = ConfigurableAgent(
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
            print(f"✅ Agent cached (key: {cache_key[:16]}...)")
        except Exception as e:
            raise Exception(f"Failed to create agent: {str(e)}")

    return cli_agent_cache[cache_key]
