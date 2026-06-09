"""
Configurable AI Agent implementation
"""

import time
import logging
from typing import Dict, Any, Optional, Union, Generator

from crewai import Agent, Task, Crew, LLM
from crewai.memory import LongTermMemory, ShortTermMemory

from src.config import config
from src.models import model_selector
from src.providers import provider_registry

logger = logging.getLogger(__name__)


class ConfigurableAgent:
    """A configurable AI agent that can use any model from models.dev"""

    def __init__(
        self,
        model_id: str,
        role: str,
        goal: str,
        backstory: str,
        provider: str,
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
    ):
        self.model_id = model_id
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.session_id = session_id or f"session_{int(time.time())}"
        self.enable_memory = enable_memory

        # Store sampling parameters
        self.sampling_params = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_tokens": max_tokens,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stop": stop,
            "seed": seed,
            "logprobs": logprobs,
            "reasoning_effort": reasoning_effort,
        }

        self.provider = provider

        # Get full model info from model_selector for cost tracking
        full_model_info = model_selector.get_model_info(model_id, provider)
        if full_model_info:
            self.model_info = full_model_info
        else:
            # Fallback to synthetic model info if not found
            self.model_info = {
                "provider": provider,
                "provider_name": provider.title(),
                "model": {"tool_call": False, "cost": {"input": 0, "output": 0}}
            }
        print(
            f"Initialized agent with model: {model_id} from provider: {provider}"
        )

        # Create the appropriate LLM instance with sampling parameters
        self.llm = self._create_llm(**self.sampling_params)

        # Create memory systems if enabled
        self.memory_systems = []
        if enable_memory:
            self.memory_systems = [LongTermMemory(), ShortTermMemory()]

        # Create the agent
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=[],  # No tools for basic chat functionality
            llm=self.llm,
            memory=self.memory_systems[0] if self.memory_systems else None,
            allow_delegation=True,
        )

    def _create_llm(
        self,
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
    ):
        """Create the appropriate LLM instance based on the provider with sampling parameters"""
        from src.models import model_selector
        
        provider_id = self.model_info["provider"]  # type: ignore

        # Get API key from provider registry
        api_key = provider_registry.get_api_key(provider_id, self.model_id)
        if not api_key:
            raise ValueError(f"API key not configured for provider: {provider_id}")

        # Get model string from provider registry
        model_string = provider_registry.get_model_string(provider_id, self.model_id)
        
        # Get base URL for OpenAI-compatible providers
        base_url = provider_registry.get_base_url(provider_id)

        # Validate and adjust parameters based on model constraints from models.dev
        validation = model_selector.validate_and_adjust_params(
            model_id=self.model_id,
            provider_id=provider_id,
            temperature=temperature,
            max_tokens=max_tokens,
            reasoning_effort=reasoning_effort,
        )
        
        # Log any warnings about parameter adjustments
        for warning in validation.get('warnings', []):
            logger.warning(warning)
        
        validated_params = validation.get('params', {})
        constraints = validation.get('constraints', {})
        
        # Log model constraints for debugging
        logger.info(
            f"Model {self.model_id} constraints: "
            f"context={constraints.get('context_length')}, "
            f"max_output={constraints.get('max_output')}, "
            f"temp_support={constraints.get('supports_temperature')}, "
            f"reasoning={constraints.get('supports_reasoning')}"
        )
        
        # Build LLM kwargs with validated parameters
        llm_kwargs = {
            'model': model_string,
            'api_key': api_key,
        }
        
        # Add base_url for OpenAI-compatible providers
        if base_url:
            llm_kwargs['base_url'] = base_url
            logger.info(f"Using OpenAI-compatible mode with base_url: {base_url}")
        
        # Add validated parameters
        if 'temperature' in validated_params:
            llm_kwargs['temperature'] = validated_params['temperature']
        if 'max_tokens' in validated_params:
            llm_kwargs['max_tokens'] = validated_params['max_tokens']
        if 'reasoning_effort' in validated_params:
            llm_kwargs['reasoning_effort'] = validated_params['reasoning_effort']
        
        # Add other sampling parameters (these are passed through without validation)
        if top_p is not None:
            llm_kwargs['top_p'] = top_p
        if presence_penalty is not None:
            llm_kwargs['presence_penalty'] = presence_penalty
        if frequency_penalty is not None:
            llm_kwargs['frequency_penalty'] = frequency_penalty
        if stop is not None:
            llm_kwargs['stop'] = stop
        if seed is not None:
            llm_kwargs['seed'] = seed
        if logprobs is not None:
            llm_kwargs['logprobs'] = logprobs
        
        # Note: top_k is not supported by CrewAI LLM
        if top_k is not None:
            logger.warning("top_k parameter is not supported by CrewAI LLM, ignoring")

        return LLM(**llm_kwargs)  # type: ignore

    def process_request(
        self, request: str, stream: bool = False, agent_id: Optional[str] = None
    ) -> Union[str, Generator[str, None, None]]:
        """Process a request using the agent with tracking and optional streaming"""
        start_time = time.time()
        success = True
        error_message = None
        response_text = ""

        try:
            task = Task(
                description=request,
                agent=self.agent,
                expected_output="A response to the user's request.",
            )

            crew = Crew(agents=[self.agent], tasks=[task], verbose=not stream)

            result = crew.kickoff()

            # Extract the actual response from CrewOutput
            response_text = getattr(
                result, "raw", getattr(result, "output", str(result))
            )  # type: ignore

            response_time_ms = int((time.time() - start_time) * 1000)

            # Log usage to database
            self._log_usage(
                agent_id=agent_id,
                input_text=request,
                output_text=response_text,
                response_time_ms=response_time_ms,
                success=True,
            )

            if stream:
                # Return a generator for streaming
                def generate_chunks():
                    for i in range(
                        0, len(response_text), 50
                    ):  # Stream in 50-char chunks
                        chunk = response_text[i : i + 50]
                        yield chunk
                        time.sleep(0.05)  # Small delay for streaming effect

                return generate_chunks()
            else:
                return response_text

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            # Log failed request
            self._log_usage(
                agent_id=agent_id,
                input_text=request,
                output_text="",
                response_time_ms=response_time_ms,
                success=False,
                error_message=str(e),
            )
            raise e

    def _log_usage(
        self,
        agent_id: Optional[str],
        input_text: str,
        output_text: str,
        response_time_ms: int,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """Log API usage to the database"""
        try:
            from src.db import get_db
            
            db = get_db()
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            input_tokens = len(input_text) // 4
            output_tokens = len(output_text) // 4 if output_text else 0
            
            # Get cost info from model
            cost_info = self.model_info.get("model", {}).get("cost", {})
            input_cost = (input_tokens / 1_000_000) * cost_info.get("input", 0)
            output_cost = (output_tokens / 1_000_000) * cost_info.get("output", 0)
            total_cost = input_cost + output_cost
            
            db.log_usage({
                "agent_id": agent_id,
                "provider": self.model_info.get("provider", "unknown"),
                "model_id": self.model_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cached_tokens": 0,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost,
                "response_time_ms": response_time_ms,
                "success": success,
                "error_message": error_message,
            })
        except Exception as e:
            logger.warning(f"Failed to log usage: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_id": self.model_id,
            "provider": self.model_info["provider"],  # type: ignore
            "provider_name": self.model_info["provider_name"],  # type: ignore
            "capabilities": self.model_info["model"],  # type: ignore
        }
