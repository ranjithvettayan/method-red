"""
Custom Provider for self-hosted LLMs (LM Studio, Ollama, etc.)

This provider handles user-defined OpenAI-compatible endpoints stored in the database.
"""

from typing import Optional, List, Dict, Any
from src.providers.base import BaseProvider


class CustomProvider(BaseProvider):
    """Provider for custom/self-hosted OpenAI-compatible endpoints"""

    def __init__(self, provider_config: Dict[str, Any]):
        """Initialize with config from database
        
        Args:
            provider_config: Dict with id, name, base_url, api_key, provider_type, etc.
        """
        super().__init__(provider_config["id"])
        self.config = provider_config
        self.name = provider_config.get("name", provider_config["id"])
        self._base_url = provider_config.get("base_url", "")
        self._api_key = provider_config.get("api_key", "")
        self.provider_type = provider_config.get("provider_type", "openai-compatible")
        self.is_enabled = provider_config.get("is_enabled", True)

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        """Get API key for this provider
        
        Many self-hosted solutions don't require an API key,
        so we return a placeholder if none is set.
        """
        if self._api_key:
            return self._api_key
        # Return a placeholder for providers that don't need auth
        return "not-required"

    def get_model_string(self, model_id: str) -> str:
        """Get the model string for CrewAI/LiteLLM.
        
        For custom OpenAI-compatible providers, we use 'openai/' prefix
        with the base_url to route correctly.
        """
        # Use openai/ prefix for OpenAI-compatible endpoints
        return f"openai/{model_id}"

    def get_base_url(self) -> Optional[str]:
        """Get the base URL for this custom provider"""
        return self._base_url if self._base_url else None

    def is_configured(self) -> bool:
        """Check if this provider is properly configured"""
        return bool(self._base_url) and self.is_enabled


class CustomProviderRegistry:
    """Registry for custom providers loaded from database"""
    
    def __init__(self):
        self._providers: Dict[str, CustomProvider] = {}
        self._models: Dict[str, Dict[str, Any]] = {}  # model_id -> model config
    
    def load_from_db(self, db):
        """Load custom providers and models from database"""
        self._providers.clear()
        self._models.clear()
        
        # Load providers
        for provider_config in db.get_custom_providers():
            if provider_config.get("is_enabled", True):
                provider = CustomProvider(provider_config)
                self._providers[provider.provider_id] = provider
        
        # Load models
        for model in db.get_custom_models():
            provider_id = model["provider_id"]
            if provider_id in self._providers:
                model_id = model["id"]
                self._models[model_id] = {
                    **model,
                    "provider": self._providers[provider_id]
                }
    
    def get_provider(self, provider_id: str) -> Optional[CustomProvider]:
        """Get a custom provider by ID"""
        return self._providers.get(provider_id)
    
    def get_all_providers(self) -> List[CustomProvider]:
        """Get all enabled custom providers"""
        return list(self._providers.values())
    
    def get_provider_ids(self) -> List[str]:
        """Get all custom provider IDs"""
        return list(self._providers.keys())
    
    def get_models_for_provider(self, provider_id: str) -> List[Dict[str, Any]]:
        """Get all models for a specific provider"""
        return [
            model for model in self._models.values()
            if model["provider_id"] == provider_id
        ]
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get a custom model by ID"""
        return self._models.get(model_id)
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all custom models"""
        return list(self._models.values())
    
    def has_provider(self, provider_id: str) -> bool:
        """Check if a provider exists"""
        return provider_id in self._providers
    
    def has_model(self, model_id: str) -> bool:
        """Check if a model exists"""
        return model_id in self._models
    
    def get_api_key(self, provider_id: str, model_id: str = None) -> Optional[str]:
        """Get API key for a provider"""
        provider = self.get_provider(provider_id)
        return provider.get_api_key(model_id) if provider else None
    
    def get_model_string(self, provider_id: str, model_id: str) -> str:
        """Get the model string for LiteLLM"""
        provider = self.get_provider(provider_id)
        if provider:
            # For custom providers, use the model_name from the model config
            model = self.get_model(model_id)
            if model:
                return provider.get_model_string(model["model_name"])
            return provider.get_model_string(model_id)
        return f"openai/{model_id}"
    
    def get_base_url(self, provider_id: str) -> Optional[str]:
        """Get base URL for a provider"""
        provider = self.get_provider(provider_id)
        return provider.get_base_url() if provider else None


# Global custom provider registry
_custom_registry: Optional[CustomProviderRegistry] = None


def get_custom_registry() -> CustomProviderRegistry:
    """Get the global custom provider registry"""
    global _custom_registry
    if _custom_registry is None:
        _custom_registry = CustomProviderRegistry()
    return _custom_registry


def reload_custom_providers():
    """Reload custom providers from database"""
    from src.db import get_db
    registry = get_custom_registry()
    registry.load_from_db(get_db())
