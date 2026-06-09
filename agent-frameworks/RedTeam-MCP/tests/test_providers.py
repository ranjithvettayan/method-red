#!/usr/bin/env python3
"""
Unit tests for provider registry and individual providers
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.providers.base import BaseProvider
from src.providers.registry import ProviderRegistry
from src.providers.core.anthropic import AnthropicProvider
from src.providers.core.openai import OpenAIProvider


class TestBaseProvider:
    """Test cases for BaseProvider abstract class"""

    def test_base_provider_abstract_methods(self):
        """Test that BaseProvider defines required abstract methods"""
        # This should raise TypeError because BaseProvider is abstract
        with pytest.raises(TypeError):
            BaseProvider()

    def test_base_provider_inheritance(self):
        """Test that concrete providers can inherit from BaseProvider"""
        class TestProvider(BaseProvider):
            def __init__(self):
                super().__init__("test_provider")

            def get_api_key(self, model_id=None):
                return "test_key"

            def get_model_string(self, model_id):
                return f"test/{model_id}"

        provider = TestProvider()
        assert provider.provider_id == "test_provider"
        assert provider.get_api_key() == "test_key"
        assert provider.get_model_string("model1") == "test/model1"


class TestProviderRegistry:
    """Test cases for ProviderRegistry"""

    def test_registry_initialization(self):
        """Test that registry initializes with all providers"""
        registry = ProviderRegistry()

        # Should have loaded all providers
        assert len(registry.providers) > 0

        # Should have core providers
        assert 'anthropic' in registry.providers
        assert 'openai' in registry.providers

    def test_get_provider(self):
        """Test getting a provider by name"""
        registry = ProviderRegistry()

        provider = registry.get_provider('anthropic')
        assert provider is not None
        assert isinstance(provider, AnthropicProvider)

    def test_get_provider_not_found(self):
        """Test getting a non-existent provider"""
        registry = ProviderRegistry()

        provider = registry.get_provider('nonexistent')
        assert provider is None

    def test_get_available_providers(self):
        """Test getting all available providers"""
        registry = ProviderRegistry()

        providers = registry.get_available_providers()
        assert isinstance(providers, dict)
        assert len(providers) > 0

    def test_get_configured_providers(self):
        """Test getting configured providers"""
        registry = ProviderRegistry()

        providers = registry.get_configured_providers()
        assert isinstance(providers, dict)
        # May be empty if no API keys are set


class TestAnthropicProvider:
    """Test cases for AnthropicProvider"""

    def test_anthropic_provider_init(self):
        """Test Anthropic provider initialization"""
        provider = AnthropicProvider()
        assert provider.provider_id == 'anthropic'

    def test_anthropic_provider_get_api_key(self):
        """Test getting API key from Anthropic provider"""
        provider = AnthropicProvider()

        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'}):
            api_key = provider.get_api_key()
            assert api_key == 'test_key'

    def test_anthropic_provider_get_api_key_none(self):
        """Test getting API key when not set"""
        provider = AnthropicProvider()

        with patch.dict(os.environ, {}, clear=True), \
             patch('src.providers.core.anthropic.config') as mock_config:
            mock_config.get.return_value = None
            api_key = provider.get_api_key()
            assert api_key is None

    def test_anthropic_provider_get_model_string(self):
        """Test getting model string from Anthropic provider"""
        provider = AnthropicProvider()

        model_string = provider.get_model_string('claude-3-haiku-20240307')
        assert model_string == 'anthropic/claude-3-haiku-20240307'

    def test_anthropic_provider_is_configured(self):
        """Test checking if Anthropic provider is configured"""
        provider = AnthropicProvider()

        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'}), \
             patch('src.providers.core.anthropic.config') as mock_config:
            mock_config.get.return_value = None
            assert provider.is_configured() is True

        with patch.dict(os.environ, {}, clear=True), \
             patch('src.providers.core.anthropic.config') as mock_config:
            mock_config.get.return_value = None
            assert provider.is_configured() is False


class TestOpenAIProvider:
    """Test cases for OpenAIProvider"""

    def test_openai_provider_init(self):
        """Test OpenAI provider initialization"""
        provider = OpenAIProvider()
        assert provider.provider_id == 'openai'

    def test_openai_provider_get_api_key(self):
        """Test getting API key from OpenAI provider"""
        provider = OpenAIProvider()

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            api_key = provider.get_api_key()
            assert api_key == 'test_key'

    def test_openai_provider_get_api_key_none(self):
        """Test getting API key when not set"""
        provider = OpenAIProvider()

        with patch.dict(os.environ, {}, clear=True), \
             patch('src.providers.core.openai.config') as mock_config:
            mock_config.get.return_value = None
            api_key = provider.get_api_key()
            assert api_key is None

    def test_openai_provider_get_model_string(self):
        """Test getting model string from OpenAI provider"""
        provider = OpenAIProvider()

        model_string = provider.get_model_string('gpt-4')
        assert model_string == 'openai/gpt-4'

    def test_openai_provider_is_configured(self):
        """Test checking if OpenAI provider is configured"""
        provider = OpenAIProvider()

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}), \
             patch('src.providers.core.openai.config') as mock_config:
            mock_config.get.return_value = None
            assert provider.is_configured() is True

        with patch.dict(os.environ, {}, clear=True), \
             patch('src.providers.core.openai.config') as mock_config:
            mock_config.get.return_value = None
            assert provider.is_configured() is False


class TestOpenAICompatibleProviders:
    """Test cases for OpenAI-compatible providers with base_url"""

    def test_native_litellm_provider_no_base_url(self):
        """Test that native LiteLLM providers return None for base_url"""
        provider = AnthropicProvider()
        assert provider.get_base_url() is None

        provider = OpenAIProvider()
        assert provider.get_base_url() is None

    def test_openai_compatible_provider_has_base_url(self):
        """Test that OpenAI-compatible providers return a base_url"""
        from src.providers.other.siliconflow import SiliconflowProvider
        from src.providers.other.venice import VeniceProvider
        from src.providers.chinese.alibaba import AlibabaProvider

        siliconflow = SiliconflowProvider()
        assert siliconflow.get_base_url() == "https://api.siliconflow.com/v1"
        assert siliconflow.get_model_string("qwen-2-72b") == "openai/qwen-2-72b"

        venice = VeniceProvider()
        assert venice.get_base_url() == "https://api.venice.ai/api/v1"
        assert venice.get_model_string("llama-3.1-405b") == "openai/llama-3.1-405b"

        alibaba = AlibabaProvider()
        assert alibaba.get_base_url() == "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    def test_registry_get_base_url(self):
        """Test that registry correctly returns base_url"""
        registry = ProviderRegistry()

        # Native LiteLLM providers should return None
        assert registry.get_base_url('anthropic') is None
        assert registry.get_base_url('openai') is None

        # OpenAI-compatible providers should return their base_url
        assert registry.get_base_url('siliconflow') == "https://api.siliconflow.com/v1"
        assert registry.get_base_url('venice') == "https://api.venice.ai/api/v1"

        # Non-existent provider should return None
        assert registry.get_base_url('nonexistent') is None


if __name__ == "__main__":
    pytest.main([__file__])