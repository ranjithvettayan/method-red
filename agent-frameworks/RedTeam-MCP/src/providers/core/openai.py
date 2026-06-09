from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation"""

    def __init__(self):
        super().__init__('openai')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        api_key = os.getenv('OPENAI_API_KEY') or config.get('models.openai_key')
        if not api_key or api_key == 'your_openai_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"openai/{model_id}"