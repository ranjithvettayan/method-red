"""
REST API endpoints
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


def register_endpoints(app, limiter, config):
    """Register REST API endpoints with the FastAPI app"""
    from fastapi import HTTPException, Request
    from fastapi.responses import StreamingResponse
    
    from src.api.models import ChatRequest, MultiAgentRequest, TeamRequest
    from src.api.cache import get_or_create_agent
    from src.models import model_selector
    from src.agents import MultiAgentCoordinator, CoordinationMode

    @app.post("/chat")
    @limiter.limit(config.get("api.rate_limit", "100/minute"))
    async def chat(chat_request: ChatRequest, request: Request):
        """Single chat request endpoint with rate limiting"""
        try:
            from src.config import config as config_manager

            # Get predefined agents
            predefined_agents = config_manager.get_predefined_agents()

            # Handle predefined agent lookup
            agent_config = {}
            if chat_request.agent_id:
                if chat_request.agent_id not in predefined_agents:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Predefined agent '{chat_request.agent_id}' not found",
                    )
                agent_config = predefined_agents[chat_request.agent_id].copy()

            # Override with request parameters
            agent_config.update(
                {
                    "model_id": chat_request.model_id,
                    "provider": chat_request.provider,
                    "role": chat_request.agent_role
                    or agent_config.get("role", "Assistant"),
                    "goal": chat_request.agent_goal
                    or agent_config.get(
                        "goal",
                        "Help users with their requests using advanced AI capabilities",
                    ),
                    "backstory": chat_request.agent_backstory
                    or agent_config.get(
                        "backstory",
                        "A versatile AI assistant capable of handling various tasks with access to multiple AI models",
                    ),
                    "session_id": chat_request.session_id
                    or agent_config.get("session_id"),
                    "enable_memory": chat_request.enable_memory
                    if chat_request.enable_memory is not None
                    else agent_config.get("enable_memory", True),
                }
            )

            # Merge sampling parameters
            sampling_params = agent_config.get("sampling_params", {}).copy()
            request_sampling = {
                "temperature": chat_request.temperature,
                "top_p": chat_request.top_p,
                "top_k": chat_request.top_k,
                "max_tokens": chat_request.max_tokens,
                "presence_penalty": chat_request.presence_penalty,
                "frequency_penalty": chat_request.frequency_penalty,
                "stop": chat_request.stop,
                "seed": chat_request.seed,
                "logprobs": chat_request.logprobs,
                "reasoning_effort": chat_request.reasoning_effort,
            }
            # Override with request values (keep None values as-is)
            for key, value in request_sampling.items():
                if value is not None:
                    sampling_params[key] = value

            # Get or create agent
            agent = get_or_create_agent(
                model_id=agent_config["model_id"],
                provider=agent_config["provider"],
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                session_id=agent_config["session_id"],
                enable_memory=agent_config["enable_memory"],
                sampling_params=sampling_params,
            )

            # Process request with agent_id for usage tracking
            result = agent.process_request(
                chat_request.query, 
                stream=chat_request.stream,
                agent_id=chat_request.agent_id,
            )

            if chat_request.stream:
                return StreamingResponse(
                    result,
                    media_type="text/plain",
                    headers={"Content-Type": "text/plain; charset=utf-8"},
                )
            else:
                return {"response": result}

        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/multi-agent")
    @limiter.limit(config.get("api.rate_limit", "100/minute"))
    async def multi_agent(multi_request: MultiAgentRequest, request: Request):
        """Multi-agent collaboration endpoint"""
        try:
            from src.config import config as config_manager

            # Get predefined agents
            predefined_agents = config_manager.get_predefined_agents()

            # Create agents from request
            agents = []
            agent_configs = multi_request.agents or []

            if len(agent_configs) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="At least 2 agents are required for multi-agent collaboration",
                )

            for agent_config in agent_configs:
                if isinstance(agent_config, str):
                    # Agent ID - look up from predefined agents
                    if agent_config not in predefined_agents:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Predefined agent '{agent_config}' not found",
                        )
                    agent_data = predefined_agents[agent_config]
                elif isinstance(agent_config, dict):
                    # Full agent configuration
                    agent_data = agent_config
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Agent configuration must be either a string (agent ID) or dict",
                    )

                agent = get_or_create_agent(
                    model_id=agent_data.get("model_id") or config.get("models.default"),
                    provider=agent_data.get("provider", "openai"),
                    role=agent_data.get("role", "Assistant"),
                    goal=agent_data.get("goal", "Help with tasks"),
                    backstory=agent_data.get("backstory", "An AI assistant"),
                    session_id=agent_data.get("session_id"),
                    enable_memory=agent_data.get("enable_memory", True),
                    sampling_params=agent_data.get("sampling_params", {}),
                )
                agents.append(agent)

            # Create coordinator
            coordinator = MultiAgentCoordinator(agents)

            # Coordinate
            result = coordinator.coordinate(
                multi_request.coordination_mode,
                multi_request.query,
                stream=multi_request.stream,
                rebuttal_limit=multi_request.rebuttal_limit,
            )

            if multi_request.stream:
                return StreamingResponse(
                    result,
                    media_type="text/plain",
                    headers={"Content-Type": "text/plain; charset=utf-8"},
                )
            else:
                return {"response": result}

        except Exception as e:
            logger.error(f"Multi-agent error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/models")
    async def get_models():
        """Get all available models from models.dev"""
        return model_selector.list_available_models()

    @app.get("/agents")
    async def get_agents():
        """Get all predefined agents from configuration"""
        from src.config import config

        predefined_agents = config.get_predefined_agents()
        return {
            "agents": [
                {
                    "id": agent_id,
                    "name": agent.get("name", agent_id),
                    "model_id": agent.get("model_id"),
                    "role": agent.get("role"),
                    "goal": agent.get("goal"),
                    "description": agent.get("backstory", "")[:100] + "..."
                    if len(agent.get("backstory", "")) > 100
                    else agent.get("backstory", ""),
                }
                for agent_id, agent in predefined_agents.items()
            ]
        }

    @app.get("/teams")
    async def get_teams():
        """Get all available agent teams"""
        from src.config import config

        teams = config.get_teams()
        return {
            "teams": [
                {
                    "id": team_id,
                    "name": team.get("name", team_id),
                    "description": team.get("description", ""),
                    "agents": team.get("agents", []),
                    "default_mode": team.get("default_mode", "ensemble"),
                }
                for team_id, team in teams.items()
            ]
        }

    @app.get("/teams/{team_id}")
    async def get_team(team_id: str):
        """Get details about a specific team"""
        from src.config import config

        team = config.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")

        # Get full agent details
        predefined_agents = config.get_predefined_agents()
        agents_details = []
        for agent_id in team.get("agents", []):
            if agent_id in predefined_agents:
                agent = predefined_agents[agent_id]
                agents_details.append({
                    "id": agent_id,
                    "name": agent.get("name", agent_id),
                    "role": agent.get("role"),
                    "goal": agent.get("goal"),
                    "model_id": agent.get("model_id"),
                    "provider": agent.get("provider"),
                })

        return {
            "id": team_id,
            "name": team.get("name", team_id),
            "description": team.get("description", ""),
            "default_mode": team.get("default_mode", "ensemble"),
            "agents": agents_details,
        }

    @app.post("/team")
    @limiter.limit(config.get("api.rate_limit", "100/minute"))
    async def run_team(team_request: TeamRequest, request: Request):
        """Run a task using a predefined team of agents"""
        try:
            from src.db import get_db
            from src.api.cache import clear_agent_cache

            db = get_db()
            # Clear agent cache to ensure fresh agents with updated settings
            clear_agent_cache()

            # Get team configuration from database
            team = db.get_team(team_request.team_id)
            if not team:
                raise HTTPException(
                    status_code=404,
                    detail=f"Team '{team_request.team_id}' not found",
                )

            # Database uses "members", config uses "agents" - support both
            agent_ids = team.get("members", []) or team.get("agents", [])
            if not agent_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Team '{team_request.team_id}' has no agents configured",
                )

            # Use team's default mode if not specified
            mode_str = team_request.coordination_mode or team.get("default_mode", "ensemble")

            # Validate coordination mode
            mode_map = {
                "pipeline": CoordinationMode.PIPELINE,
                "ensemble": CoordinationMode.ENSEMBLE,
                "debate": CoordinationMode.DEBATE,
                "swarm": CoordinationMode.SWARM,
                "hierarchical": CoordinationMode.HIERARCHICAL,
            }

            if mode_str not in mode_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid coordination mode '{mode_str}'. Available: {', '.join(mode_map.keys())}",
                )

            mode = mode_map[mode_str]

            # Get agents from database
            agents = []

            for agent_id in agent_ids:
                agent_data = db.get_agent(agent_id)
                if not agent_data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Agent '{agent_id}' from team not found",
                    )

                agent = get_or_create_agent(
                    model_id=agent_data.get("model_id"),
                    provider=agent_data.get("provider", "openai"),
                    role=agent_data.get("role", "Assistant"),
                    goal=agent_data.get("goal", "Help with tasks"),
                    backstory=agent_data.get("backstory", "An AI assistant"),
                    session_id=agent_data.get("session_id"),
                    enable_memory=agent_data.get("enable_memory", True),
                    sampling_params=agent_data.get("sampling_params", {}),
                )
                agents.append(agent)

            # Create coordinator and run
            coordinator = MultiAgentCoordinator(agents)
            
            if team_request.stream:
                result = coordinator.coordinate(
                    mode,
                    team_request.query,
                    stream=True,
                    rebuttal_limit=team_request.rebuttal_limit,
                )
                return StreamingResponse(
                    result,
                    media_type="text/plain",
                    headers={"Content-Type": "text/plain; charset=utf-8"},
                )
            else:
                # Use coordinate_with_history for non-streaming to get individual responses
                result = coordinator.coordinate_with_history(
                    mode,
                    team_request.query,
                    rebuttal_limit=team_request.rebuttal_limit,
                )
                return {
                    "team": team.get("name", team_request.team_id),
                    "mode": mode_str,
                    "conversation": result.get("conversation", []),
                    "response": result.get("final_response", ""),
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Team error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ==================== Custom Providers ====================
    
    @app.get("/custom-providers")
    async def get_custom_providers():
        """Get all custom providers"""
        from src.db import get_db
        db = get_db()
        providers = db.get_custom_providers()
        return {"providers": providers}
    
    @app.get("/custom-providers/{provider_id}")
    async def get_custom_provider(provider_id: str):
        """Get a specific custom provider"""
        from src.db import get_db
        db = get_db()
        provider = db.get_custom_provider(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Custom provider '{provider_id}' not found")
        return provider
    
    @app.post("/custom-providers")
    async def create_custom_provider(request: Request):
        """Create a new custom provider"""
        from src.db import get_db
        from src.providers import provider_registry
        
        data = await request.json()
        
        # Validate required fields
        if not data.get("id"):
            raise HTTPException(status_code=400, detail="Provider ID is required")
        if not data.get("base_url"):
            raise HTTPException(status_code=400, detail="Base URL is required")
        
        db = get_db()
        
        # Check if provider already exists
        if db.get_custom_provider(data["id"]):
            raise HTTPException(status_code=400, detail=f"Provider '{data['id']}' already exists")
        
        # Create provider
        provider = db.create_custom_provider({
            "id": data["id"],
            "name": data.get("name", data["id"]),
            "base_url": data["base_url"],
            "api_key": data.get("api_key", ""),
            "provider_type": data.get("provider_type", "openai-compatible"),
            "is_enabled": data.get("is_enabled", True)
        })
        
        # Reload custom providers
        provider_registry.reload_custom_providers()
        
        return provider
    
    @app.put("/custom-providers/{provider_id}")
    async def update_custom_provider(provider_id: str, request: Request):
        """Update an existing custom provider"""
        from src.db import get_db
        from src.providers import provider_registry
        
        data = await request.json()
        db = get_db()
        
        provider = db.update_custom_provider(provider_id, data)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Custom provider '{provider_id}' not found")
        
        # Reload custom providers
        provider_registry.reload_custom_providers()
        
        return provider
    
    @app.delete("/custom-providers/{provider_id}")
    async def delete_custom_provider(provider_id: str):
        """Delete a custom provider"""
        from src.db import get_db
        from src.providers import provider_registry
        
        db = get_db()
        if not db.delete_custom_provider(provider_id):
            raise HTTPException(status_code=404, detail=f"Custom provider '{provider_id}' not found")
        
        # Reload custom providers
        provider_registry.reload_custom_providers()
        
        return {"status": "deleted", "id": provider_id}
    
    # ==================== Custom Models ====================
    
    @app.get("/custom-providers/{provider_id}/models")
    async def get_custom_models(provider_id: str):
        """Get all models for a custom provider"""
        from src.db import get_db
        db = get_db()
        
        # Verify provider exists
        if not db.get_custom_provider(provider_id):
            raise HTTPException(status_code=404, detail=f"Custom provider '{provider_id}' not found")
        
        models = db.get_custom_models(provider_id)
        return {"models": models}
    
    @app.post("/custom-providers/{provider_id}/models")
    async def create_custom_model(provider_id: str, request: Request):
        """Create a new model for a custom provider"""
        from src.db import get_db
        from src.providers import provider_registry
        
        data = await request.json()
        db = get_db()
        
        # Verify provider exists
        if not db.get_custom_provider(provider_id):
            raise HTTPException(status_code=404, detail=f"Custom provider '{provider_id}' not found")
        
        # Validate required fields
        if not data.get("model_name"):
            raise HTTPException(status_code=400, detail="Model name is required")
        
        # Generate ID if not provided
        model_id = data.get("id", f"{provider_id}:{data['model_name']}")
        
        # Check if model already exists
        if db.get_custom_model(model_id):
            raise HTTPException(status_code=400, detail=f"Model '{model_id}' already exists")
        
        model = db.create_custom_model({
            "id": model_id,
            "provider_id": provider_id,
            "model_name": data["model_name"],
            "display_name": data.get("display_name", data["model_name"]),
            "context_length": data.get("context_length", 4096),
            "max_output": data.get("max_output", 4096),
            "supports_vision": data.get("supports_vision", False),
            "supports_tools": data.get("supports_tools", False),
            "supports_streaming": data.get("supports_streaming", True)
        })
        
        # Reload custom providers
        provider_registry.reload_custom_providers()
        
        return model
    
    @app.put("/custom-models/{model_id}")
    async def update_custom_model(model_id: str, request: Request):
        """Update an existing custom model"""
        from src.db import get_db
        from src.providers import provider_registry
        
        data = await request.json()
        db = get_db()
        
        model = db.update_custom_model(model_id, data)
        if not model:
            raise HTTPException(status_code=404, detail=f"Custom model '{model_id}' not found")
        
        # Reload custom providers
        provider_registry.reload_custom_providers()
        
        return model
    
    @app.delete("/custom-models/{model_id}")
    async def delete_custom_model(model_id: str):
        """Delete a custom model"""
        from src.db import get_db
        from src.providers import provider_registry
        
        db = get_db()
        if not db.delete_custom_model(model_id):
            raise HTTPException(status_code=404, detail=f"Custom model '{model_id}' not found")
        
        # Reload custom providers
        provider_registry.reload_custom_providers()
        
        return {"status": "deleted", "id": model_id}
    
    @app.post("/custom-providers/{provider_id}/test")
    async def test_custom_provider(provider_id: str):
        """Test connection to a custom provider"""
        from src.db import get_db
        import httpx
        
        db = get_db()
        provider = db.get_custom_provider(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Custom provider '{provider_id}' not found")
        
        base_url = provider["base_url"].rstrip("/")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try common endpoints for model listing
                headers = {}
                if provider.get("api_key"):
                    headers["Authorization"] = f"Bearer {provider['api_key']}"
                
                # Try /v1/models endpoint (OpenAI-compatible)
                response = await client.get(f"{base_url}/models", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("data", data.get("models", []))
                    return {
                        "status": "connected",
                        "models_found": len(models),
                        "models": [m.get("id", m) if isinstance(m, dict) else m for m in models[:10]]
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Server returned status {response.status_code}"
                    }
        except httpx.ConnectError:
            return {"status": "error", "message": "Could not connect to server"}
        except httpx.TimeoutException:
            return {"status": "error", "message": "Connection timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0.0",
        }
