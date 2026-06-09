from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class GoogleProvider(BaseProvider):
    """Google provider implementation"""

    def __init__(self):
        super().__init__('google')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        api_key = (os.getenv('GOOGLE_GENERATIVE_AI_API_KEY') or
                  os.getenv('GEMINI_API_KEY') or
                  config.get('models.google_generative_ai_api_key') or
                  config.get('models.gemini_api_key'))
        if not api_key or api_key == 'your_google_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"google/{model_id}"