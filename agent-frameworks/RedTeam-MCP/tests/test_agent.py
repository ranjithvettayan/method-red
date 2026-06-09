#!/usr/bin/env python3
"""
Unit tests for agent functionality
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agents import ConfigurableAgent


class TestConfigurableAgent:
    """Test cases for ConfigurableAgent class"""

    @patch("src.agents.configurable_agent.model_selector")
    @patch("src.agents.configurable_agent.provider_registry")
    def test_agent_init_success(self, mock_registry, mock_selector):
        """Test successful agent initialization"""
        # Mock model selector
        mock_selector.get_model_info.return_value = {
            "provider": "anthropic",
            "model": {"name": "Claude 3 Haiku"},
            "provider_name": "Anthropic",
        }

        # Mock provider registry
        mock_registry.get_api_key.return_value = "test_api_key"
        mock_registry.get_model_string.return_value = (
            "anthropic/claude-3-haiku-20240307"
        )

        # Mock CrewAI components
        with (
            patch("src.agents.configurable_agent.LLM") as mock_llm_class,
            patch("src.agents.configurable_agent.Agent") as mock_agent_class,
            patch("src.agents.configurable_agent.LongTermMemory"),
            patch("src.agents.configurable_agent.ShortTermMemory"),
        ):
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm

            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            agent = ConfigurableAgent(
                model_id="claude-3-haiku-20240307",
                provider="anthropic",
                role="Test Role",
                goal="Test Goal",
                backstory="Test Backstory",
            )

            assert agent.model_id == "claude-3-haiku-20240307"
            assert agent.role == "Test Role"
            assert agent.goal == "Test Goal"
            assert agent.backstory == "Test Backstory"
            assert agent.model_info["provider"] == "anthropic"

    @patch("src.agents.configurable_agent.provider_registry")
    def test_agent_init_no_api_key_for_provider(self, mock_registry):
        """Test agent initialization with provider that has no API key"""
        mock_registry.get_api_key.return_value = None

        with pytest.raises(ValueError, match="API key not configured for provider: test-provider"):
            ConfigurableAgent(
                model_id="test-model",
                provider="test-provider",
                role="Test Role",
                goal="Test Goal",
                backstory="Test Backstory",
            )

    @patch("src.agents.configurable_agent.model_selector")
    @patch("src.agents.configurable_agent.provider_registry")
    def test_agent_init_no_api_key(self, mock_registry, mock_selector):
        """Test agent initialization without API key"""
        # Mock model selector
        mock_selector.get_model_info.return_value = {
            "provider": "anthropic",
            "model": {"name": "Claude 3 Haiku"},
            "provider_name": "Anthropic",
        }

        # Mock provider registry - no API key
        mock_registry.get_api_key.return_value = None

        with pytest.raises(
            ValueError, match="API key not configured for provider: anthropic"
        ):
            ConfigurableAgent(
                model_id="claude-3-haiku-20240307",
                provider="anthropic",
                role="Test Role",
                goal="Test Goal",
                backstory="Test Backstory",
            )

    @patch("src.agents.configurable_agent.model_selector")
    @patch("src.agents.configurable_agent.provider_registry")
    def test_agent_sampling_params(self, mock_registry, mock_selector):
        """Test agent initialization with sampling parameters"""
        # Mock model selector
        mock_selector.get_model_info.return_value = {
            "provider": "anthropic",
            "model": {"name": "Claude 3 Haiku"},
            "provider_name": "Anthropic",
        }
        
        # Mock validate_and_adjust_params to return validated params
        mock_selector.validate_and_adjust_params.return_value = {
            'params': {
                'temperature': 0.7,
                'max_tokens': 1000,
            },
            'warnings': [],
            'constraints': {
                'context_length': 128000,
                'max_output': 8192,
                'supports_temperature': True,
                'supports_reasoning': False,
            }
        }

        # Mock provider registry
        mock_registry.get_api_key.return_value = "test_api_key"
        mock_registry.get_model_string.return_value = (
            "anthropic/claude-3-haiku-20240307"
        )
        mock_registry.get_base_url.return_value = None  # Native LiteLLM provider

        # Mock CrewAI components
        with (
            patch("src.agents.configurable_agent.LLM") as mock_llm_class,
            patch("src.agents.configurable_agent.Agent") as mock_agent_class,
            patch("src.agents.configurable_agent.LongTermMemory"),
            patch("src.agents.configurable_agent.ShortTermMemory"),
        ):
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm

            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            agent = ConfigurableAgent(
                model_id="claude-3-haiku-20240307",
                provider="anthropic",
                role="Test Role",
                goal="Test Goal",
                backstory="Test Backstory",
                temperature=0.7,
                max_tokens=1000,
                top_p=0.9,
            )

            # Check that LLM was created with validated sampling parameters
            mock_llm_class.assert_called_once()
            # LLM is now called with model, api_key, and validated sampling params
            # Note: base_url is NOT included when it's None (native LiteLLM provider)
            mock_llm_class.assert_called_with(
                model="anthropic/claude-3-haiku-20240307",
                api_key="test_api_key",
                temperature=0.7,
                max_tokens=1000,
                top_p=0.9,  # top_p is passed through without validation
            )

    @patch("src.agents.configurable_agent.model_selector")
    @patch("src.agents.configurable_agent.provider_registry")
    def test_agent_process_request(self, mock_registry, mock_selector):
        """Test processing a request"""
        # Mock model selector
        mock_selector.get_model_info.return_value = {
            "provider": "anthropic",
            "model": {"name": "Claude 3 Haiku"},
            "provider_name": "Anthropic",
        }

        # Mock provider registry
        mock_registry.get_api_key.return_value = "test_api_key"
        mock_registry.get_model_string.return_value = (
            "anthropic/claude-3-haiku-20240307"
        )

        # Mock CrewAI components
        with (
            patch("src.agents.configurable_agent.LLM") as mock_llm_class,
            patch("src.agents.configurable_agent.Agent") as mock_agent_class,
            patch("src.agents.configurable_agent.Task") as mock_task_class,
            patch("src.agents.configurable_agent.Crew") as mock_crew_class,
        ):
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm

            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            mock_task = MagicMock()
            mock_task_class.return_value = mock_task

            mock_crew = MagicMock()
            mock_crew_class.return_value = mock_crew

            # Mock crew result
            mock_result = MagicMock()
            mock_result.raw = "Test response"
            mock_crew.kickoff.return_value = mock_result

            agent = ConfigurableAgent(
                model_id="claude-3-haiku-20240307",
                provider="anthropic",
                role="Test Role",
                goal="Test Goal",
                backstory="Test Backstory",
            )

            response = agent.process_request("Test request")

            assert response == "Test response"
            mock_crew.kickoff.assert_called_once()

    @patch("src.agents.configurable_agent.model_selector")
    @patch("src.agents.configurable_agent.provider_registry")
    def test_agent_process_request_streaming(self, mock_registry, mock_selector):
        """Test processing a request with streaming"""
        # Mock model selector
        mock_selector.get_model_info.return_value = {
            "provider": "anthropic",
            "model": {"name": "Claude 3 Haiku"},
            "provider_name": "Anthropic",
        }

        # Mock provider registry
        mock_registry.get_api_key.return_value = "test_api_key"
        mock_registry.get_model_string.return_value = (
            "anthropic/claude-3-haiku-20240307"
        )

        # Mock CrewAI components
        with (
            patch("src.agents.configurable_agent.LLM") as mock_llm_class,
            patch("src.agents.configurable_agent.Agent") as mock_agent_class,
            patch("src.agents.configurable_agent.Task") as mock_task_class,
            patch("src.agents.configurable_agent.Crew") as mock_crew_class,
        ):
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm

            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            mock_task = MagicMock()
            mock_task_class.return_value = mock_task

            mock_crew = MagicMock()
            mock_crew_class.return_value = mock_crew

            # Mock crew result with longer text
            mock_result = MagicMock()
            mock_result.raw = "This is a very long test response for streaming that should be chunked into multiple parts when streaming is enabled."
            mock_crew.kickoff.return_value = mock_result

            agent = ConfigurableAgent(
                model_id="claude-3-haiku-20240307",
                provider="anthropic",
                role="Test Role",
                goal="Test Goal",
                backstory="Test Backstory",
            )

            stream_generator = agent.process_request("Test request", stream=True)

            # Collect all chunks from the generator
            chunks = list(stream_generator)
            response = "".join(chunks)

            assert (
                response
                == "This is a very long test response for streaming that should be chunked into multiple parts when streaming is enabled."
            )
            assert len(chunks) > 1  # Should be chunked

    @patch("src.agents.configurable_agent.model_selector")
    @patch("src.agents.configurable_agent.provider_registry")
    def test_agent_get_model_info(self, mock_registry, mock_selector):
        """Test getting model information"""
        # Mock model selector
        mock_model_info = {
            "provider": "anthropic",
            "model": {"name": "Claude 3 Haiku", "tool_call": True},
            "provider_name": "Anthropic",
        }
        mock_selector.get_model_info.return_value = mock_model_info

        # Mock provider registry
        mock_registry.get_api_key.return_value = "test_api_key"
        mock_registry.get_model_string.return_value = (
            "anthropic/claude-3-haiku-20240307"
        )

        # Mock CrewAI components
        with (
            patch("src.agents.configurable_agent.LLM") as mock_llm_class,
            patch("src.agents.configurable_agent.Agent") as mock_agent_class,
            patch("src.agents.configurable_agent.LongTermMemory"),
            patch("src.agents.configurable_agent.ShortTermMemory"),
        ):
            mock_llm = MagicMock()
            mock_llm_class.return_value = mock_llm

            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            agent = ConfigurableAgent(
                model_id="claude-3-haiku-20240307",
                provider="anthropic",
                role="Test Role",
                goal="Test Goal",
                backstory="Test Backstory",
            )

            info = agent.get_model_info()

            assert info["model_id"] == "claude-3-haiku-20240307"
            assert info["provider"] == "anthropic"
            assert info["provider_name"] == "Anthropic"
            # Real model info from models.dev has tool_call: True for Claude
            assert "tool_call" in info["capabilities"]


if __name__ == "__main__":
    pytest.main([__file__])
