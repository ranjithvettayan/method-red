from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class LmstudioProvider(BaseProvider):
    """Lmstudio provider implementation - OpenAI-compatible API"""

    def __init__(self):
        super().__init__('lmstudio')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        # LM Studio typically doesn't require an API key for local use
        env_var_name = 'LMSTUDIO_API_KEY'
        api_key = os.getenv(env_var_name) or config.get('models.lmstudio_key')
        if not api_key or api_key == 'your_lmstudio_key_here':
            # Return a placeholder for local LM Studio
            return 'lm-studio'
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"openai/{model_id}"

    def get_base_url(self) -> Optional[str]:
        return "http://127.0.0.1:1234/v1"