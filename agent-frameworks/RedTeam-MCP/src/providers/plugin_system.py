#!/usr/bin/env python3
"""
Plugin system for LLM providers
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Type
import pkgutil
import sys

from .base import BaseProvider

logger = logging.getLogger(__name__)


class ProviderPlugin:
    """Represents a loaded provider plugin"""

    def __init__(self, name: str, provider_class: Type[BaseProvider], metadata: Dict[str, Any]):
        self.name = name
        self.provider_class = provider_class
        self.metadata = metadata
        self.instance: Optional[BaseProvider] = None

    def create_instance(self) -> BaseProvider:
        """Create an instance of the provider"""
        if self.instance is None:
            self.instance = self.provider_class()
        return self.instance

    def is_enabled(self) -> bool:
        """Check if this plugin is enabled in configuration"""
        from src.config import config
        enabled_providers = config.get('providers.enabled', [])
        disabled_providers = config.get('providers.disabled', [])

        # If enabled list is specified, only enable those
        if enabled_providers:
            return self.name in enabled_providers

        # If disabled list is specified, enable all except those
        if disabled_providers:
            return self.name not in disabled_providers

        # Default: enable all
        return True


class PluginManager:
    """Manages provider plugins with dynamic loading"""

    def __init__(self):
        self.plugins: Dict[str, ProviderPlugin] = {}
        self.discovery_paths: List[Path] = []

    def add_discovery_path(self, path: Path):
        """Add a path to search for plugins"""
        if path not in self.discovery_paths:
            self.discovery_paths.append(path)

    def discover_plugins(self):
        """Discover and load all available plugins"""
        # Add default provider paths
        provider_root = Path(__file__).parent
        for category in ['core', 'cloud', 'chinese', 'specialized', 'research', 'routing', 'other']:
            self.add_discovery_path(provider_root / category)

        # Also add external plugin paths from config
        from src.config import config
        external_paths = config.get('providers.plugin_paths', [])
        for path_str in external_paths:
            path = Path(path_str)
            if path.exists():
                self.add_discovery_path(path)

        # Discover plugins in all paths
        for discovery_path in self.discovery_paths:
            if discovery_path.exists():
                self._discover_in_path(discovery_path)

    def _discover_in_path(self, path: Path):
        """Discover plugins in a specific path"""
        if not path.is_dir():
            return

        # Convert path to Python module path
        try:
            # Get the relative path from the src directory
            src_path = Path(__file__).parent.parent  # src/providers -> src
            relative_path = path.relative_to(src_path)

            # Convert to module path (e.g., src.providers.core)
            module_path = '.'.join(['src'] + list(relative_path.parts))

            # Import the package
            package = importlib.import_module(module_path)

            # Find all provider classes in the package
            for _, module_name, _ in pkgutil.iter_modules([str(path)]):
                try:
                    full_module_name = f'{module_path}.{module_name}'
                    module = importlib.import_module(full_module_name)

                    # Find provider classes
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and
                            issubclass(obj, BaseProvider) and
                            obj != BaseProvider):

                            # Create plugin metadata
                            metadata = {
                                'version': getattr(obj, '__version__', '1.0.0'),
                                'description': getattr(obj, '__doc__', '').strip(),
                                'author': getattr(obj, '__author__', 'Unknown'),
                                'module': full_module_name,
                                'class_name': name,
                            }

                            plugin = ProviderPlugin(module_name, obj, metadata)
                            self.plugins[module_name] = plugin
                            logger.info(f"Discovered plugin: {module_name}")

                except Exception as e:
                    logger.warning(f"Failed to load plugin {module_name}: {e}")

        except Exception as e:
            logger.warning(f"Failed to discover plugins in {path}: {e}")

    def get_plugin(self, name: str) -> Optional[ProviderPlugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)

    def get_enabled_plugins(self) -> Dict[str, ProviderPlugin]:
        """Get all enabled plugins"""
        return {name: plugin for name, plugin in self.plugins.items() if plugin.is_enabled()}

    def create_provider_instance(self, name: str) -> Optional[BaseProvider]:
        """Create a provider instance from a plugin"""
        plugin = self.get_plugin(name)
        if plugin and plugin.is_enabled():
            try:
                return plugin.create_instance()
            except Exception as e:
                logger.error(f"Failed to create provider instance for {name}: {e}")
        return None

    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all plugins"""
        return {
            name: {
                'enabled': plugin.is_enabled(),
                'metadata': plugin.metadata,
                'has_instance': plugin.instance is not None
            }
            for name, plugin in self.plugins.items()
        }


# Global plugin manager
plugin_manager = PluginManager()