"""
Pydantic models for API requests and responses
"""

# FastAPI imports (only imported when running API)
try:
    from pydantic import BaseModel, Field, field_validator
    from typing import Dict, Any, Optional, List, Union

    from src.agents import CoordinationMode

    PYDANTIC_AVAILABLE = True

    class ChatRequest(BaseModel):
        query: str = Field(
            ..., min_length=1, max_length=10000, description="The user's query message"
        )
        agent_id: Optional[str] = Field(
            None,
            max_length=100,
            description="Predefined agent ID to use (loads agent defaults)",
        )
        model_id: str = Field(
            ...,
            max_length=100,
            description="Model identifier (required - specify the exact model name)",
        )
        provider: str = Field(
            ...,
            max_length=50,
            description="Provider name (required - e.g., 'openai', 'anthropic', 'azure')",
        )
        agent_role: Optional[str] = Field(
            "Assistant", max_length=200, description="Agent role"
        )
        agent_goal: Optional[str] = Field(
            "Help users with their requests using advanced AI capabilities",
            max_length=500,
            description="Agent goal",
        )
        agent_backstory: Optional[str] = Field(
            "A versatile AI assistant capable of handling various tasks with access to multiple AI models",
            max_length=1000,
            description="Agent backstory",
        )
        session_id: Optional[str] = Field(
            None, max_length=100, description="Session identifier"
        )
        stream: Optional[bool] = Field(False, description="Enable streaming response")
        enable_memory: Optional[bool] = Field(
            True, description="Enable memory for the agent"
        )
        user_id: Optional[str] = Field(
            "anonymous", max_length=100, description="User identifier"
        )

        # Advanced sampling parameters
        temperature: Optional[float] = Field(
            None,
            ge=0.0,
            le=2.0,
            description="Controls randomness (0.0 = deterministic, 2.0 = very random)",
        )
        top_p: Optional[float] = Field(
            None, ge=0.0, le=1.0, description="Nucleus sampling parameter"
        )
        top_k: Optional[int] = Field(
            None,
            ge=1,
            le=1000,
            description="Top-k sampling (not supported by all providers)",
        )
        max_tokens: Optional[int] = Field(
            None, ge=1, le=4096, description="Maximum tokens to generate"
        )
        presence_penalty: Optional[float] = Field(
            None, ge=-2.0, le=2.0, description="Penalty for token presence"
        )
        frequency_penalty: Optional[float] = Field(
            None, ge=-2.0, le=2.0, description="Penalty for token frequency"
        )
        stop: Optional[List[str]] = Field(
            None, max_length=4, description="Stop sequences"
        )
        seed: Optional[int] = Field(
            None, description="Random seed for reproducible results"
        )
        logprobs: Optional[bool] = Field(None, description="Include log probabilities")
        reasoning_effort: Optional[str] = Field(
            None,
            description="Reasoning effort level",
            pattern="^(none|low|medium|high)$",
        )

        @field_validator("user_id")
        @classmethod
        def validate_user_id(cls, v):
            if not v or not v.strip():
                return "anonymous"
            return v.strip()


    class MultiAgentRequest(BaseModel):
        query: str = Field(
            ..., min_length=1, max_length=10000, description="The user's query message"
        )
        coordination_mode: CoordinationMode = Field(
            ..., description="Multi-agent coordination mode"
        )
        agents: Optional[List[Union[str, Dict[str, Any]]]] = Field(
            None,
            description="List of agent IDs (strings) or full agent configurations (dicts)",
        )
        rebuttal_limit: Optional[int] = Field(
            3, ge=1, le=10, description="Maximum number of rebuttals in debate mode (1-10)"
        )
        stream: Optional[bool] = Field(False, description="Enable streaming response")
        user_id: Optional[str] = Field(
            "anonymous", max_length=100, description="User identifier"
        )


    class TeamRequest(BaseModel):
        query: str = Field(
            ..., min_length=1, max_length=10000, description="The task for the team"
        )
        team_id: str = Field(
            ..., max_length=100, description="Team ID (e.g., 'writing_team', 'sales_team')"
        )
        coordination_mode: Optional[str] = Field(
            None,
            description="Override coordination mode (pipeline, ensemble, debate, swarm, hierarchical). Uses team default if not specified.",
        )
        rebuttal_limit: Optional[int] = Field(
            3, ge=1, le=10, description="Maximum rebuttals in debate mode"
        )
        stream: Optional[bool] = Field(False, description="Enable streaming response")
        user_id: Optional[str] = Field(
            "anonymous", max_length=100, description="User identifier"
        )

except ImportError:
    PYDANTIC_AVAILABLE = False
    ChatRequest = None
    MultiAgentRequest = None
    TeamRequest = None
