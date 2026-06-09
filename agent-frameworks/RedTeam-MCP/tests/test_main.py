#!/usr/bin/env python3
"""
Unit tests for main module
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src import main


class TestMain:
    """Test cases for main module"""

    @patch('src.cli.chat.config')
    @patch('src.main.setup_logging')
    @patch('src.main.FASTAPI_AVAILABLE', True)
    @patch('src.main.uvicorn')
    def test_main_serve_command(self, mock_uvicorn, mock_setup_logging, mock_config):
        """Test serve command"""
        mock_config.get.side_effect = lambda key, default: {
            'logging.level': 'INFO',
            'logging.file': 'agent.log',
            'api.host': '0.0.0.0',
            'api.port': 8000
        }.get(key, default)

        with patch('sys.argv', ['main.py', 'serve']):
            main.main()

        mock_setup_logging.assert_called_once()
        mock_uvicorn.run.assert_called_once()

    @patch('src.cli.chat.config')
    @patch('src.main.setup_logging')
    @patch('src.main.model_selector')
    @patch('builtins.print')
    def test_main_models_command(self, mock_print, mock_selector, mock_setup_logging, mock_config):
        """Test models command"""
        mock_config.get.side_effect = lambda key, default: {
            'logging.level': 'INFO',
            'logging.file': 'agent.log'
        }.get(key, default)

        mock_selector.list_available_models.return_value = {
            'anthropic': {
                'name': 'Anthropic',
                'models': {'claude-3-haiku': {}}
            }
        }

        with patch('sys.argv', ['main.py', 'models']):
            main.main()

        mock_print.assert_called()

    @patch('src.cli.chat.config')
    @patch('src.main.setup_logging')
    @patch('src.main.model_selector')
    @patch('src.main.ConfigurableAgent')
    @patch('builtins.print')
    def test_main_test_command(self, mock_print, mock_agent, mock_selector, mock_setup_logging, mock_config):
        """Test test command"""
        mock_config.get.side_effect = lambda key, default: {
            'logging.level': 'INFO',
            'logging.file': 'agent.log',
            'models.default': 'claude-3-haiku'
        }.get(key, default)

        mock_selector.list_available_models.return_value = {
            'anthropic': {
                'name': 'Anthropic',
                'models': {'claude-3-haiku': {}}
            }
        }

        with patch('sys.argv', ['main.py', 'test']):
            main.main()

        mock_print.assert_called()

    @patch('builtins.print')
    def test_main_unknown_command(self, mock_print):
        """Test unknown command"""
        with patch('sys.argv', ['main.py', 'unknown']):
            main.main()

        assert any("Unknown command: unknown" in str(call) for call in mock_print.call_args_list)

    @patch('builtins.print')
    def test_main_no_args(self, mock_print):
        """Test no arguments"""
        with patch('sys.argv', ['main.py']):
            main.main()

        assert any("Red Team MCP" in str(call) for call in mock_print.call_args_list)

    @patch('src.cli.chat.config')
    @patch('src.cli.chat.get_or_create_cli_agent')
    @patch('builtins.print')
    def test_chat_cli_with_sampling_parameters(self, mock_print, mock_get_agent, mock_config):
        """Test chat CLI with sampling parameters"""
        mock_config.get.side_effect = lambda key, default: {
            'models.default': 'gpt-3.5-turbo'
        }.get(key, default)
        
        mock_config.get_predefined_agents.return_value = {}
        
        mock_agent = MagicMock()
        mock_agent.process_request.return_value = "Test response"
        mock_get_agent.return_value = mock_agent

        with patch('sys.argv', ['main.py', 'chat', '--temperature', '0.7', '--max-tokens', '100', '--stream', 'Hello world']):
            main.main()

        # Verify agent was created with sampling parameters
        mock_get_agent.assert_called_once_with(
            model_id='gpt-3.5-turbo',
            provider='openai',
            role='Assistant',
            goal='Help users with their requests',
            backstory='A helpful AI assistant',
            enable_memory=True,
            session_id=None,
            temperature=0.7,
            top_p=None,
            top_k=None,
            max_tokens=100,
            presence_penalty=None,
            frequency_penalty=None,
            stop=None,
            seed=None,
            logprobs=None,
            reasoning_effort=None,
        )

    @patch('src.cli.chat.config')
    @patch('src.cli.chat.get_or_create_cli_agent')
    @patch('builtins.print')
    def test_chat_cli_with_predefined_agent(self, mock_print, mock_get_agent, mock_config):
        """Test chat CLI with predefined agent"""
        mock_config.get.side_effect = lambda key, default: {
            'models.default': 'gpt-3.5-turbo'
        }.get(key, default)
        
        mock_config.get_predefined_agents.return_value = {
            'financial_analyst': {
                'model_id': 'claude-3-haiku',
                'provider': 'anthropic',
                'role': 'Financial Analyst',
                'goal': 'Analyze financial data',
                'backstory': 'Expert analyst',
                'enable_memory': True
            }
        }
        
        mock_agent = MagicMock()
        mock_agent.process_request.return_value = "Financial analysis"
        mock_get_agent.return_value = mock_agent

        with patch('sys.argv', ['main.py', 'chat', '--agent-id', 'financial_analyst', 'Analyze stocks']):
            main.main()

        # Verify agent was created with predefined config
        mock_get_agent.assert_called_once_with(
            model_id='claude-3-haiku',
            provider='anthropic',
            role='Financial Analyst',
            goal='Analyze financial data',
            backstory='Expert analyst',
            enable_memory=True,
            session_id=None,
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
        )

    @patch('src.cli.chat.config')
    @patch('src.cli.chat.get_or_create_cli_agent')
    @patch('builtins.print')
    def test_chat_cli_with_session_and_user(self, mock_print, mock_get_agent, mock_config):
        """Test chat CLI with session ID and user ID"""
        mock_config.get.side_effect = lambda key, default: {
            'models.default': 'gpt-3.5-turbo'
        }.get(key, default)
        
        mock_config.get_predefined_agents.return_value = {}
        
        mock_agent = MagicMock()
        mock_agent.process_request.return_value = "Session response"
        mock_get_agent.return_value = mock_agent

        with patch('sys.argv', ['main.py', 'chat', '--session-id', 'session123', '--user-id', 'testuser', '--no-memory', 'Hello']):
            main.main()

        # Verify agent was created with session and user settings
        mock_get_agent.assert_called_once_with(
            model_id='gpt-3.5-turbo',
            provider='openai',
            role='Assistant',
            goal='Help users with their requests',
            backstory='A helpful AI assistant',
            enable_memory=False,  # --no-memory flag
            session_id='session123',
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
        )

    @patch('src.cli.chat.config')
    @patch('src.cli.chat.get_or_create_cli_agent')
    @patch('builtins.print')
    def test_chat_cli_help_output(self, mock_print, mock_get_agent, mock_config):
        """Test chat CLI help output shows all parameters"""
        mock_config.get.side_effect = lambda key, default: {
            'models.default': 'gpt-3.5-turbo'
        }.get(key, default)
        
        mock_config.get_predefined_agents.return_value = {}

        with patch('sys.argv', ['main.py', 'chat']):
            main.main()

        # Check that help output includes sampling parameters
        print_calls = [str(call) for call in mock_print.call_args_list]
        help_text = ' '.join(print_calls)
        
        assert '--temperature' in help_text
        assert '--max-tokens' in help_text
        assert '--top-p' in help_text
        assert '--top-k' in help_text
        assert '--presence-penalty' in help_text
        assert '--frequency-penalty' in help_text
        assert '--seed' in help_text
        assert '--logprobs' in help_text
        assert '--reasoning-effort' in help_text
        assert '--agent-id' in help_text
        assert '--session-id' in help_text
        assert '--user-id' in help_text
        assert '--no-memory' in help_text

    def test_get_or_create_cli_agent_caching(self):
        """Test agent caching functionality"""
        from src.cli import utils as cli_utils
        # Clear cache for test
        cli_utils.cli_agent_cache.clear()
        
        with patch('src.cli.utils.ConfigurableAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent
            
            # First call should create agent
            agent1 = cli_utils.get_or_create_cli_agent(
                model_id='test-model',
                provider='test-provider',
                role='Test Role',
                goal='Test Goal',
                backstory='Test Backstory'
            )
            
            assert mock_agent_class.call_count == 1
            
            # Second call with same params should reuse cached agent
            agent2 = cli_utils.get_or_create_cli_agent(
                model_id='test-model',
                provider='test-provider',
                role='Test Role',
                goal='Test Goal',
                backstory='Test Backstory'
            )
            
            assert mock_agent_class.call_count == 1  # Should not create new agent
            assert agent1 is agent2  # Should return same instance
            
            # Different params should create new agent
            agent3 = cli_utils.get_or_create_cli_agent(
                model_id='different-model',
                provider='test-provider',
                role='Test Role',
                goal='Test Goal',
                backstory='Test Backstory'
            )
            
            assert mock_agent_class.call_count == 2  # Should create new agent

    def test_get_or_create_cli_agent_with_sampling_params(self):
        """Test agent caching with sampling parameters"""
        from src.cli import utils as cli_utils
        cli_utils.cli_agent_cache.clear()
        
        with patch('src.cli.utils.ConfigurableAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent
            
            # Create agent with sampling parameters
            agent = cli_utils.get_or_create_cli_agent(
                model_id='test-model',
                provider='test-provider',
                role='Test Role',
                goal='Test Goal',
                backstory='Test Backstory',
                temperature=0.7,
                max_tokens=100,
                top_p=0.9
            )
            
            # Verify ConfigurableAgent was called with all parameters
            mock_agent_class.assert_called_once_with(
                model_id='test-model',
                provider='test-provider',
                role='Test Role',
                goal='Test Goal',
                backstory='Test Backstory',
                enable_memory=True,
                session_id=None,
                temperature=0.7,
                top_p=0.9,
                top_k=None,
                max_tokens=100,
                presence_penalty=None,
                frequency_penalty=None,
                stop=None,
                seed=None,
                logprobs=None,
                reasoning_effort=None,
            )

    @patch('src.cli.multi_agent.config')
    @patch('src.main.setup_logging')
    @patch('src.cli.multi_agent.get_or_create_cli_agent')
    @patch('src.cli.multi_agent.MultiAgentCoordinator')
    @patch('builtins.print')
    def test_multi_agent_cli_with_cached_agents(self, mock_print, mock_coordinator_class, mock_get_agent, mock_setup_logging, mock_config):
        """Test multi-agent CLI uses cached agent creation"""
        mock_config.get_predefined_agents.return_value = {
            'agent1': {
                'model_id': 'gpt-3.5-turbo',
                'provider': 'openai',
                'role': 'Agent 1',
                'goal': 'Help with tasks',
                'backstory': 'AI assistant'
            },
            'agent2': {
                'model_id': 'claude-3-haiku',
                'provider': 'anthropic',
                'role': 'Agent 2',
                'goal': 'Help with tasks',
                'backstory': 'AI assistant'
            }
        }
        
        mock_agent1 = MagicMock()
        mock_agent2 = MagicMock()
        mock_get_agent.side_effect = [mock_agent1, mock_agent2]
        
        mock_coordinator = MagicMock()
        mock_coordinator_class.return_value = mock_coordinator
        mock_coordinator.coordinate.return_value = "Coordinated response"

        with patch('sys.argv', ['main.py', 'multi-agent', '--agents', 'agent1,agent2', 'Test query']):
            main.main()

        # Verify get_or_create_cli_agent was called for each agent
        assert mock_get_agent.call_count == 2
        mock_get_agent.assert_any_call(
            model_id='gpt-3.5-turbo',
            provider='openai',
            role='Agent 1',
            goal='Help with tasks',
            backstory='AI assistant',
            enable_memory=True,
            session_id=None,
        )
        mock_get_agent.assert_any_call(
            model_id='claude-3-haiku',
            provider='anthropic',
            role='Agent 2',
            goal='Help with tasks',
            backstory='AI assistant',
            enable_memory=True,
            session_id=None,
        )