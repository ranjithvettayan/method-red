from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class CohereProvider(BaseProvider):
    """Cohere provider implementation"""

    def __init__(self):
        super().__init__('cohere')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        env_var_name = 'COHERE_API_KEY'
        api_key = os.getenv(env_var_name) or config.get('models.cohere_key')
        if not api_key or api_key == 'your_cohere_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"cohere/{model_id}"