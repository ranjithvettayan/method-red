"""
WebSocket handlers for real-time communication
"""

import logging
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


def register_websockets(app, config):
    """Register WebSocket endpoints with the FastAPI app"""
    from fastapi import WebSocket, WebSocketDisconnect
    
    from src.api.cache import get_or_create_agent
    from src.agents import MultiAgentCoordinator, CoordinationMode

    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket endpoint for single agent chat with real-time streaming"""
        await websocket.accept()
        try:
            while True:
                # Receive chat request
                data = await websocket.receive_json()
                
                try:
                    # Parse request data
                    query = data.get("query", "")
                    agent_id = data.get("agent_id")
                    model_id = data.get("model_id", config.get('models.default', 'gpt-3.5-turbo'))
                    provider = data.get("provider", "openai")
                    agent_role = data.get("agent_role", "Assistant")
                    agent_goal = data.get("agent_goal", "Help users with their requests using advanced AI capabilities")
                    agent_backstory = data.get("agent_backstory", "A versatile AI assistant capable of handling various tasks with access to multiple AI models")
                    session_id = data.get("session_id")
                    enable_memory = data.get("enable_memory", True)
                    stream = data.get("stream", True)  # Default to streaming for WebSocket
                    
                    # Sampling parameters
                    sampling_params = {
                        "temperature": data.get("temperature"),
                        "top_p": data.get("top_p"),
                        "top_k": data.get("top_k"),
                        "max_tokens": data.get("max_tokens"),
                        "presence_penalty": data.get("presence_penalty"),
                        "frequency_penalty": data.get("frequency_penalty"),
                        "stop": data.get("stop"),
                        "seed": data.get("seed"),
                        "logprobs": data.get("logprobs"),
                        "reasoning_effort": data.get("reasoning_effort"),
                    }
                    
                    # Handle predefined agent
                    if agent_id:
                        predefined_agents = config.get_predefined_agents()
                        if agent_id in predefined_agents:
                            agent_config = predefined_agents[agent_id]
                            model_id = agent_config.get("model_id", model_id)
                            provider = agent_config.get("provider", provider)
                            agent_role = agent_config.get("role", agent_role)
                            agent_goal = agent_config.get("goal", agent_goal)
                            agent_backstory = agent_config.get("backstory", agent_backstory)
                            enable_memory = agent_config.get("enable_memory", enable_memory)
                    
                    # Get or create agent
                    agent = get_or_create_agent(
                        model_id=model_id,
                        provider=provider,
                        role=agent_role,
                        goal=agent_goal,
                        backstory=agent_backstory,
                        session_id=session_id,
                        enable_memory=enable_memory,
                        sampling_params=sampling_params,
                    )
                    
                    # Process request
                    response = agent.process_request(query, stream=stream)
                    
                    if stream:
                        # Stream response chunks
                        for chunk in response:
                            await websocket.send_json({
                                "type": "chunk",
                                "content": chunk
                            })
                        # Send completion signal
                        await websocket.send_json({
                            "type": "done"
                        })
                    else:
                        # Send complete response
                        await websocket.send_json({
                            "type": "response",
                            "content": response
                        })
                        
                except Exception as e:
                    logger.error(f"WebSocket chat error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                    
        except WebSocketDisconnect:
            logger.info("WebSocket chat connection closed")
        except Exception as e:
            logger.error(f"WebSocket chat connection error: {e}")

    @app.websocket("/ws/multi-agent")
    async def websocket_multi_agent(websocket: WebSocket):
        """WebSocket endpoint for multi-agent coordination with real-time streaming"""
        await websocket.accept()
        try:
            while True:
                # Receive multi-agent request
                data = await websocket.receive_json()
                
                try:
                    # Parse request data
                    query = data.get("query", "")
                    coordination_mode = data.get("coordination_mode", "ensemble")
                    agents = data.get("agents", [])
                    rebuttal_limit = data.get("rebuttal_limit", 3)
                    stream = data.get("stream", True)  # Default to streaming for WebSocket
                    
                    # Validate coordination mode
                    mode_map = {
                        "pipeline": CoordinationMode.PIPELINE,
                        "ensemble": CoordinationMode.ENSEMBLE,
                        "debate": CoordinationMode.DEBATE,
                        "swarm": CoordinationMode.SWARM,
                        "hierarchical": CoordinationMode.HIERARCHICAL
                    }
                    
                    if coordination_mode not in mode_map:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unknown coordination mode: {coordination_mode}"
                        })
                        continue
                        
                    coord_mode = mode_map[coordination_mode]
                    
                    # Get predefined agents
                    predefined_agents = config.get_predefined_agents()
                    
                    # Create agents from request
                    agent_instances = []
                    for agent_config in agents:
                        if isinstance(agent_config, str):
                            # Agent ID - look up from predefined agents
                            if agent_config not in predefined_agents:
                                await websocket.send_json({
                                    "type": "error",
                                    "message": f"Predefined agent '{agent_config}' not found"
                                })
                                continue
                            agent_data = predefined_agents[agent_config]
                        elif isinstance(agent_config, dict):
                            # Full agent configuration
                            agent_data = agent_config
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": "Agent configuration must be either a string (agent ID) or dict"
                            })
                            continue
                            
                        agent = get_or_create_agent(
                            model_id=agent_data.get("model_id", config.get("models.default")),
                            provider=agent_data.get("provider", "openai"),
                            role=agent_data.get("role", "Assistant"),
                            goal=agent_data.get("goal", "Help with tasks"),
                            backstory=agent_data.get("backstory", "An AI assistant"),
                            session_id=agent_data.get("session_id"),
                            enable_memory=agent_data.get("enable_memory", True),
                            sampling_params=agent_data.get("sampling_params", {}),
                        )
                        agent_instances.append(agent)
                    
                    if len(agent_instances) < 2:
                        await websocket.send_json({
                            "type": "error",
                            "message": "At least 2 agents are required for multi-agent coordination"
                        })
                        continue
                    
                    # Create coordinator
                    coordinator = MultiAgentCoordinator(agent_instances)
                    
                    # Coordinate
                    response = coordinator.coordinate(
                        coord_mode,
                        query,
                        stream=stream,
                        rebuttal_limit=rebuttal_limit,
                    )
                    
                    if stream:
                        # Stream response chunks
                        for chunk in response:
                            await websocket.send_json({
                                "type": "chunk",
                                "content": chunk
                            })
                        # Send completion signal
                        await websocket.send_json({
                            "type": "done"
                        })
                    else:
                        # Send complete response
                        await websocket.send_json({
                            "type": "response",
                            "content": response
                        })
                        
                except Exception as e:
                    logger.error(f"WebSocket multi-agent error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                    
        except WebSocketDisconnect:
            logger.info("WebSocket multi-agent connection closed")
        except Exception as e:
            logger.error(f"WebSocket multi-agent connection error: {e}")

    @app.websocket("/ws/team")
    async def websocket_team(websocket: WebSocket):
        """WebSocket endpoint for team coordination with real-time streaming"""
        await websocket.accept()
        try:
            while True:
                # Receive team request
                data = await websocket.receive_json()
                
                try:
                    # Parse request data
                    query = data.get("query", "")
                    team_id = data.get("team_id", "")
                    coordination_mode = data.get("coordination_mode")  # Optional override
                    rebuttal_limit = data.get("rebuttal_limit", 3)
                    stream = data.get("stream", True)  # Default to streaming for WebSocket
                    
                    if not team_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "team_id is required"
                        })
                        continue
                    
                    # Get team configuration
                    team = config.get_team(team_id)
                    if not team:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Team '{team_id}' not found"
                        })
                        continue
                    
                    agent_ids = team.get("agents", [])
                    if not agent_ids:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Team '{team_id}' has no agents configured"
                        })
                        continue
                    
                    # Use team's default mode if not specified
                    mode_str = coordination_mode or team.get("default_mode", "ensemble")
                    
                    # Validate coordination mode
                    mode_map = {
                        "pipeline": CoordinationMode.PIPELINE,
                        "ensemble": CoordinationMode.ENSEMBLE,
                        "debate": CoordinationMode.DEBATE,
                        "swarm": CoordinationMode.SWARM,
                        "hierarchical": CoordinationMode.HIERARCHICAL
                    }
                    
                    if mode_str not in mode_map:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Invalid coordination mode: {mode_str}"
                        })
                        continue
                    
                    coord_mode = mode_map[mode_str]
                    
                    # Get predefined agents and create them
                    predefined_agents = config.get_predefined_agents()
                    agent_instances = []
                    
                    for agent_id in agent_ids:
                        if agent_id not in predefined_agents:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Agent '{agent_id}' from team not found"
                            })
                            continue
                        
                        agent_data = predefined_agents[agent_id]
                        agent = get_or_create_agent(
                            model_id=agent_data.get("model_id", config.get("models.default")),
                            provider=agent_data.get("provider", "openai"),
                            role=agent_data.get("role", "Assistant"),
                            goal=agent_data.get("goal", "Help with tasks"),
                            backstory=agent_data.get("backstory", "An AI assistant"),
                            session_id=agent_data.get("session_id"),
                            enable_memory=agent_data.get("enable_memory", True),
                            sampling_params=agent_data.get("sampling_params", {}),
                        )
                        agent_instances.append(agent)
                    
                    if len(agent_instances) < 2:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Team must have at least 2 agents"
                        })
                        continue
                    
                    # Send team info
                    await websocket.send_json({
                        "type": "info",
                        "team": team.get("name", team_id),
                        "mode": mode_str,
                        "agents": len(agent_instances)
                    })
                    
                    # Create coordinator
                    coordinator = MultiAgentCoordinator(agent_instances)
                    
                    # Coordinate
                    response = coordinator.coordinate(
                        coord_mode,
                        query,
                        stream=stream,
                        rebuttal_limit=rebuttal_limit,
                    )
                    
                    if stream:
                        # Stream response chunks
                        for chunk in response:
                            await websocket.send_json({
                                "type": "chunk",
                                "content": chunk
                            })
                        # Send completion signal
                        await websocket.send_json({
                            "type": "done"
                        })
                    else:
                        # Send complete response
                        await websocket.send_json({
                            "type": "response",
                            "content": response
                        })
                        
                except Exception as e:
                    logger.error(f"WebSocket team error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                    
        except WebSocketDisconnect:
            logger.info("WebSocket team connection closed")
        except Exception as e:
            logger.error(f"WebSocket team connection error: {e}")

    @app.websocket("/ws/health")
    async def websocket_health(websocket: WebSocket):
        """WebSocket health check endpoint"""
        await websocket.accept()
        try:
            while True:
                # Wait for health check request
                await websocket.receive_text()
                
                # Send health status
                await websocket.send_json({
                    "status": "healthy",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "version": "1.0.0",
                    "connection": "websocket"
                })
                
        except WebSocketDisconnect:
            logger.info("WebSocket health connection closed")
        except Exception as e:
            logger.error(f"WebSocket health connection error: {e}")
