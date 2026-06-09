from typing import Optional
import os
from src.providers.base import BaseProvider
from src.config import config


class GithubModelsProvider(BaseProvider):
    """Github Models provider implementation - OpenAI-compatible API"""

    def __init__(self):
        super().__init__('github-models')

    def get_api_key(self, model_id: str = None) -> Optional[str]:
        env_var_name = 'GITHUB_TOKEN'
        api_key = os.getenv(env_var_name) or config.get('models.github_models_key')
        if not api_key or api_key == 'your_github_models_key_here':
            return None
        return api_key

    def get_model_string(self, model_id: str) -> str:
        return f"openai/{model_id}"

    def get_base_url(self) -> Optional[str]:
        return "https://models.github.ai/inference"