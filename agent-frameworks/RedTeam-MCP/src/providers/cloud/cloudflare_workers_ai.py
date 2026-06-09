from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class CloudflareWorkersAIProvider(BaseProvider):
    """Cloudflare Workers Ai provider implementation"""

    def __init__(self):
        super().__init__('cloudflare-workers-ai')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        env_var_name = 'CLOUDFLARE_WORKERS_AI_API_KEY'
        api_key = os.getenv(env_var_name) or config.get('models.cloudflare_workers_ai_key')
        if not api_key or api_key == 'your_cloudflare_workers_ai_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"cloudflare-workers-ai/{model_id}"