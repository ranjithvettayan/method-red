from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class GroqProvider(BaseProvider):
    """Groq provider implementation"""

    def __init__(self):
        super().__init__('groq')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        api_key = os.getenv('GROQ_API_KEY') or config.get('models.groq_key')
        if not api_key or api_key == 'your_groq_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"groq/{model_id}"