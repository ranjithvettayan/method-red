from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class V0Provider(BaseProvider):
    """V0 provider implementation"""

    def __init__(self):
        super().__init__('v0')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        env_var_name = 'V0_API_KEY'
        api_key = os.getenv(env_var_name) or config.get('models.v0_key')
        if not api_key or api_key == 'your_v0_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"v0/{model_id}"