from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class AnthropicProvider(BaseProvider):
    """Anthropic provider implementation"""

    def __init__(self):
        super().__init__('anthropic')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        api_key = os.getenv('ANTHROPIC_API_KEY') or config.get('models.anthropic_key')
        if not api_key or api_key == 'your_anthropic_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"anthropic/{model_id}"