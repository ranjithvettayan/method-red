from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class BasetenProvider(BaseProvider):
    """Baseten provider implementation - OpenAI-compatible API"""

    def __init__(self):
        super().__init__('baseten')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        env_var_name = 'BASETEN_API_KEY'
        api_key = os.getenv(env_var_name) or config.get('models.baseten_key')
        if not api_key or api_key == 'your_baseten_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"openai/{model_id}"

    def get_base_url(self) -> Optional[str]:
        return "https://inference.baseten.co/v1"