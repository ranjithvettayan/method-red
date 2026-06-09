from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class GoogleVertexProvider(BaseProvider):
    """Google Vertex provider implementation"""

    def __init__(self):
        super().__init__('google-vertex')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        env_var_name = 'GOOGLE_VERTEX_API_KEY'
        api_key = os.getenv(env_var_name) or config.get('models.google_vertex_key')
        if not api_key or api_key == 'your_google_vertex_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"google-vertex/{model_id}"