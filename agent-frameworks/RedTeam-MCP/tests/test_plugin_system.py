import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.providers.plugin_system import PluginManager, ProviderPlugin, plugin_manager
from src.providers.plugin_registry import PluginProviderRegistry
from src.providers.base import BaseProvider


class MockProvider(BaseProvider):
    """Mock provider for testing"""

    def __init__(self, api_key=None):
        super().__init__(api_key)

    def get_api_key(self):
        return self.api_key

    def get_model_string(self, model_name):
        return f"mock-{model_name}"

    def is_configured(self):
        return self.api_key is not None


class TestProviderPlugin:
    """Test cases for ProviderPlugin class"""

    def test_plugin_initialization(self):
        """Test plugin initialization with metadata"""
        metadata = {
            'version': '1.0.0',
            'description': 'Test provider',
            'author': 'Test Author',
            'module': 'test.module',
            'class_name': 'TestProvider'
        }

        plugin = ProviderPlugin('test_provider', MockProvider, metadata)

        assert plugin.name == 'test_provider'
        assert plugin.provider_class == MockProvider
        assert plugin.metadata == metadata
        assert plugin.instance is None

    def test_plugin_instance_creation(self):
        """Test lazy instance creation"""
        plugin = ProviderPlugin('test_provider', MockProvider, {})

        # Initially no instance
        assert plugin.instance is None

        # Create instance creates it
        instance = plugin.create_instance()
        assert isinstance(instance, MockProvider)
        assert plugin.instance is instance

        # Subsequent calls return same instance
        instance2 = plugin.create_instance()
        assert instance2 is instance

    @patch('src.config.config')
    def test_plugin_is_enabled_default(self, mock_config):
        """Test plugin enabled status with default config"""
        mock_config.get.return_value = []  # No enabled/disabled lists

        plugin = ProviderPlugin('test_provider', MockProvider, {})
        assert plugin.is_enabled() is True

    @patch('src.config.config')
    def test_plugin_is_enabled_in_list(self, mock_config):
        """Test plugin enabled when in enabled list"""
        mock_config.get.side_effect = lambda key, default: ['test_provider'] if key == 'providers.enabled' else []

        plugin = ProviderPlugin('test_provider', MockProvider, {})
        assert plugin.is_enabled() is True

    @patch('src.config.config')
    def test_plugin_is_disabled_in_list(self, mock_config):
        """Test plugin disabled when in disabled list"""
        mock_config.get.side_effect = lambda key, default: ['test_provider'] if key == 'providers.disabled' else []

        plugin = ProviderPlugin('test_provider', MockProvider, {})
        assert plugin.is_enabled() is False


class TestPluginManager:
    """Test cases for PluginManager class"""

    def test_manager_initialization(self):
        """Test plugin manager initialization"""
        manager = PluginManager()

        assert manager.plugins == {}
        assert manager.discovery_paths == []

    def test_add_discovery_path(self):
        """Test adding discovery paths"""
        manager = PluginManager()
        test_path = Path('/test/path')

        manager.add_discovery_path(test_path)
        assert test_path in manager.discovery_paths

        # Adding same path again should not duplicate
        manager.add_discovery_path(test_path)
        assert manager.discovery_paths.count(test_path) == 1

    def test_get_plugin(self):
        """Test getting a plugin by name"""
        manager = PluginManager()
        plugin = ProviderPlugin('test_plugin', MockProvider, {})

        manager.plugins['test_plugin'] = plugin

        assert manager.get_plugin('test_plugin') is plugin
        assert manager.get_plugin('nonexistent') is None

    def test_get_enabled_plugins(self):
        """Test getting enabled plugins"""
        manager = PluginManager()

        # Add test plugins
        plugin1 = ProviderPlugin('enabled_plugin', MockProvider, {})
        plugin2 = ProviderPlugin('disabled_plugin', MockProvider, {})

        manager.plugins = {
            'enabled_plugin': plugin1,
            'disabled_plugin': plugin2
        }

        with patch.object(plugin1, 'is_enabled', return_value=True), \
             patch.object(plugin2, 'is_enabled', return_value=False):

            enabled = manager.get_enabled_plugins()
            assert len(enabled) == 1
            assert 'enabled_plugin' in enabled
            assert enabled['enabled_plugin'] is plugin1

    def test_create_provider_instance(self):
        """Test creating provider instances"""
        manager = PluginManager()
        plugin = ProviderPlugin('test_plugin', MockProvider, {})

        manager.plugins['test_plugin'] = plugin

        with patch.object(plugin, 'is_enabled', return_value=True):
            instance = manager.create_provider_instance('test_plugin')
            assert isinstance(instance, MockProvider)
            assert plugin.instance is instance

    def test_create_provider_instance_disabled(self):
        """Test creating provider instance when disabled"""
        manager = PluginManager()
        plugin = ProviderPlugin('test_plugin', MockProvider, {})

        manager.plugins['test_plugin'] = plugin

        with patch.object(plugin, 'is_enabled', return_value=False):
            instance = manager.create_provider_instance('test_plugin')
            assert instance is None

    def test_get_plugin_info(self):
        """Test getting plugin information"""
        manager = PluginManager()

        metadata = {
            'version': '1.0.0',
            'description': 'Test plugin',
            'author': 'Test Author'
        }
        plugin = ProviderPlugin('test_plugin', MockProvider, metadata)
        manager.plugins = {'test_plugin': plugin}

        with patch.object(plugin, 'is_enabled', return_value=True):
            info = manager.get_plugin_info()

            assert 'test_plugin' in info
            assert info['test_plugin']['enabled'] is True
            assert info['test_plugin']['metadata'] == metadata
            assert info['test_plugin']['has_instance'] is False


class TestPluginProviderRegistry:
    """Test cases for PluginProviderRegistry class"""

    @patch('src.providers.plugin_registry.plugin_manager')
    def test_registry_initialization(self, mock_plugin_manager):
        """Test registry initialization with plugin system"""
        mock_plugin_manager.get_enabled_plugins.return_value = {}
        mock_plugin_manager.discover_plugins = MagicMock()

        registry = PluginProviderRegistry()

        # Should call discover_plugins and get_enabled_plugins
        mock_plugin_manager.discover_plugins.assert_called_once()
        mock_plugin_manager.get_enabled_plugins.assert_called_once()

    @patch('src.providers.plugin_registry.plugin_manager')
    def test_get_provider(self, mock_plugin_manager):
        """Test getting a provider from the plugin registry"""
        mock_plugin_manager.get_enabled_plugins.return_value = {}
        mock_plugin_manager.discover_plugins = MagicMock()

        registry = PluginProviderRegistry()

        # Add a provider manually for testing
        mock_provider = MagicMock()
        registry.providers['test_provider'] = mock_provider

        provider = registry.get_provider('test_provider')
        assert provider == mock_provider

    @patch('src.providers.plugin_registry.plugin_manager')
    def test_get_provider_not_found(self, mock_plugin_manager):
        """Test getting a non-existent provider"""
        mock_plugin_manager.get_enabled_plugins.return_value = {}
        mock_plugin_manager.discover_plugins = MagicMock()

        registry = PluginProviderRegistry()

        provider = registry.get_provider('nonexistent')
        assert provider is None

    @patch('src.providers.plugin_registry.plugin_manager')
    def test_get_available_providers(self, mock_plugin_manager):
        """Test getting list of available providers"""
        mock_plugin_manager.get_enabled_plugins.return_value = {}
        mock_plugin_manager.discover_plugins = MagicMock()

        registry = PluginProviderRegistry()

        # Add test providers
        registry.providers = {
            'provider1': MagicMock(),
            'provider2': MagicMock()
        }

        available = registry.get_available_providers()
        assert len(available) == 2
        assert 'provider1' in available
        assert 'provider2' in available

    @patch('src.providers.plugin_registry.plugin_manager')
    def test_get_configured_providers(self, mock_plugin_manager):
        """Test getting configured providers"""
        mock_plugin_manager.get_enabled_plugins.return_value = {}
        mock_plugin_manager.discover_plugins = MagicMock()

        registry = PluginProviderRegistry()

        # Add test providers with different configured status
        configured_provider = MagicMock()
        configured_provider.is_configured.return_value = True

        unconfigured_provider = MagicMock()
        unconfigured_provider.is_configured.return_value = False

        registry.providers = {
            'configured': configured_provider,
            'unconfigured': unconfigured_provider
        }

        configured = registry.get_configured_providers()
        assert len(configured) == 1
        assert 'configured' in configured

    @patch('src.providers.plugin_registry.plugin_manager')
    def test_get_plugin_info(self, mock_plugin_manager):
        """Test getting plugin information from registry"""
        mock_info = {'test': 'info'}
        mock_plugin_manager.get_plugin_info.return_value = mock_info

        registry = PluginProviderRegistry()

        info = registry.get_plugin_info()
        assert info == mock_info
        mock_plugin_manager.get_plugin_info.assert_called_once()

    @patch('src.providers.plugin_registry.plugin_manager')
    def test_reload_plugins(self, mock_plugin_manager):
        """Test reloading plugins"""
        mock_plugin_manager.get_enabled_plugins.return_value = {}
        mock_plugin_manager.discover_plugins = MagicMock()

        registry = PluginProviderRegistry()

        # Add some providers
        registry.providers = {'test': MagicMock()}

        registry.reload_plugins()

        # Should clear providers and plugins, then reload
        assert registry.providers == {}
        # discover_plugins should be called twice (once in init, once in reload)
        assert mock_plugin_manager.discover_plugins.call_count == 2


class TestPluginDiscovery:
    """Test cases for plugin discovery functionality"""

    def test_discovery_runs_without_error(self):
        """Test that plugin discovery runs without throwing exceptions"""
        # This is a basic smoke test to ensure discovery doesn't crash
        # The actual functionality is tested through integration
        manager = PluginManager()

        # Should not raise any exceptions
        try:
            manager.discover_plugins()
        except Exception as e:
            pytest.fail(f"Plugin discovery failed with: {e}")


class TestPluginErrorHandling:
    """Test cases for plugin error handling"""

    @patch('src.providers.plugin_registry.plugin_manager')
    def test_load_plugins_with_creation_error(self, mock_plugin_manager):
        """Test loading plugins when provider creation fails"""
        mock_plugin_manager.discover_plugins = MagicMock()

        # Mock plugin that will fail to create instance
        failing_plugin = MagicMock()
        failing_plugin.create_instance.side_effect = Exception("Creation failed")
        failing_plugin.name = "failing_plugin"

        mock_plugin_manager.get_enabled_plugins.return_value = {
            'failing_plugin': failing_plugin
        }

        registry = PluginProviderRegistry()

        # Should not crash, provider should not be loaded
        assert 'failing_plugin' not in registry.providers