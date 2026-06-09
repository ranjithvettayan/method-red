"""
CRUD API Endpoints for Agent Management

RESTful API for managing agents, teams, and settings.
All endpoints require token authentication.
"""

import logging
from typing import Optional, List
from functools import wraps

logger = logging.getLogger(__name__)

# Check for FastAPI availability
try:
    from fastapi import APIRouter, HTTPException, Depends, Header, Query, Request
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None

if FASTAPI_AVAILABLE:
    from src.db import get_db

    router = APIRouter(prefix="/api/v1", tags=["crud"])

    # ==================== Pydantic Models ====================

    class AgentCreate(BaseModel):
        id: str = Field(..., description="Unique agent ID")
        name: Optional[str] = Field(None, description="Display name")
        model_id: str = Field(..., description="Model ID (e.g., claude-3-haiku-20240307)")
        provider: str = Field(..., description="Provider (e.g., anthropic, openai)")
        role: str = Field(..., description="Agent role")
        goal: str = Field(..., description="Agent goal")
        backstory: str = Field(..., description="Agent backstory")
        enable_memory: bool = Field(True, description="Enable conversation memory")
        sampling_params: dict = Field(default_factory=dict, description="Sampling parameters")

    class AgentUpdate(BaseModel):
        name: Optional[str] = None
        model_id: Optional[str] = None
        provider: Optional[str] = None
        role: Optional[str] = None
        goal: Optional[str] = None
        backstory: Optional[str] = None
        enable_memory: Optional[bool] = None
        sampling_params: Optional[dict] = None

    class TeamCreate(BaseModel):
        id: str = Field(..., description="Unique team ID")
        name: Optional[str] = Field(None, description="Display name")
        description: str = Field("", description="Team description")
        default_mode: str = Field("ensemble", description="Default coordination mode")
        members: List[str] = Field(default_factory=list, description="List of agent IDs")

    class TeamUpdate(BaseModel):
        name: Optional[str] = None
        description: Optional[str] = None
        default_mode: Optional[str] = None
        members: Optional[List[str]] = None

    class SettingsUpdate(BaseModel):
        settings: dict = Field(..., description="Settings to update")

    class TokenResponse(BaseModel):
        token: str = Field(..., description="New API token")
        message: str = Field(..., description="Status message")

    class TokenInfo(BaseModel):
        prefix: Optional[str]
        created_at: Optional[str]
        exists: bool

    # ==================== Auth Dependency ====================

    async def verify_token(authorization: Optional[str] = Header(None)) -> bool:
        """Verify the API token from Authorization header"""
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
        token = parts[1]
        db = get_db()
        
        if not db.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return True

    # ==================== Agent Endpoints ====================

    @router.get("/agents")
    async def list_agents(auth: bool = Depends(verify_token)):
        """List all agents"""
        db = get_db()
        return {"agents": db.get_agents()}

    @router.get("/agents/{agent_id}")
    async def get_agent(agent_id: str, auth: bool = Depends(verify_token)):
        """Get a single agent by ID"""
        db = get_db()
        agent = db.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        return agent

    @router.post("/agents", status_code=201)
    async def create_agent(agent: AgentCreate, auth: bool = Depends(verify_token)):
        """Create a new agent"""
        db = get_db()
        
        # Check if agent already exists
        if db.get_agent(agent.id):
            raise HTTPException(status_code=409, detail=f"Agent '{agent.id}' already exists")
        
        created = db.create_agent(agent.model_dump())
        return created

    @router.put("/agents/{agent_id}")
    async def update_agent(agent_id: str, updates: AgentUpdate, auth: bool = Depends(verify_token)):
        """Update an existing agent"""
        db = get_db()
        
        # Filter out None values
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        
        updated = db.update_agent(agent_id, update_data)
        if not updated:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        return updated

    @router.delete("/agents/{agent_id}")
    async def delete_agent(agent_id: str, auth: bool = Depends(verify_token)):
        """Delete an agent"""
        db = get_db()
        
        if not db.delete_agent(agent_id):
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        return {"message": f"Agent '{agent_id}' deleted"}

    # ==================== Team Endpoints ====================

    @router.get("/teams")
    async def list_teams(auth: bool = Depends(verify_token)):
        """List all teams"""
        db = get_db()
        return {"teams": db.get_teams()}

    @router.get("/teams/{team_id}")
    async def get_team(team_id: str, auth: bool = Depends(verify_token)):
        """Get a single team by ID"""
        db = get_db()
        team = db.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")
        return team

    @router.post("/teams", status_code=201)
    async def create_team(team: TeamCreate, auth: bool = Depends(verify_token)):
        """Create a new team"""
        db = get_db()
        
        if db.get_team(team.id):
            raise HTTPException(status_code=409, detail=f"Team '{team.id}' already exists")
        
        # Validate members exist
        for agent_id in team.members:
            if not db.get_agent(agent_id):
                raise HTTPException(status_code=400, detail=f"Agent '{agent_id}' not found")
        
        created = db.create_team(team.model_dump())
        return created

    @router.put("/teams/{team_id}")
    async def update_team(team_id: str, updates: TeamUpdate, auth: bool = Depends(verify_token)):
        """Update an existing team"""
        db = get_db()
        
        # Filter out None values
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        
        # Validate members if provided
        if "members" in update_data:
            for agent_id in update_data["members"]:
                if not db.get_agent(agent_id):
                    raise HTTPException(status_code=400, detail=f"Agent '{agent_id}' not found")
        
        updated = db.update_team(team_id, update_data)
        if not updated:
            raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")
        
        return updated

    @router.delete("/teams/{team_id}")
    async def delete_team(team_id: str, auth: bool = Depends(verify_token)):
        """Delete a team"""
        db = get_db()
        
        if not db.delete_team(team_id):
            raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")
        
        return {"message": f"Team '{team_id}' deleted"}

    @router.post("/teams/{team_id}/members")
    async def add_team_member(
        team_id: str, 
        agent_id: str = Query(..., description="Agent ID to add"),
        auth: bool = Depends(verify_token)
    ):
        """Add an agent to a team"""
        db = get_db()
        
        if not db.get_team(team_id):
            raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")
        
        if not db.get_agent(agent_id):
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        if not db.add_team_member(team_id, agent_id):
            raise HTTPException(status_code=409, detail=f"Agent '{agent_id}' is already in team")
        
        return {"message": f"Agent '{agent_id}' added to team '{team_id}'"}

    @router.delete("/teams/{team_id}/members/{agent_id}")
    async def remove_team_member(team_id: str, agent_id: str, auth: bool = Depends(verify_token)):
        """Remove an agent from a team"""
        db = get_db()
        
        if not db.remove_team_member(team_id, agent_id):
            raise HTTPException(status_code=404, detail="Team member not found")
        
        return {"message": f"Agent '{agent_id}' removed from team '{team_id}'"}

    # ==================== Settings Endpoints ====================

    @router.get("/settings")
    async def get_settings(auth: bool = Depends(verify_token)):
        """Get all settings"""
        db = get_db()
        return {"settings": db.get_all_settings()}

    @router.put("/settings")
    async def update_settings(updates: SettingsUpdate, auth: bool = Depends(verify_token)):
        """Update settings"""
        db = get_db()
        db.update_settings(updates.settings)
        return {"message": "Settings updated", "settings": db.get_all_settings()}

    # ==================== Token Endpoints ====================

    @router.get("/token/info")
    async def get_token_info(auth: bool = Depends(verify_token)):
        """Get token metadata (not the token itself)"""
        db = get_db()
        return db.get_token_info()

    @router.post("/token/regenerate")
    async def regenerate_token(auth: bool = Depends(verify_token)):
        """Regenerate the API token"""
        db = get_db()
        new_token = db.regenerate_token()
        return TokenResponse(
            token=new_token,
            message="Token regenerated. Save this token - it won't be shown again!"
        )

    # ==================== Import/Export Endpoints ====================

    @router.get("/export")
    async def export_data(auth: bool = Depends(verify_token)):
        """Export all data as JSON"""
        db = get_db()
        return db.export_all()

    @router.post("/import")
    async def import_data(
        data: dict,
        replace: bool = Query(False, description="Replace existing data"),
        auth: bool = Depends(verify_token)
    ):
        """Import data from JSON"""
        db = get_db()
        db.import_all(data, replace=replace)
        return {"message": "Data imported successfully"}

    @router.post("/reset")
    async def reset_to_defaults(auth: bool = Depends(verify_token)):
        """Reset database to defaults from YAML config"""
        from src.config import config
        db = get_db()
        
        # Clear and reimport
        with db._get_conn() as conn:
            conn.execute("DELETE FROM team_members")
            conn.execute("DELETE FROM teams")
            conn.execute("DELETE FROM agents")
            conn.execute("DELETE FROM settings WHERE category != 'auth'")
        
        db.import_from_yaml_config(config)
        return {"message": "Reset to defaults", "agents": len(db.get_agents()), "teams": len(db.get_teams())}

    # ==================== Models Endpoints ====================

    @router.get("/models")
    async def list_models(
        provider: Optional[str] = Query(None, description="Filter by provider"),
        auth: bool = Depends(verify_token)
    ):
        """List available models (including custom provider models)"""
        from src.models import model_selector
        from src.db import get_db
        
        models_data = model_selector.list_available_models()
        
        if provider:
            # Check if it's a custom provider
            db = get_db()
            custom_provider = db.get_custom_provider(provider)
            if custom_provider:
                custom_models = db.get_custom_models(provider)
                return {
                    "providers": {
                        provider: {
                            "name": custom_provider.get("name", provider),
                            "is_custom": True,
                            "base_url": custom_provider.get("base_url", ""),
                            "models": [
                                {
                                    "id": m["id"],
                                    "name": m.get("display_name", m["model_name"]),
                                    "model_name": m["model_name"],
                                    "context_length": m.get("context_length", 4096),
                                    "max_output": m.get("max_output", 4096),
                                    "supports_vision": m.get("supports_vision", False),
                                    "supports_tools": m.get("supports_tools", False),
                                    "supports_streaming": m.get("supports_streaming", True),
                                }
                                for m in custom_models
                            ]
                        }
                    }
                }
            elif provider in models_data:
                return {"providers": {provider: models_data[provider]}}
            else:
                raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
        
        return {"providers": models_data}

    @router.get("/models/providers")
    async def list_providers(auth: bool = Depends(verify_token)):
        """List available providers (including custom)"""
        from src.models import model_selector
        from src.db import get_db
        
        models_data = model_selector.list_available_models()
        providers = [
            {"id": pid, "name": pdata.get("name", pid), "model_count": len(pdata.get("models", [])), "is_custom": False}
            for pid, pdata in models_data.items()
        ]
        
        # Add custom providers
        db = get_db()
        custom_providers = db.get_custom_providers()
        for cp in custom_providers:
            if cp.get("is_enabled", True):
                custom_models = db.get_custom_models(cp["id"])
                providers.append({
                    "id": cp["id"],
                    "name": f"🖥️ {cp['name']}" if cp.get("name") else f"🖥️ {cp['id']}",
                    "model_count": len(custom_models),
                    "is_custom": True,
                    "base_url": cp.get("base_url", "")
                })
        
        # Sort providers A-Z by name
        providers.sort(key=lambda p: p["name"].lower())
        return {"providers": providers}

    @router.get("/models/{model_id}/constraints")
    async def get_model_constraints(
        model_id: str,
        provider: Optional[str] = Query(None, description="Provider ID to search first"),
        auth: bool = Depends(verify_token)
    ):
        """Get model constraints (context length, max output, temperature support, reasoning)"""
        from src.models import model_selector
        
        constraints = model_selector.get_model_constraints(model_id, provider)
        model_info = model_selector.get_model_info(model_id, provider)
        
        return {
            "model_id": model_id,
            "provider": model_info.get('provider') if model_info else provider,
            "constraints": constraints
        }

    # ==================== Usage & Statistics Endpoints ====================

    @router.get("/stats")
    async def get_usage_stats(
        days: int = Query(30, ge=1, le=365, description="Number of days to include"),
        agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
        provider: Optional[str] = Query(None, description="Filter by provider"),
        auth: bool = Depends(verify_token)
    ):
        """Get usage statistics and cost breakdown"""
        db = get_db()
        stats = db.get_usage_stats(days=days, agent_id=agent_id, provider=provider)
        return stats

    @router.get("/stats/recent")
    async def get_recent_usage(
        limit: int = Query(50, ge=1, le=500, description="Number of recent logs to return"),
        auth: bool = Depends(verify_token)
    ):
        """Get recent usage logs"""
        db = get_db()
        logs = db.get_recent_usage(limit=limit)
        return {"logs": logs}

    @router.post("/stats/log")
    async def log_usage(request: Request, auth: bool = Depends(verify_token)):
        """Log API usage (internal use)"""
        data = await request.json()
        db = get_db()
        
        # Validate required fields
        if not data.get("provider") or not data.get("model_id"):
            raise HTTPException(status_code=400, detail="provider and model_id are required")
        
        log_id = db.log_usage(data)
        return {"id": log_id, "status": "logged"}

    @router.delete("/stats/clear")
    async def clear_usage_logs(
        before_date: Optional[str] = Query(None, description="Clear logs before this date (ISO format)"),
        auth: bool = Depends(verify_token)
    ):
        """Clear usage logs"""
        db = get_db()
        deleted = db.clear_usage_logs(before_date)
        return {"deleted": deleted}

    @router.get("/stats/cost-estimate")
    async def estimate_cost(
        provider: str = Query(..., description="Provider ID"),
        model_id: str = Query(..., description="Model ID"),
        input_tokens: int = Query(1000, description="Estimated input tokens"),
        output_tokens: int = Query(500, description="Estimated output tokens"),
        auth: bool = Depends(verify_token)
    ):
        """Estimate cost for a given model and token count"""
        from src.models import model_selector
        
        model_info = model_selector.get_model_info(model_id, provider)
        if not model_info:
            raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
        
        model = model_info.get("model", {})
        cost_info = model.get("cost", {})
        
        # Cost is per million tokens
        input_cost = (input_tokens / 1_000_000) * cost_info.get("input", 0)
        output_cost = (output_tokens / 1_000_000) * cost_info.get("output", 0)
        total_cost = input_cost + output_cost
        
        return {
            "provider": provider,
            "model_id": model_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_per_million": {
                "input": cost_info.get("input", 0),
                "output": cost_info.get("output", 0),
                "cache_read": cost_info.get("cache_read", 0),
            },
            "estimated_cost": {
                "input": round(input_cost, 6),
                "output": round(output_cost, 6),
                "total": round(total_cost, 6),
            }
        }

    # ==================== Health Endpoint ====================

    @router.get("/health")
    async def health_check():
        """Health check (no auth required)"""
        db = get_db()
        return {
            "status": "healthy",
            "database": "connected" if db.is_initialized() else "empty",
            "agents": len(db.get_agents()),
            "teams": len(db.get_teams())
        }


def get_crud_router():
    """Get the CRUD router if FastAPI is available"""
    if FASTAPI_AVAILABLE:
        return router
    return None
