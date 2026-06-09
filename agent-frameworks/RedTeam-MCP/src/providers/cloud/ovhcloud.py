from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class OvhcloudProvider(BaseProvider):
    """Ovhcloud provider implementation - OpenAI-compatible API"""

    def __init__(self):
        super().__init__('ovhcloud')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        env_var_name = 'OVHCLOUD_API_KEY'
        api_key = os.getenv(env_var_name) or config.get('models.ovhcloud_key')
        if not api_key or api_key == 'your_ovhcloud_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"openai/{model_id}"

    def get_base_url(self) -> Optional[str]:
        return "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"