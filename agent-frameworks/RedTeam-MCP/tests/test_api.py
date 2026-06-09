#!/usr/bin/env python3
"""
Unit tests for API endpoints
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import after adding to path
from src.api import ChatRequest, create_app


class TestChatRequest:
    """Test cases for ChatRequest model"""

    def test_chat_request_valid(self):
        """Test valid ChatRequest creation"""
        request = ChatRequest(
            query="Hello world",
            model_id="claude-3-haiku-20240307",
            provider="anthropic",
            agent_role="Assistant",
            agent_goal="Help users",
            agent_backstory="AI assistant",
            session_id="session123",
            stream=False,
            enable_memory=True,
            user_id="user123",
            temperature=0.7,
            max_tokens=1000
        )

        assert request.query == "Hello world"
        assert request.model_id == "claude-3-haiku-20240307"
        assert request.temperature == 0.7
        assert request.max_tokens == 1000

    def test_chat_request_defaults(self):
        """Test ChatRequest with minimal parameters"""
        request = ChatRequest(query="Hello", model_id="gpt-4", provider="openai")

        assert request.query == "Hello"
        assert request.model_id == "gpt-4"
        assert request.provider == "openai"
        assert request.agent_role == "Assistant"
        assert request.stream is False
        assert request.enable_memory is True
        assert request.user_id == "anonymous"

    def test_chat_request_validation_query_required(self):
        """Test that query is required"""
        with pytest.raises(ValueError):
            ChatRequest(model_id="gpt-4", provider="openai")

    def test_chat_request_validation_query_length(self):
        """Test query length validation"""
        # Too short
        with pytest.raises(ValueError):
            ChatRequest(query="", model_id="gpt-4", provider="openai")

        # Too long
        with pytest.raises(ValueError):
            ChatRequest(query="x" * 10001, model_id="gpt-4", provider="openai")

    def test_chat_request_validation_temperature_range(self):
        """Test temperature range validation"""
        # Valid
        ChatRequest(query="Hello", model_id="gpt-4", provider="openai", temperature=1.0)

        # Too low
        with pytest.raises(ValueError):
            ChatRequest(query="Hello", model_id="gpt-4", provider="openai", temperature=-0.1)

        # Too high
        with pytest.raises(ValueError):
            ChatRequest(query="Hello", model_id="gpt-4", provider="openai", temperature=2.1)

    def test_chat_request_validation_user_id(self):
        """Test user_id validation"""
        # Empty becomes anonymous
        request = ChatRequest(query="Hello", model_id="gpt-4", provider="openai", user_id="")
        assert request.user_id == "anonymous"

        # Whitespace becomes anonymous
        request = ChatRequest(query="Hello", model_id="gpt-4", provider="openai", user_id="   ")
        assert request.user_id == "anonymous"

        # Valid user_id
        request = ChatRequest(query="Hello", model_id="gpt-4", provider="openai", user_id="user123")
        assert request.user_id == "user123"


class TestAPIApp:
    """Test cases for FastAPI application"""

    @patch('src.api.app.FASTAPI_AVAILABLE', True)
    @patch('src.agents.ConfigurableAgent')
    @patch('src.models.model_selector')
    @patch('src.config.config')
    def test_create_app(self, mock_config, mock_selector, mock_agent_class):
        """Test app creation"""
        mock_config.get.side_effect = lambda key, default=None: {
            'api.rate_limit': '100/minute',
            'api.max_request_size': 1024*1024,
            'models.default': 'claude-3-haiku-20240307'
        }.get(key, default)

        app = create_app()
        assert app is not None
        assert app.title == "Red Team MCP API"

    @patch('src.api.app.FASTAPI_AVAILABLE', True)
    @patch('src.api.app.FASTAPI_AVAILABLE', True)
    @patch('src.models.model_selector')
    @patch('src.config.config')
    def test_chat_endpoint(self, mock_config, mock_selector):
        """Test chat endpoint"""
        from fastapi.testclient import TestClient

        # Setup mocks
        mock_config.get.side_effect = lambda key, default=None: {
            'api.rate_limit': '100/minute',
            'api.max_request_size': 1024*1024,
            'models.default': 'claude-3-haiku-20240307'
        }.get(key, default)

        app = create_app()
        client = TestClient(app)

        # Test POST /chat
        response = client.post("/chat", json={
            "query": "Hello world",
            "model_id": "claude-3-haiku-20240307",
            "provider": "anthropic"
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)

    @patch('src.api.app.FASTAPI_AVAILABLE', True)
    @patch('src.agents.ConfigurableAgent')
    @patch('src.models.model_selector')
    @patch('src.config.config')
    def test_chat_endpoint_streaming(self, mock_config, mock_selector, mock_agent_class):
        """Test chat endpoint with streaming"""
        from fastapi.testclient import TestClient

        # Setup mocks
        mock_config.get.side_effect = lambda key, default=None: {
            'api.rate_limit': '100/minute',
            'api.max_request_size': 1024*1024,
            'models.default': 'claude-3-haiku-20240307'
        }.get(key, default)

        def mock_stream():
            yield "Hello "
            yield "world!"

        mock_agent = MagicMock()
        mock_agent.process_request.return_value = mock_stream()
        mock_agent_class.return_value = mock_agent

        app = create_app()
        client = TestClient(app)

        # Test POST /chat with streaming
        response = client.post("/chat", json={
            "query": "Hello world",
            "model_id": "claude-3-haiku-20240307",
            "provider": "anthropic",
            "stream": True
        })

        assert response.status_code == 200
        content = response.content.decode()
        assert "Hello" in content

    @patch('src.api.app.FASTAPI_AVAILABLE', True)
    @patch('src.models.model_selector')
    @patch('src.config.config')
    def test_models_endpoint(self, mock_config, mock_selector):
        """Test models endpoint"""
        from fastapi.testclient import TestClient

        # Setup mocks
        mock_config.get.side_effect = lambda key, default=None: {
            'api.rate_limit': '100/minute',
            'api.max_request_size': 1024*1024
        }.get(key, default)

        mock_selector.list_available_models.return_value = {
            'anthropic': {'name': 'Anthropic', 'models': {}}
        }

        app = create_app()
        client = TestClient(app)

        # Test GET /models
        response = client.get("/models")

        assert response.status_code == 200
        data = response.json()
        assert 'anthropic' in data

    @patch('src.api.app.FASTAPI_AVAILABLE', True)
    @patch('src.config.config')
    def test_health_endpoint(self, mock_config):
        """Test health check endpoint"""
        from fastapi.testclient import TestClient

        # Setup mocks
        mock_config.get.side_effect = lambda key, default=None: {
            'api.rate_limit': '100/minute',
            'api.max_request_size': 1024*1024
        }.get(key, default)

        app = create_app()
        client = TestClient(app)

        # Test GET /health
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"

    @patch('src.api.app.FASTAPI_AVAILABLE', True)
    @patch('src.models.model_selector')
    @patch('src.config.config')
    def test_chat_endpoint_error_handling(self, mock_config, mock_selector):
        """Test error handling in chat endpoint"""
        from fastapi.testclient import TestClient

        # Setup mocks
        mock_config.get.side_effect = lambda key, default=None: {
            'api.rate_limit': '100/minute',
            'api.max_request_size': 1024*1024,
            'models.default': 'invalid-model'
        }.get(key, default)

        app = create_app()
        client = TestClient(app)

        # Test POST /chat with invalid model
        response = client.post("/chat", json={
            "query": "Hello world",
            "model_id": "invalid-model",
            "provider": "invalid-provider"
        })

        # Should return 500 error for invalid model
        assert response.status_code == 500
        data = response.json()
        assert "Failed to create agent" in data["detail"]


class TestWebSocketAPI:
    """Test cases for WebSocket endpoints"""

    @patch('src.config.config')
    @patch('src.agents.ConfigurableAgent')
    @pytest.mark.asyncio
    async def test_websocket_chat_basic(self, mock_agent_class, mock_config):
        """Test basic WebSocket chat functionality"""
        from src.api import create_app
        
        mock_config.get.side_effect = lambda key, default: {
            'models.default': 'gpt-3.5-turbo'
        }.get(key, default)
        
        mock_config.get_predefined_agents.return_value = {}
        
        mock_agent = MagicMock()
        mock_agent.process_request.return_value = ["Hello", " ", "world", "!"]
        mock_agent_class.return_value = mock_agent
        
        app = create_app()
        
        # Test with test client that supports WebSocket
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        with client.websocket_connect("/ws/chat") as websocket:
            # Send chat request
            websocket.send_json({
                "query": "Hello world",
                "model_id": "gpt-3.5-turbo",
                "provider": "openai",
                "stream": True
            })
            
            # Receive streaming chunks
            messages = []
            while True:
                data = websocket.receive_json()
                messages.append(data)
                if data.get("type") == "done":
                    break
            
            # Verify response structure
            assert len(messages) == 5  # 4 chunks + done
            assert messages[0] == {"type": "chunk", "content": "Hello"}
            assert messages[1] == {"type": "chunk", "content": " "}
            assert messages[2] == {"type": "chunk", "content": "world"}
            assert messages[3] == {"type": "chunk", "content": "!"}
            assert messages[4] == {"type": "done"}

    @patch('src.config.config')
    @patch('src.agents.ConfigurableAgent')
    @pytest.mark.asyncio
    async def test_websocket_chat_with_predefined_agent(self, mock_agent_class, mock_config):
        """Test WebSocket chat with predefined agent"""
        from src.api import create_app
        
        mock_config.get_predefined_agents.return_value = {
            'financial_analyst': {
                'model_id': 'claude-3-haiku',
                'provider': 'anthropic',
                'role': 'Financial Analyst',
                'goal': 'Analyze financial data',
                'backstory': 'Expert analyst'
            }
        }
        
        mock_agent = MagicMock()
        mock_agent.process_request.return_value = "Financial analysis complete"
        mock_agent_class.return_value = mock_agent
        
        app = create_app()
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        with client.websocket_connect("/ws/chat") as websocket:
            # Send request with predefined agent
            websocket.send_json({
                "query": "Analyze stocks",
                "agent_id": "financial_analyst",
                "stream": False
            })
            
            # Receive response
            data = websocket.receive_json()
            
            # Verify response
            assert data == {
                "type": "response",
                "content": "Financial analysis complete"
            }

    @patch('src.config.config')
    @patch('src.agents.ConfigurableAgent')
    @pytest.mark.asyncio
    async def test_websocket_chat_with_sampling_params(self, mock_agent_class, mock_config):
        """Test WebSocket chat with sampling parameters"""
        from src.api import create_app
        
        mock_config.get.side_effect = lambda key, default: {
            'models.default': 'gpt-3.5-turbo'
        }.get(key, default)
        
        mock_config.get_predefined_agents.return_value = {}
        
        mock_agent = MagicMock()
        mock_agent.process_request.return_value = "Creative response"
        mock_agent_class.return_value = mock_agent
        
        app = create_app()
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        with client.websocket_connect("/ws/chat") as websocket:
            # Send request with sampling parameters
            websocket.send_json({
                "query": "Write a story",
                "model_id": "gpt-4",
                "provider": "openai",
                "temperature": 0.8,
                "top_p": 0.9,
                "max_tokens": 500,
                "presence_penalty": 0.1,
                "stream": False
            })
            
            # Receive response
            data = websocket.receive_json()
            
            # Verify response
            assert data == {
                "type": "response", 
                "content": "Creative response"
            }

    @patch('src.config.config')
    @patch('src.agents.ConfigurableAgent')
    @patch('src.agents.MultiAgentCoordinator')
    @pytest.mark.asyncio
    async def test_websocket_multi_agent(self, mock_coordinator_class, mock_agent_class, mock_config):
        """Test WebSocket multi-agent coordination"""
        from src.api import create_app
        
        mock_config.get_predefined_agents.return_value = {
            'agent1': {
                'model_id': 'gpt-3.5-turbo',
                'provider': 'openai',
                'role': 'Agent 1',
                'goal': 'Help with tasks'
            },
            'agent2': {
                'model_id': 'claude-3-haiku',
                'provider': 'anthropic',
                'role': 'Agent 2',
                'goal': 'Help with tasks'
            }
        }
        
        mock_agent1 = MagicMock()
        mock_agent2 = MagicMock()
        mock_agent_class.side_effect = [mock_agent1, mock_agent2]
        
        mock_coordinator = MagicMock()
        mock_coordinator.coordinate.return_value = ["Coordinated", " ", "response"]
        mock_coordinator_class.return_value = mock_coordinator
        
        app = create_app()
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        with client.websocket_connect("/ws/multi-agent") as websocket:
            # Send multi-agent request
            websocket.send_json({
                "query": "Test coordination",
                "coordination_mode": "ensemble",
                "agents": ["agent1", "agent2"],
                "stream": True
            })
            
            # Receive streaming response
            messages = []
            while True:
                data = websocket.receive_json()
                messages.append(data)
                if data.get("type") == "done":
                    break
            
            # Verify response structure
            assert len(messages) == 4  # 3 chunks + done
            assert messages[3] == {"type": "done"}

    @pytest.mark.asyncio
    async def test_websocket_health(self):
        """Test WebSocket health check"""
        from src.api import create_app
        import json
        
        app = create_app()
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        with client.websocket_connect("/ws/health") as websocket:
            # Send health check request (any message)
            websocket.send_text("ping")
            
            # Receive health response
            data = websocket.receive_json()
            
            # Verify health response structure
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert data["version"] == "1.0.0"
            assert data["connection"] == "websocket"

    @patch('src.config.config')
    @patch('src.agents.ConfigurableAgent')
    @pytest.mark.asyncio
    async def test_websocket_chat_error_handling(self, mock_agent_class, mock_config):
        """Test WebSocket chat error handling"""
        from src.api import create_app
        
        mock_config.get.side_effect = lambda key, default: {
            'models.default': 'gpt-3.5-turbo'
        }.get(key, default)
        
        mock_config.get_predefined_agents.return_value = {}
        
        # Make agent creation fail
        mock_agent_class.side_effect = Exception("Agent creation failed")
        
        app = create_app()
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        with client.websocket_connect("/ws/chat") as websocket:
            # Send request that will cause error
            websocket.send_json({
                "query": "This will fail",
                "model_id": "invalid-model",
                "provider": "invalid-provider"
            })
            
            # Receive error response
            data = websocket.receive_json()
            
            # Verify error response
            assert data["type"] == "error"
            assert "Agent creation failed" in data["message"]

    @patch('src.config.config')
    @pytest.mark.asyncio
    async def test_websocket_multi_agent_invalid_mode(self, mock_config):
        """Test WebSocket multi-agent with invalid coordination mode"""
        from src.api import create_app
        
        mock_config.get_predefined_agents.return_value = {
            'agent1': {'model_id': 'gpt-3.5-turbo', 'provider': 'openai'}
        }
        
        app = create_app()
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        with client.websocket_connect("/ws/multi-agent") as websocket:
            # Send request with invalid mode
            websocket.send_json({
                "query": "Test",
                "coordination_mode": "invalid_mode",
                "agents": ["agent1"]
            })
            
            # Receive error response
            data = websocket.receive_json()
            
            # Verify error response
            assert data["type"] == "error"
            assert "Unknown coordination mode" in data["message"]


if __name__ == "__main__":
    pytest.main([__file__])