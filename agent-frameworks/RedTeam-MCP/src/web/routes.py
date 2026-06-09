"""Web UI routes - pure API frontend using HTMX."""

from fastapi import APIRouter, Request, Response, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import httpx
from typing import Optional
import os

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def get_api_base(request: Request) -> str:
    """Get the API base URL."""
    return str(request.base_url).rstrip("/")


def get_token_from_cookie(request: Request) -> Optional[str]:
    """Extract token from cookie."""
    return request.cookies.get("mcp_token")


async def api_call(
    method: str,
    endpoint: str,
    request: Request,
    json_data: dict = None,
    timeout: float = 30.0,
) -> tuple[dict | list | None, int, str | None]:
    """Make an API call and return (data, status_code, error)."""
    token = get_token_from_cookie(request)
    if not token:
        return None, 401, "Not authenticated"
    
    base_url = get_api_base(request)
    url = f"{base_url}/api/v1{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=json_data, timeout=timeout)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=json_data, timeout=timeout)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, timeout=timeout)
            else:
                return None, 400, f"Unknown method: {method}"
            
            if response.status_code == 401:
                return None, 401, "Invalid or expired token"
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    return None, response.status_code, error_data.get("detail", str(response.status_code))
                except:
                    return None, response.status_code, f"Error: {response.status_code}"
            
            if response.status_code == 204:
                return {}, 204, None
            
            return response.json(), response.status_code, None
    except httpx.TimeoutException:
        return None, 504, "Request timed out"
    except Exception as e:
        return None, 500, str(e)


# ============ Authentication Routes ============

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    """Render login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error}
    )


@router.post("/login")
async def login(request: Request, token: str = Form(...)):
    """Validate token and set cookie."""
    # Verify token by making an API call
    base_url = get_api_base(request)
    url = f"{base_url}/api/v1/token/info"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                redirect = RedirectResponse(url="/ui/", status_code=303)
                redirect.set_cookie(
                    key="mcp_token",
                    value=token,
                    httponly=True,
                    samesite="strict",
                    max_age=60 * 60 * 24 * 30,  # 30 days
                )
                return redirect
            else:
                return RedirectResponse(url="/ui/login?error=Invalid+token", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/ui/login?error={str(e)}", status_code=303)


@router.get("/logout")
async def logout():
    """Clear token cookie and redirect to login."""
    response = RedirectResponse(url="/ui/login", status_code=303)
    response.delete_cookie("mcp_token")
    return response


# ============ Dashboard ============

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    # Fetch stats
    agents_data, _, _ = await api_call("GET", "/agents", request)
    teams_data, _, _ = await api_call("GET", "/teams", request)
    settings_data, _, _ = await api_call("GET", "/settings", request)
    
    # Extract lists from API response format {"agents": [...]} and {"teams": [...]}
    agents = agents_data.get("agents", []) if isinstance(agents_data, dict) else (agents_data or [])
    teams = teams_data.get("teams", []) if isinstance(teams_data, dict) else (teams_data or [])
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "agents_count": len(agents),
            "teams_count": len(teams),
            "settings": settings_data or {},
        }
    )


# ============ Agents CRUD ============

def dict_to_list(data: dict, key: str) -> list:
    """Transform {id: config} dict to list of {id: id, **config}"""
    if not data or key not in data:
        return []
    items = data[key]
    if isinstance(items, dict):
        return [{"id": k, **v} for k, v in items.items()]
    return items if isinstance(items, list) else []


@router.get("/agents", response_class=HTMLResponse)
async def agents_list(request: Request):
    """List all agents."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    data, status, error = await api_call("GET", "/agents", request)
    agents = dict_to_list(data, "agents")
    
    return templates.TemplateResponse(
        "agents/list.html",
        {
            "request": request,
            "agents": agents,
            "error": error,
        }
    )


@router.get("/agents/new", response_class=HTMLResponse)
async def agent_new_form(request: Request):
    """New agent form."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    # Get available providers
    providers_data, _, _ = await api_call("GET", "/models/providers", request)
    providers = providers_data.get("providers", []) if providers_data else []
    
    return templates.TemplateResponse(
        "agents/form.html",
        {
            "request": request,
            "agent": None,
            "providers": providers,
            "models": [],
            "is_new": True,
        }
    )


@router.get("/agents/{agent_id}", response_class=HTMLResponse)
async def agent_detail(request: Request, agent_id: str):
    """Agent detail view."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    agent, status, error = await api_call("GET", f"/agents/{agent_id}", request)
    
    if error:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error}
        )
    
    return templates.TemplateResponse(
        "agents/detail.html",
        {"request": request, "agent": agent}
    )


@router.get("/agents/{agent_id}/edit", response_class=HTMLResponse)
async def agent_edit_form(request: Request, agent_id: str):
    """Edit agent form."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    agent, _, error = await api_call("GET", f"/agents/{agent_id}", request)
    providers_data, _, _ = await api_call("GET", "/models/providers", request)
    providers = providers_data.get("providers", []) if providers_data else []
    
    # Get models for the agent's current provider
    models = []
    if agent and agent.get("provider"):
        models_data, _, _ = await api_call("GET", f"/models?provider={agent['provider']}", request)
        if models_data and "providers" in models_data:
            provider_data = models_data["providers"].get(agent["provider"], {})
            models = provider_data.get("models", [])
    
    if error:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error}
        )
    
    return templates.TemplateResponse(
        "agents/form.html",
        {
            "request": request,
            "agent": agent,
            "providers": providers,
            "models": models,
            "is_new": False,
        }
    )


# HTMX partial endpoints for agents
@router.post("/htmx/agents", response_class=HTMLResponse)
async def htmx_create_agent(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    model_id: str = Form(...),
    provider: str = Form(...),
    role: str = Form(...),
    goal: str = Form(""),
    backstory: str = Form(""),
    enable_memory: bool = Form(False),
    temperature: Optional[float] = Form(None),
    max_tokens: Optional[int] = Form(None),
    top_p: Optional[float] = Form(None),
    reasoning_effort: Optional[str] = Form(None),
    presence_penalty: Optional[float] = Form(None),
    frequency_penalty: Optional[float] = Form(None),
    seed: Optional[int] = Form(None),
):
    """Create agent via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    # Build sampling_params from form fields
    sampling_params = {}
    if temperature is not None:
        sampling_params["temperature"] = temperature
    if max_tokens is not None:
        sampling_params["max_tokens"] = max_tokens
    if top_p is not None:
        sampling_params["top_p"] = top_p
    if reasoning_effort and reasoning_effort.strip():
        sampling_params["reasoning_effort"] = reasoning_effort
    if presence_penalty is not None:
        sampling_params["presence_penalty"] = presence_penalty
    if frequency_penalty is not None:
        sampling_params["frequency_penalty"] = frequency_penalty
    if seed is not None:
        sampling_params["seed"] = seed
    
    agent_data = {
        "id": id,
        "name": name,
        "model_id": model_id,
        "provider": provider,
        "role": role,
        "goal": goal,
        "backstory": backstory,
        "enable_memory": enable_memory,
        "sampling_params": sampling_params,
    }
    
    result, status, error = await api_call("POST", "/agents", request, agent_data)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    # Return redirect header for HTMX
    response = HTMLResponse("")
    response.headers["HX-Redirect"] = "/ui/agents"
    return response


@router.put("/htmx/agents/{agent_id}", response_class=HTMLResponse)
async def htmx_update_agent(
    request: Request,
    agent_id: str,
    name: str = Form(...),
    model_id: str = Form(...),
    provider: str = Form(...),
    role: str = Form(...),
    goal: str = Form(""),
    backstory: str = Form(""),
    enable_memory: bool = Form(False),
    temperature: Optional[float] = Form(None),
    max_tokens: Optional[int] = Form(None),
    top_p: Optional[float] = Form(None),
    reasoning_effort: Optional[str] = Form(None),
    presence_penalty: Optional[float] = Form(None),
    frequency_penalty: Optional[float] = Form(None),
    seed: Optional[int] = Form(None),
):
    """Update agent via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    # Build sampling_params from form fields
    sampling_params = {}
    if temperature is not None:
        sampling_params["temperature"] = temperature
    if max_tokens is not None:
        sampling_params["max_tokens"] = max_tokens
    if top_p is not None:
        sampling_params["top_p"] = top_p
    if reasoning_effort and reasoning_effort.strip():
        sampling_params["reasoning_effort"] = reasoning_effort
    if presence_penalty is not None:
        sampling_params["presence_penalty"] = presence_penalty
    if frequency_penalty is not None:
        sampling_params["frequency_penalty"] = frequency_penalty
    if seed is not None:
        sampling_params["seed"] = seed
    
    agent_data = {
        "name": name,
        "model_id": model_id,
        "provider": provider,
        "role": role,
        "goal": goal,
        "backstory": backstory,
        "enable_memory": enable_memory,
        "sampling_params": sampling_params,
    }
    
    result, status, error = await api_call("PUT", f"/agents/{agent_id}", request, agent_data)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    response = HTMLResponse("")
    response.headers["HX-Redirect"] = f"/ui/agents/{agent_id}"
    return response


@router.delete("/htmx/agents/{agent_id}", response_class=HTMLResponse)
async def htmx_delete_agent(request: Request, agent_id: str):
    """Delete agent via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    result, status, error = await api_call("DELETE", f"/agents/{agent_id}", request)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    response = HTMLResponse("")
    response.headers["HX-Redirect"] = "/ui/agents"
    return response


@router.get("/htmx/models", response_class=HTMLResponse)
async def htmx_get_models(request: Request, provider: str = ""):
    """Get models for a provider via HTMX - returns <option> elements."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<option value=''>Not authenticated</option>", status_code=401)
    
    if not provider:
        return HTMLResponse("<option value=''>Select a provider first...</option>")
    
    models_data, _, error = await api_call("GET", f"/models?provider={provider}", request)
    
    if error:
        return HTMLResponse(f"<option value=''>Error: {error}</option>")
    
    models = []
    if models_data and "providers" in models_data:
        provider_data = models_data["providers"].get(provider, {})
        models_raw = provider_data.get("models", [])
        # Handle both dict and list formats for models
        if isinstance(models_raw, dict):
            models = [{"id": mid, **mdata} if isinstance(mdata, dict) else {"id": mid, "name": mdata} 
                      for mid, mdata in models_raw.items()]
        else:
            models = models_raw
    
    if not models:
        return HTMLResponse("<option value=''>No models available</option>")
    
    # Sort models A-Z by name
    def get_model_name(m):
        return (m.get("name", m.get("id", m)) if isinstance(m, dict) else m).lower()
    models.sort(key=get_model_name)
    
    options = ['<option value="">Select model...</option>']
    for model in models:
        model_id = model.get("id", model) if isinstance(model, dict) else model
        model_name = model.get("name", model_id) if isinstance(model, dict) else model_id
        options.append(f'<option value="{model_id}">{model_name}</option>')
    
    return HTMLResponse("\n".join(options))


@router.get("/htmx/model-constraints", response_class=HTMLResponse)
async def htmx_get_model_constraints(request: Request, model_id: str = "", provider: str = ""):
    """Get model constraints via HTMX - returns constraint info HTML."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("", status_code=401)
    
    if not model_id or not provider:
        return HTMLResponse("")
    
    constraints_data, _, error = await api_call(
        "GET", 
        f"/models/{model_id}/constraints?provider={provider}", 
        request
    )
    
    if error or not constraints_data:
        return HTMLResponse("")
    
    constraints = constraints_data.get("constraints", {})
    
    # Build constraint info text
    info_parts = []
    
    context_length = constraints.get("context_length")
    if context_length:
        info_parts.append(f"Context: {context_length:,} tokens")
    
    max_output = constraints.get("max_output")
    if max_output:
        info_parts.append(f"Max output: {max_output:,} tokens")
    
    if constraints.get("supports_temperature") is False:
        info_parts.append("⚠️ Temperature not supported")
    
    if constraints.get("supports_reasoning"):
        info_parts.append("✓ Reasoning supported")
    
    if not info_parts:
        return HTMLResponse("")
    
    constraint_text = " | ".join(info_parts)
    
    return HTMLResponse(f"""
        <div class="flex items-center">
            <svg class="h-5 w-5 text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
            </svg>
            <span>{constraint_text}</span>
        </div>
    """)


# ============ Teams CRUD ============

@router.get("/teams", response_class=HTMLResponse)
async def teams_list(request: Request):
    """List all teams."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    data, status, error = await api_call("GET", "/teams", request)
    teams = dict_to_list(data, "teams")
    
    return templates.TemplateResponse(
        "teams/list.html",
        {
            "request": request,
            "teams": teams,
            "error": error,
        }
    )


@router.get("/teams/new", response_class=HTMLResponse)
async def team_new_form(request: Request):
    """New team form."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    data, _, _ = await api_call("GET", "/agents", request)
    agents = dict_to_list(data, "agents")
    
    return templates.TemplateResponse(
        "teams/form.html",
        {
            "request": request,
            "team": None,
            "agents": agents,
            "is_new": True,
        }
    )


@router.get("/teams/{team_id}", response_class=HTMLResponse)
async def team_detail(request: Request, team_id: str):
    """Team detail view."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    team, status, error = await api_call("GET", f"/teams/{team_id}", request)
    
    if error:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error}
        )
    
    # Fetch all agents to enrich member data
    data, _, _ = await api_call("GET", "/agents", request)
    agents_list = dict_to_list(data, "agents")
    agents_map = {a["id"]: a for a in agents_list}
    
    # Enrich members with agent details
    enriched_members = []
    if team and team.get("members"):
        for i, member_id in enumerate(team["members"]):
            agent = agents_map.get(member_id, {})
            enriched_members.append({
                "id": member_id,
                "name": agent.get("name") or agent.get("role") or member_id,
                "role": agent.get("role", "Unknown"),
                "position": i + 1,
            })
    
    # Get available agents (not in team) for adding
    available_agents = [a for a in agents_list if a["id"] not in (team.get("members") or [])]
    
    return templates.TemplateResponse(
        "teams/detail.html",
        {
            "request": request,
            "team": {**team, "members": enriched_members} if team else None,
            "available_agents": available_agents,
        }
    )


@router.get("/teams/{team_id}/edit", response_class=HTMLResponse)
async def team_edit_form(request: Request, team_id: str):
    """Edit team form."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    team, _, error = await api_call("GET", f"/teams/{team_id}", request)
    data, _, _ = await api_call("GET", "/agents", request)
    agents = dict_to_list(data, "agents")
    
    if error:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error}
        )
    
    return templates.TemplateResponse(
        "teams/form.html",
        {
            "request": request,
            "team": team,
            "agents": agents,
            "is_new": False,
        }
    )


# HTMX partial endpoints for teams
@router.post("/htmx/teams", response_class=HTMLResponse)
async def htmx_create_team(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    default_mode: str = Form("ensemble"),
):
    """Create team via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    # Get members from form (multi-select sends multiple values)
    form_data = await request.form()
    members = form_data.getlist("members")
    
    team_data = {
        "id": id,
        "name": name,
        "description": description,
        "default_mode": default_mode,
        "members": members,
    }
    
    result, status, error = await api_call("POST", "/teams", request, team_data)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    response = HTMLResponse("")
    response.headers["HX-Redirect"] = "/ui/teams"
    return response


@router.put("/htmx/teams/{team_id}", response_class=HTMLResponse)
async def htmx_update_team(
    request: Request,
    team_id: str,
    name: str = Form(...),
    description: str = Form(""),
    default_mode: str = Form("ensemble"),
):
    """Update team via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    # Get members from form (multi-select sends multiple values)
    form_data = await request.form()
    members = form_data.getlist("members")
    
    team_data = {
        "name": name,
        "description": description,
        "default_mode": default_mode,
        "members": members,
    }
    
    result, status, error = await api_call("PUT", f"/teams/{team_id}", request, team_data)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    response = HTMLResponse("")
    response.headers["HX-Redirect"] = f"/ui/teams/{team_id}"
    return response


@router.delete("/htmx/teams/{team_id}", response_class=HTMLResponse)
async def htmx_delete_team(request: Request, team_id: str):
    """Delete team via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    result, status, error = await api_call("DELETE", f"/teams/{team_id}", request)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    response = HTMLResponse("")
    response.headers["HX-Redirect"] = "/ui/teams"
    return response


@router.post("/htmx/teams/{team_id}/members", response_class=HTMLResponse)
async def htmx_add_team_member(
    request: Request,
    team_id: str,
    agent_id: str = Form(...),
):
    """Add member to team via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    result, status, error = await api_call(
        "POST", f"/teams/{team_id}/members?agent_id={agent_id}", request
    )
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    # Refresh team detail with enriched members
    team, _, _ = await api_call("GET", f"/teams/{team_id}", request)
    data, _, _ = await api_call("GET", "/agents", request)
    agents_list = dict_to_list(data, "agents")
    agents_map = {a["id"]: a for a in agents_list}
    
    enriched_members = []
    if team and team.get("members"):
        for i, member_id in enumerate(team["members"]):
            agent = agents_map.get(member_id, {})
            enriched_members.append({
                "id": member_id,
                "name": agent.get("name") or agent.get("role") or member_id,
                "role": agent.get("role", "Unknown"),
                "position": i + 1,
            })
    
    available_agents = [a for a in agents_list if a["id"] not in (team.get("members") or [])]
    
    return templates.TemplateResponse(
        "teams/_members.html",
        {
            "request": request,
            "team": {**team, "members": enriched_members} if team else None,
            "available_agents": available_agents,
        }
    )


@router.delete("/htmx/teams/{team_id}/members/{agent_id}", response_class=HTMLResponse)
async def htmx_remove_team_member(request: Request, team_id: str, agent_id: str):
    """Remove member from team via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    result, status, error = await api_call(
        "DELETE", f"/teams/{team_id}/members/{agent_id}", request
    )
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    # Refresh team detail with enriched members
    team, _, _ = await api_call("GET", f"/teams/{team_id}", request)
    data, _, _ = await api_call("GET", "/agents", request)
    agents_list = dict_to_list(data, "agents")
    agents_map = {a["id"]: a for a in agents_list}
    
    enriched_members = []
    if team and team.get("members"):
        for i, member_id in enumerate(team["members"]):
            agent = agents_map.get(member_id, {})
            enriched_members.append({
                "id": member_id,
                "name": agent.get("name") or agent.get("role") or member_id,
                "role": agent.get("role", "Unknown"),
                "position": i + 1,
            })
    
    available_agents = [a for a in agents_list if a["id"] not in (team.get("members") or [])]
    
    return templates.TemplateResponse(
        "teams/_members.html",
        {
            "request": request,
            "team": {**team, "members": enriched_members} if team else None,
            "available_agents": available_agents,
        }
    )


# ============ Custom Providers ============

@router.get("/custom-providers", response_class=HTMLResponse)
async def custom_providers_list(request: Request):
    """List all custom providers."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    data, status, error = await api_call("GET", "/custom-providers", request)
    providers = data.get("providers", []) if data else []
    
    return templates.TemplateResponse(
        "custom_providers/list.html",
        {
            "request": request,
            "providers": providers,
            "error": error,
        }
    )


@router.get("/custom-providers/{provider_id}", response_class=HTMLResponse)
async def custom_provider_detail(request: Request, provider_id: str):
    """Custom provider detail page with models."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    provider, status, error = await api_call("GET", f"/custom-providers/{provider_id}", request)
    if not provider:
        return RedirectResponse(url="/ui/custom-providers", status_code=303)
    
    models_data, _, _ = await api_call("GET", f"/custom-providers/{provider_id}/models", request)
    models = models_data.get("models", []) if models_data else []
    
    return templates.TemplateResponse(
        "custom_providers/detail.html",
        {
            "request": request,
            "provider": provider,
            "models": models,
            "error": error,
        }
    )


@router.get("/custom-providers/{provider_id}/edit", response_class=HTMLResponse)
async def custom_provider_edit(request: Request, provider_id: str):
    """Edit custom provider page."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    provider, status, error = await api_call("GET", f"/custom-providers/{provider_id}", request)
    if not provider:
        return RedirectResponse(url="/ui/custom-providers", status_code=303)
    
    return templates.TemplateResponse(
        "custom_providers/edit.html",
        {
            "request": request,
            "provider": provider,
            "error": error,
        }
    )


# ============ Custom Providers HTMX ============

@router.post("/htmx/custom-providers", response_class=HTMLResponse)
async def htmx_create_custom_provider(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    base_url: str = Form(...),
    api_key: Optional[str] = Form(None),
    provider_type: str = Form("openai-compatible"),
):
    """HTMX: Create a custom provider."""
    data = {
        "id": id,
        "name": name,
        "base_url": base_url,
        "api_key": api_key or "",
        "provider_type": provider_type,
        "is_enabled": True,
    }
    
    result, status, error = await api_call("POST", "/custom-providers", request, json_data=data)
    
    if error:
        return HTMLResponse(
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>'
        )
    
    # Reload the provider list
    providers_data, _, _ = await api_call("GET", "/custom-providers", request)
    providers = providers_data.get("providers", []) if providers_data else []
    
    return templates.TemplateResponse(
        "custom_providers/_provider_list.html",
        {"request": request, "providers": providers}
    )


@router.put("/htmx/custom-providers/{provider_id}", response_class=HTMLResponse)
async def htmx_update_custom_provider(
    request: Request,
    provider_id: str,
    name: str = Form(...),
    base_url: str = Form(...),
    api_key: Optional[str] = Form(None),
    provider_type: str = Form("openai-compatible"),
    is_enabled: Optional[str] = Form(None),
):
    """HTMX: Update a custom provider."""
    data = {
        "name": name,
        "base_url": base_url,
        "api_key": api_key or "",
        "provider_type": provider_type,
        "is_enabled": is_enabled == "true",
    }
    
    result, status, error = await api_call("PUT", f"/custom-providers/{provider_id}", request, json_data=data)
    
    if error:
        return HTMLResponse(
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>'
        )
    
    return HTMLResponse(
        '<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">Provider updated successfully!</div>'
    )


@router.delete("/htmx/custom-providers/{provider_id}", response_class=HTMLResponse)
async def htmx_delete_custom_provider(request: Request, provider_id: str):
    """HTMX: Delete a custom provider."""
    result, status, error = await api_call("DELETE", f"/custom-providers/{provider_id}", request)
    
    if error:
        return HTMLResponse(
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>'
        )
    
    # Return empty to remove from list
    return HTMLResponse("")


@router.post("/htmx/custom-providers/{provider_id}/test", response_class=HTMLResponse)
async def htmx_test_custom_provider(request: Request, provider_id: str):
    """HTMX: Test connection to a custom provider."""
    result, status, error = await api_call("POST", f"/custom-providers/{provider_id}/test", request)
    
    if error:
        return HTMLResponse(
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mt-2">{error}</div>'
        )
    
    if result.get("status") == "connected":
        models_found = result.get("models_found", 0)
        models_list = result.get("models", [])
        models_preview = ", ".join(models_list[:5]) + ("..." if len(models_list) > 5 else "")
        return HTMLResponse(
            f'<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mt-2">'
            f'✅ Connected! Found {models_found} models: {models_preview}</div>'
        )
    else:
        msg = result.get("message", "Unknown error")
        return HTMLResponse(
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mt-2">'
            f'❌ Connection failed: {msg}</div>'
        )


@router.post("/htmx/custom-providers/{provider_id}/models", response_class=HTMLResponse)
async def htmx_create_custom_model(
    request: Request,
    provider_id: str,
    model_name: str = Form(...),
    display_name: Optional[str] = Form(None),
    context_length: int = Form(4096),
    max_output: int = Form(4096),
    supports_vision: Optional[str] = Form(None),
    supports_tools: Optional[str] = Form(None),
    supports_streaming: Optional[str] = Form(None),
):
    """HTMX: Create a custom model."""
    data = {
        "model_name": model_name,
        "display_name": display_name or model_name,
        "context_length": context_length,
        "max_output": max_output,
        "supports_vision": supports_vision == "true",
        "supports_tools": supports_tools == "true",
        "supports_streaming": supports_streaming == "true" if supports_streaming else True,
    }
    
    result, status, error = await api_call(
        "POST", f"/custom-providers/{provider_id}/models", request, json_data=data
    )
    
    if error:
        return HTMLResponse(
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>'
        )
    
    # Reload the models list
    models_data, _, _ = await api_call("GET", f"/custom-providers/{provider_id}/models", request)
    models = models_data.get("models", []) if models_data else []
    
    return templates.TemplateResponse(
        "custom_providers/_model_list.html",
        {"request": request, "models": models, "provider": {"id": provider_id}}
    )


@router.put("/htmx/custom-models/{model_id}", response_class=HTMLResponse)
async def htmx_update_custom_model(
    request: Request,
    model_id: str,
    model_name: str = Form(...),
    display_name: Optional[str] = Form(None),
    context_length: int = Form(4096),
    max_output: int = Form(4096),
    supports_vision: Optional[str] = Form(None),
    supports_tools: Optional[str] = Form(None),
    supports_streaming: Optional[str] = Form(None),
):
    """HTMX: Update a custom model."""
    data = {
        "model_name": model_name,
        "display_name": display_name or model_name,
        "context_length": context_length,
        "max_output": max_output,
        "supports_vision": supports_vision == "true",
        "supports_tools": supports_tools == "true",
        "supports_streaming": supports_streaming == "true" if supports_streaming else True,
    }
    
    result, status, error = await api_call("PUT", f"/custom-models/{model_id}", request, json_data=data)
    
    if error:
        return HTMLResponse(
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>'
        )
    
    # Get the provider ID from the model
    model = result or {}
    provider_id = model.get("provider_id", "")
    
    # Reload the models list
    models_data, _, _ = await api_call("GET", f"/custom-providers/{provider_id}/models", request)
    models = models_data.get("models", []) if models_data else []
    
    return templates.TemplateResponse(
        "custom_providers/_model_list.html",
        {"request": request, "models": models, "provider": {"id": provider_id}}
    )


@router.delete("/htmx/custom-models/{model_id}", response_class=HTMLResponse)
async def htmx_delete_custom_model(request: Request, model_id: str):
    """HTMX: Delete a custom model."""
    result, status, error = await api_call("DELETE", f"/custom-models/{model_id}", request)
    
    if error:
        return HTMLResponse(
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>'
        )
    
    # Return empty to remove from list
    return HTMLResponse("")


@router.post("/htmx/custom-providers/{provider_id}/detect-models", response_class=HTMLResponse)
async def htmx_detect_models(request: Request, provider_id: str):
    """HTMX: Auto-detect models from provider."""
    # Test the provider to get models
    result, status, error = await api_call("POST", f"/custom-providers/{provider_id}/test", request)
    
    if error or result.get("status") != "connected":
        msg = error or result.get("message", "Could not connect to provider")
        return HTMLResponse(
            f'<div class="text-center py-6">'
            f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded inline-block">'
            f'❌ {msg}</div></div>'
        )
    
    # Create models from detected list
    detected_models = result.get("models", [])
    created_count = 0
    
    for model_name in detected_models:
        data = {
            "model_name": model_name,
            "display_name": model_name,
            "context_length": 4096,
            "max_output": 4096,
            "supports_streaming": True,
        }
        create_result, _, _ = await api_call(
            "POST", f"/custom-providers/{provider_id}/models", request, json_data=data
        )
        if create_result:
            created_count += 1
    
    # Reload the models list
    models_data, _, _ = await api_call("GET", f"/custom-providers/{provider_id}/models", request)
    models = models_data.get("models", []) if models_data else []
    
    return templates.TemplateResponse(
        "custom_providers/_model_list.html",
        {"request": request, "models": models, "provider": {"id": provider_id}, "detected_count": created_count}
    )


# ============ Settings ============

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    settings, status, error = await api_call("GET", "/settings", request)
    providers_data, _, _ = await api_call("GET", "/models/providers", request)
    providers = providers_data.get("providers", []) if providers_data else []
    
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": settings or {},
            "providers": providers,
            "error": error,
        }
    )


@router.post("/htmx/settings", response_class=HTMLResponse)
async def htmx_update_settings(request: Request):
    """Update settings via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    form_data = await request.form()
    settings = dict(form_data)
    
    # API expects {"settings": {...}}
    result, status, error = await api_call("PUT", "/settings", request, {"settings": settings})
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    return HTMLResponse("<p class='text-green-500'>Settings saved!</p>")


@router.post("/htmx/token/regenerate", response_class=HTMLResponse)
async def htmx_regenerate_token(request: Request):
    """Regenerate auth token via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    result, status, error = await api_call("POST", "/token/regenerate", request)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    new_token = result.get("token")
    
    # Update cookie with new token
    response = HTMLResponse(f"""
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            <p class="font-bold">New Token Generated</p>
            <p class="mt-2 font-mono text-sm break-all">{new_token}</p>
            <p class="mt-2 text-sm">Save this token! You'll be logged out after this page refresh.</p>
        </div>
    """)
    response.set_cookie(
        key="mcp_token",
        value=new_token,
        httponly=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 30,
    )
    return response


# ============ Export/Import ============

@router.get("/export", response_class=HTMLResponse)
async def export_page(request: Request):
    """Export configuration page."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    return templates.TemplateResponse(
        "export.html",
        {"request": request}
    )


@router.get("/htmx/export/download")
async def htmx_download_export(request: Request):
    """Download export as JSON."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    data, status, error = await api_call("GET", "/export", request)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    import json
    json_content = json.dumps(data, indent=2)
    
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=agent_config_export.json"}
    )


@router.post("/htmx/import", response_class=HTMLResponse)
async def htmx_import_config(request: Request):
    """Import configuration via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    form_data = await request.form()
    file = form_data.get("file")
    
    if not file:
        return HTMLResponse("<p class='text-red-500'>No file provided</p>", status_code=400)
    
    import json
    try:
        content = await file.read()
        data = json.loads(content)
    except json.JSONDecodeError:
        return HTMLResponse("<p class='text-red-500'>Invalid JSON file</p>", status_code=400)
    
    result, status, error = await api_call("POST", "/import", request, data)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=status)
    
    return HTMLResponse("""
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            <p>Configuration imported successfully!</p>
        </div>
    """)


# ============ Statistics ============

@router.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request):
    """Statistics and usage dashboard."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    # Get usage statistics for different time periods
    stats_7d, _, _ = await api_call("GET", "/stats?days=7", request)
    stats_30d, _, _ = await api_call("GET", "/stats?days=30", request)
    recent_history, _, _ = await api_call("GET", "/stats/recent?limit=50", request)
    
    # Extract totals for easier template access
    totals_7d = stats_7d.get("totals", {}) if stats_7d else {}
    totals_30d = stats_30d.get("totals", {}) if stats_30d else {}
    
    # Map to expected template format
    stats_7d_flat = {
        "total_requests": totals_7d.get("requests", 0),
        "successful_requests": totals_7d.get("successful_requests", 0),
        "failed_requests": totals_7d.get("failed_requests", 0),
        "total_tokens": totals_7d.get("input_tokens", 0) + totals_7d.get("output_tokens", 0),
        "total_cost": totals_7d.get("total_cost", 0),
        "avg_response_time": totals_7d.get("avg_response_time_ms", 0),
    }
    
    stats_30d_flat = {
        "total_requests": totals_30d.get("requests", 0),
        "successful_requests": totals_30d.get("successful_requests", 0),
        "failed_requests": totals_30d.get("failed_requests", 0),
        "total_tokens": totals_30d.get("input_tokens", 0) + totals_30d.get("output_tokens", 0),
        "total_cost": totals_30d.get("total_cost", 0),
        "avg_response_time": totals_30d.get("avg_response_time_ms", 0),
    }
    
    # Cost summary from 30 day stats
    cost_summary = {
        "total_input_tokens": totals_30d.get("input_tokens", 0),
        "total_output_tokens": totals_30d.get("output_tokens", 0),
        "total_input_cost": 0,  # Not separately tracked, included in total
        "total_output_cost": 0,
        "total_cost": totals_30d.get("total_cost", 0),
    }
    
    # Get model breakdown from stats - map to template format
    model_breakdown = []
    for model in (stats_30d.get("by_model", []) if stats_30d else []):
        model_breakdown.append({
            "provider": model.get("provider", "Unknown"),
            "model_id": model.get("model_id", "Unknown"),
            "total_requests": model.get("requests", 0),
            "total_input_tokens": model.get("input_tokens", 0),
            "total_output_tokens": model.get("output_tokens", 0),
            "total_cost": model.get("cost", 0),
            "avg_response_time": 0,  # Not available per-model
        })
    
    return templates.TemplateResponse(
        "statistics.html",
        {
            "request": request,
            "stats_7d": stats_7d_flat,
            "stats_30d": stats_30d_flat,
            "cost_summary": cost_summary,
            "model_breakdown": model_breakdown,
            "recent_history": recent_history.get("logs", []) if recent_history else [],
        }
    )


@router.get("/htmx/statistics/refresh", response_class=HTMLResponse)
async def htmx_refresh_statistics(request: Request, days: int = 7):
    """Refresh statistics via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    stats, _, error = await api_call("GET", f"/stats?days={days}", request)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=500)
    
    # Extract and flatten totals
    totals = stats.get("totals", {}) if stats else {}
    stats_flat = {
        "total_requests": totals.get("requests", 0),
        "successful_requests": totals.get("successful_requests", 0),
        "failed_requests": totals.get("failed_requests", 0),
        "total_tokens": totals.get("input_tokens", 0) + totals.get("output_tokens", 0),
        "total_cost": totals.get("total_cost", 0),
        "avg_response_time": totals.get("avg_response_time_ms", 0),
    }
    
    return templates.TemplateResponse(
        "statistics/_stats_cards.html",
        {"request": request, "stats": stats_flat, "days": days}
    )


@router.get("/htmx/statistics/history", response_class=HTMLResponse)
async def htmx_statistics_history(request: Request, days: int = 7, limit: int = 50):
    """Get usage history via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    history, _, error = await api_call("GET", f"/stats/recent?limit={limit}", request)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=500)
    
    return templates.TemplateResponse(
        "statistics/_history_table.html",
        {"request": request, "history": history.get("logs", []) if history else []}
    )


@router.get("/htmx/statistics/models", response_class=HTMLResponse)
async def htmx_statistics_models(request: Request, days: int = 30):
    """Get model breakdown via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<p class='text-red-500'>Not authenticated</p>", status_code=401)
    
    stats, _, error = await api_call("GET", f"/stats?days={days}", request)
    
    if error:
        return HTMLResponse(f"<p class='text-red-500'>{error}</p>", status_code=500)
    
    # Map model breakdown to expected template format
    model_breakdown = []
    for model in (stats.get("by_model", []) if stats else []):
        model_breakdown.append({
            "provider": model.get("provider", "Unknown"),
            "model_id": model.get("model_id", "Unknown"),
            "total_requests": model.get("requests", 0),
            "total_input_tokens": model.get("input_tokens", 0),
            "total_output_tokens": model.get("output_tokens", 0),
            "total_cost": model.get("cost", 0),
            "avg_response_time": 0,
        })
    
    return templates.TemplateResponse(
        "statistics/_model_breakdown.html",
        {"request": request, "models": model_breakdown}
    )


# ============ Chat ============

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat with agents page."""
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    # Get agents, teams, and providers for selection
    agents_data, _, _ = await api_call("GET", "/agents", request)
    teams_data, _, _ = await api_call("GET", "/teams", request)
    providers_data, _, _ = await api_call("GET", "/models/providers", request)
    
    agents = agents_data.get("agents", []) if agents_data else []
    teams = teams_data.get("teams", []) if teams_data else []
    providers = providers_data.get("providers", []) if providers_data else []
    
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "agents": agents,
            "teams": teams,
            "providers": providers,
        }
    )


@router.get("/htmx/chat/models", response_class=HTMLResponse)
async def htmx_get_models(request: Request, provider: str = ""):
    """Get models for a provider via HTMX."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("<option value=''>Not authenticated</option>", status_code=401)
    
    if not provider:
        return HTMLResponse("<option value=''>Select a provider first</option>")
    
    models_data, _, error = await api_call("GET", f"/models?provider={provider}", request)
    
    if error:
        return HTMLResponse(f"<option value=''>Error: {error}</option>")
    
    models = models_data.get("models", []) if models_data else []
    
    options = ["<option value=''>Select a model...</option>"]
    for model in models[:50]:  # Limit to first 50 models
        model_id = model.get("id", model.get("model_id", ""))
        model_name = model.get("name", model_id)
        options.append(f"<option value='{model_id}'>{model_name}</option>")
    
    return HTMLResponse("\n".join(options))


@router.get("/htmx/chat/agent-config", response_class=HTMLResponse)
async def htmx_get_agent_config(request: Request, agent_id: str = ""):
    """Get agent configuration for pre-filling form."""
    token = get_token_from_cookie(request)
    if not token:
        return HTMLResponse("", status_code=401)
    
    if not agent_id:
        # Clear config and reset form
        return HTMLResponse("""
        <script>
            // Reset to defaults
            document.getElementById('temperature').value = 0.7;
            document.getElementById('temp-value').textContent = '0.7';
            document.getElementById('max_tokens').value = 1024;
            document.getElementById('top_p').value = 1.0;
            document.getElementById('topp-value').textContent = '1.0';
        </script>
        """)
    
    agent_data, _, error = await api_call("GET", f"/agents/{agent_id}", request)
    
    if error or not agent_data:
        return HTMLResponse("")
    
    # Extract agent configuration
    provider = agent_data.get("provider", "")
    model_id = agent_data.get("model_id", "")
    sampling_params = agent_data.get("sampling_params", {})
    
    # Get sampling values with defaults
    temperature = sampling_params.get("temperature", 0.7)
    max_tokens = sampling_params.get("max_tokens", 1024)
    top_p = sampling_params.get("top_p", 1.0)
    
    import json
    html = f"""
    <div class="mt-2 p-2 bg-blue-50 rounded-lg text-xs text-blue-700">
        <p class="font-medium">Agent: {agent_data.get('name', agent_id)}</p>
        <p>Provider: {provider} | Model: {model_id}</p>
    </div>
    <script>
        (function() {{
            // Auto-select provider and trigger model load
            const providerSelect = document.getElementById('provider');
            const modelSelect = document.getElementById('model');
            
            if (providerSelect && '{provider}') {{
                providerSelect.value = '{provider}';
                // Trigger model load via HTMX
                htmx.trigger(providerSelect, 'change');
                // Set model after models load
                setTimeout(() => {{
                    if (modelSelect) {{
                        modelSelect.value = '{model_id}';
                    }}
                }}, 800);
            }}
            
            // Apply sampling parameters
            const tempSlider = document.getElementById('temperature');
            const tempValue = document.getElementById('temp-value');
            const maxTokensInput = document.getElementById('max_tokens');
            const topPSlider = document.getElementById('top_p');
            const topPValue = document.getElementById('topp-value');
            
            if (tempSlider) {{
                tempSlider.value = {temperature};
                if (tempValue) tempValue.textContent = '{temperature}';
            }}
            if (maxTokensInput) {{
                maxTokensInput.value = {max_tokens};
            }}
            if (topPSlider) {{
                topPSlider.value = {top_p};
                if (topPValue) topPValue.textContent = '{top_p}';
            }}
        }})();
    </script>
    """
    return HTMLResponse(html)

