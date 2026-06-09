#!/usr/bin/env python3
"""
Plugin-based provider registry
"""

from typing import Dict, Any, Optional
from .base import BaseProvider
from .plugin_system import plugin_manager

import logging
logger = logging.getLogger(__name__)


class PluginProviderRegistry:
    """Plugin-based registry for LLM providers"""

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Load providers from plugins"""
        # Discover all available plugins
        plugin_manager.discover_plugins()

        # Create instances for enabled plugins
        enabled_plugins = plugin_manager.get_enabled_plugins()

        for name, plugin in enabled_plugins.items():
            try:
                provider = plugin.create_instance()
                self.providers[name] = provider
                logger.info(f"Loaded provider plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to load provider {name}: {e}")

        logger.info(f"Loaded {len(self.providers)} provider plugins")

    def get_provider(self, provider_id: str) -> Optional[BaseProvider]:
        """Get provider instance by ID (checks custom providers first)"""
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return custom_registry.get_provider(provider_id)
        
        return self.providers.get(provider_id)

    def get_api_key(self, provider_id: str, model_id: str = None) -> Optional[str]:
        """Get API key for a provider"""
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return custom_registry.get_api_key(provider_id, model_id)
        
        provider = self.providers.get(provider_id)
        if provider:
            return provider.get_api_key(model_id)
        return None

    def get_model_string(self, provider_id: str, model_id: str) -> str:
        """Get model string for CrewAI"""
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return custom_registry.get_model_string(provider_id, model_id)
        
        provider = self.providers.get(provider_id)
        if provider:
            return provider.get_model_string(model_id)
        return f"{provider_id}/{model_id}"

    def get_base_url(self, provider_id: str) -> Optional[str]:
        """Get base URL for OpenAI-compatible providers.
        
        Returns None for providers natively supported by LiteLLM.
        Returns the API base URL for OpenAI-compatible providers.
        """
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return custom_registry.get_base_url(provider_id)
        
        provider = self.providers.get(provider_id)
        if provider:
            return provider.get_base_url()
        return None

    def is_provider_configured(self, provider_id: str) -> bool:
        """Check if a provider is properly configured"""
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return True  # Custom providers are always "configured" if they exist
        
        provider = self.providers.get(provider_id)
        return provider is not None and provider.is_configured()

    def get_configured_providers(self) -> Dict[str, BaseProvider]:
        """Get all configured providers (including custom)"""
        result = {pid: provider for pid, provider in self.providers.items() if provider.is_configured()}
        
        # Add custom providers
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        for provider in custom_registry.get_all_providers():
            result[provider.provider_id] = provider
        
        return result

    def get_available_providers(self) -> Dict[str, BaseProvider]:
        """Get all available providers (whether configured or not)"""
        result = self.providers.copy()
        
        # Add custom providers
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        for provider in custom_registry.get_all_providers():
            result[provider.provider_id] = provider
        
        return result

    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all plugins"""
        return plugin_manager.get_plugin_info()

    def reload_plugins(self):
        """Reload all plugins (useful for development)"""
        logger.info("Reloading provider plugins...")
        self.providers.clear()
        plugin_manager.plugins.clear()
        self._load_plugins()
    
    def reload_custom_providers(self):
        """Reload custom providers from database"""
        from .custom import reload_custom_providers
        reload_custom_providers()


# Global provider registry - now plugin-based
provider_registry = PluginProviderRegistry()