#!/usr/bin/env python3
"""
Tests for Dynamic MCP Server functionality
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add src to path for testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDynamicMCPServer:
    """Test cases for dynamic MCP server functionality"""

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_list_agents(self, mock_config):
        """Test listing available agents"""
        from src.mcp_server_dynamic import list_agents

        mock_config.get_predefined_agents.return_value = {
            'financial_analyst': {
                'role': 'Financial Analyst',
                'goal': 'Analyze financial data',
                'model_id': 'claude-3-haiku',
                'provider': 'anthropic'
            },
            'technical_expert': {
                'role': 'Technical Expert',
                'goal': 'Provide technical guidance',
                'model_id': 'gpt-4o',
                'provider': 'openai'
            }
        }

        result = await list_agents()

        assert "financial_analyst" in result
        assert "Financial Analyst" in result
        assert "technical_expert" in result
        assert "Technical Expert" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_list_agents_empty(self, mock_config):
        """Test listing agents when none configured"""
        from src.mcp_server_dynamic import list_agents

        mock_config.get_predefined_agents.return_value = {}

        result = await list_agents()

        assert "No agents configured" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_list_teams(self, mock_config):
        """Test listing available teams"""
        from src.mcp_server_dynamic import list_teams

        mock_config.get_teams.return_value = {
            'analysis_team': {
                'name': 'Analysis Team',
                'description': 'Financial analysis team',
                'members': ['financial_analyst', 'data_scientist'],
                'default_mode': 'coordinate'
            }
        }

        result = await list_teams()

        assert "analysis_team" in result
        assert "Analysis Team" in result
        assert "financial_analyst" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_list_teams_empty(self, mock_config):
        """Test listing teams when none configured"""
        from src.mcp_server_dynamic import list_teams

        mock_config.get_teams.return_value = {}

        result = await list_teams()

        assert "No teams configured" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_get_agent_info(self, mock_config):
        """Test getting agent info"""
        from src.mcp_server_dynamic import get_agent_info

        mock_config.get_predefined_agents.return_value = {
            'financial_analyst': {
                'name': 'Financial Analyst',
                'role': 'Senior Financial Analyst',
                'goal': 'Analyze financial data',
                'backstory': 'Expert in finance',
                'model_id': 'claude-3-haiku',
                'provider': 'anthropic',
                'enable_memory': True
            }
        }

        result = await get_agent_info('financial_analyst')

        assert "financial_analyst" in result
        assert "Senior Financial Analyst" in result
        assert "claude-3-haiku" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_get_agent_info_not_found(self, mock_config):
        """Test getting info for non-existent agent"""
        from src.mcp_server_dynamic import get_agent_info

        mock_config.get_predefined_agents.return_value = {}

        result = await get_agent_info('missing_agent')

        assert "not found" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic._get_or_create_agent')
    @patch('src.mcp_server_dynamic.config')
    async def test_chat(self, mock_config, mock_get_agent):
        """Test chatting with an agent"""
        from src.mcp_server_dynamic import chat

        mock_config.get_predefined_agents.return_value = {
            'financial_analyst': {
                'role': 'Financial Analyst',
                'model_id': 'claude-3-haiku',
                'provider': 'anthropic'
            }
        }

        mock_agent = MagicMock()
        mock_agent.process_request.return_value = "Test response from agent"
        mock_get_agent.return_value = mock_agent

        result = await chat('financial_analyst', 'Analyze this data')

        assert "Test response from agent" in result
        mock_agent.process_request.assert_called_once_with('Analyze this data')

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_chat_error(self, mock_config):
        """Test chat error handling with non-existent agent"""
        from src.mcp_server_dynamic import chat

        mock_config.get_predefined_agents.return_value = {}

        result = await chat('missing_agent', 'Hello')

        assert "not found" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    @patch('src.mcp_server_dynamic._get_or_create_agent')
    @patch('src.mcp_server_dynamic.MultiAgentCoordinator')
    async def test_coordinate(self, mock_coordinator_class, mock_get_agent, mock_config):
        """Test coordinating multiple agents"""
        from src.mcp_server_dynamic import coordinate

        mock_agent1 = MagicMock()
        mock_agent2 = MagicMock()
        mock_get_agent.side_effect = [mock_agent1, mock_agent2]

        mock_coordinator = MagicMock()
        mock_coordinator.coordinate.return_value = "Coordinated response"
        mock_coordinator_class.return_value = mock_coordinator

        mock_config.get_predefined_agents.return_value = {
            'agent1': {'model_id': 'test'},
            'agent2': {'model_id': 'test'}
        }

        # Note: coordinate takes agent_ids first, then query
        result = await coordinate(['agent1', 'agent2'], 'Test task', 'ensemble')

        assert "Coordinated response" in result
        mock_coordinator_class.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    @patch('src.mcp_server_dynamic._get_or_create_agent')
    @patch('src.mcp_server_dynamic.MultiAgentCoordinator')
    async def test_run_team(self, mock_coordinator_class, mock_get_agent, mock_config):
        """Test running a team"""
        from src.mcp_server_dynamic import run_team

        mock_config.get_team.return_value = {
            'name': 'Analysis Team',
            'members': ['agent1', 'agent2'],
            'default_mode': 'ensemble'
        }
        mock_config.get_predefined_agents.return_value = {
            'agent1': {'model_id': 'test', 'role': 'Agent 1', 'goal': 'Test', 'backstory': 'Test', 'provider': 'anthropic'},
            'agent2': {'model_id': 'test', 'role': 'Agent 2', 'goal': 'Test', 'backstory': 'Test', 'provider': 'anthropic'}
        }

        mock_agent1 = MagicMock()
        mock_agent2 = MagicMock()
        mock_get_agent.side_effect = [mock_agent1, mock_agent2]

        mock_coordinator = MagicMock()
        mock_coordinator.coordinate.return_value = "Team response"
        mock_coordinator_class.return_value = mock_coordinator

        result = await run_team('analysis_team', 'Test task')

        assert "Team response" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_run_team_not_found(self, mock_config):
        """Test running non-existent team"""
        from src.mcp_server_dynamic import run_team

        mock_config.get_team.return_value = None
        mock_config.get_teams.return_value = {}

        result = await run_team('missing_team', 'Test task')

        assert "not found" in result

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.chat')
    @patch('src.mcp_server_dynamic.config')
    async def test_ask_expert(self, mock_config, mock_chat):
        """Test asking an expert"""
        from src.mcp_server_dynamic import ask_expert

        mock_config.get_predefined_agents.return_value = {
            'financial_analyst': {'model_id': 'test', 'role': 'Financial Analyst'}
        }

        mock_chat.return_value = "Expert analysis"

        result = await ask_expert('financial', 'Analyze revenue')

        assert "Expert analysis" in result
        mock_chat.assert_called_once_with(agent_id='financial_analyst', message='Analyze revenue')

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.coordinate')
    @patch('src.mcp_server_dynamic.config')
    async def test_brainstorm(self, mock_config, mock_coordinate):
        """Test brainstorming with multiple agents"""
        from src.mcp_server_dynamic import brainstorm

        mock_config.get_predefined_agents.return_value = {
            'strategy_consultant': {'role': 'Strategy'},
            'technical_expert': {'role': 'Technical'}
        }

        mock_coordinate.return_value = "**Coordination Result** (ensemble mode with 2 agents)\n\nPerspective output"

        result = await brainstorm('Test topic', 2)

        assert "Coordination Result" in result
        mock_coordinate.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_agent_cache(self):
        """Test clearing agent cache"""
        import src.mcp_server_dynamic as mcp_module
        from src.mcp_server_dynamic import clear_agent_cache

        # Add something to cache
        mcp_module._agent_cache['test'] = MagicMock()

        result = await clear_agent_cache()

        assert "Cleared" in result
        assert len(mcp_module._agent_cache) == 0

    @pytest.mark.asyncio
    @patch('src.mcp_server_dynamic.config')
    async def test_reload_config(self, mock_config):
        """Test reloading configuration"""
        from src.mcp_server_dynamic import reload_config

        mock_config.reload.return_value = None
        mock_config.get_predefined_agents.return_value = {'agent1': {}, 'agent2': {}}
        mock_config.get_teams.return_value = {'team1': {}}

        result = await reload_config()

        assert "reloaded" in result
        mock_config.reload.assert_called_once()


class TestAgentCache:
    """Test agent caching functionality"""

    @patch('src.mcp_server_dynamic.config')
    @patch('src.mcp_server_dynamic.ConfigurableAgent')
    def test_get_or_create_agent_creates_new(self, mock_agent_class, mock_config):
        """Test creating a new agent"""
        import src.mcp_server_dynamic as mcp_module
        from src.mcp_server_dynamic import _get_or_create_agent

        # Clear cache
        mcp_module._agent_cache = {}

        mock_config.get_predefined_agents.return_value = {
            'test_agent': {
                'model_id': 'claude-3-haiku',
                'provider': 'anthropic',
                'role': 'Test Role',
                'goal': 'Test Goal',
                'backstory': 'Test Backstory',
                'enable_memory': True
            }
        }

        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        result = _get_or_create_agent('test_agent')

        assert result == mock_agent
        mock_agent_class.assert_called_once()

    @patch('src.mcp_server_dynamic.config')
    def test_get_or_create_agent_uses_cache(self, mock_config):
        """Test using cached agent"""
        import src.mcp_server_dynamic as mcp_module
        from src.mcp_server_dynamic import _get_or_create_agent

        # Pre-populate cache
        mock_agent = MagicMock()
        mcp_module._agent_cache = {'cached_agent': mock_agent}

        result = _get_or_create_agent('cached_agent')

        assert result == mock_agent
        # Config should not be called since agent is cached
        mock_config.get_predefined_agents.assert_not_called()

    @patch('src.mcp_server_dynamic.config')
    def test_get_or_create_agent_not_found(self, mock_config):
        """Test error when agent not found"""
        import src.mcp_server_dynamic as mcp_module
        from src.mcp_server_dynamic import _get_or_create_agent

        # Clear cache
        mcp_module._agent_cache = {}
        mock_config.get_predefined_agents.return_value = {}

        with pytest.raises(ValueError, match="not found in configuration"):
            _get_or_create_agent('missing_agent')


if __name__ == "__main__":
    pytest.main([__file__])
