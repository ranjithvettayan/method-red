from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os

from src.config import config


class BaseProvider(ABC):
    """Base class for all LLM providers"""

    def __init__(self, provider_id: str):
        self.provider_id = provider_id

    @abstractmethod
    def get_api_key(self, model_id: str = None) -> Optional[str]:
        """Get API key for this provider"""
        pass

    @abstractmethod
    def get_model_string(self, model_id: str) -> str:
        """Get the model string for CrewAI/LiteLLM.
        
        For providers natively supported by LiteLLM, return format like:
            - 'anthropic/claude-3-opus' 
            - 'groq/llama-3.1-70b'
            
        For OpenAI-compatible providers (with base_url), return format like:
            - 'openai/gpt-4' (used with base_url pointing to provider)
        """
        pass

    def get_base_url(self) -> Optional[str]:
        """Get the base URL for OpenAI-compatible API endpoints.
        
        Return None for providers natively supported by LiteLLM.
        Return the API base URL for OpenAI-compatible providers.
        
        Examples:
            - SiliconFlow: 'https://api.siliconflow.com/v1'
            - Venice: 'https://api.venice.ai/api/v1'
        """
        return None

    def is_configured(self) -> bool:
        """Check if this provider is properly configured"""
        return self.get_api_key() is not None