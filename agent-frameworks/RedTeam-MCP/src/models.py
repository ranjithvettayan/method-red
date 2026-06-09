import requests
from typing import Dict, Any, Optional

# Models.dev API endpoint
MODELS_DEV_API = "https://models.dev/api.json"


class ModelSelector:
    """Handles model selection and provider information from models.dev"""

    def __init__(self):
        self.models_data = None
        self.load_models()

    def load_models(self):
        """Load models data from models.dev"""
        try:
            response = requests.get(MODELS_DEV_API)
            response.raise_for_status()
            self.models_data = response.json()
            print(f"Loaded {sum(len(provider['models']) for provider in self.models_data.values())} models from {len(self.models_data)} providers")
        except Exception as e:
            print(f"Failed to load models from models.dev: {e}")
            self.models_data = {}

    def get_model_info(self, model_id: str, provider_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get model information by model ID and optionally provider ID"""
        if not self.models_data:
            return None

        # If provider is specified, look there first
        if provider_id and provider_id in self.models_data:
            provider = self.models_data[provider_id]
            if model_id in provider['models']:
                model = provider['models'][model_id]
                return {
                    'provider': provider_id,
                    'model': model,
                    'provider_name': provider['name']
                }

        # Search all providers
        for pid, provider in self.models_data.items():
            if model_id in provider['models']:
                model = provider['models'][model_id]
                return {
                    'provider': pid,
                    'model': model,
                    'provider_name': provider['name']
                }
        return None

    def get_model_constraints(self, model_id: str, provider_id: Optional[str] = None) -> Dict[str, Any]:
        """Get model constraints (context length, max output, temperature support, reasoning)"""
        model_info = self.get_model_info(model_id, provider_id)
        if not model_info:
            # Return sensible defaults if model not found
            return {
                'context_length': 128000,
                'max_output': 8192,
                'supports_temperature': True,
                'supports_reasoning': False,
                'tool_call': False,
            }
        
        model = model_info.get('model', {})
        limit = model.get('limit', {})
        
        return {
            'context_length': limit.get('context', 128000),
            'max_output': limit.get('output', 8192),
            'supports_temperature': model.get('temperature', True),
            'supports_reasoning': model.get('reasoning', False),
            'tool_call': model.get('tool_call', False),
            'structured_output': model.get('structured_output', False),
        }

    def validate_and_adjust_params(
        self, 
        model_id: str, 
        provider_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Validate and adjust parameters based on model constraints.
        
        Returns a dict with validated parameters and any warnings.
        """
        constraints = self.get_model_constraints(model_id, provider_id)
        adjusted = {}
        warnings = []

        # Handle temperature
        if temperature is not None:
            if not constraints['supports_temperature']:
                warnings.append(f"Model {model_id} does not support temperature parameter, ignoring")
            else:
                adjusted['temperature'] = temperature

        # Handle max_tokens - cap at model's max output
        if max_tokens is not None:
            max_output = constraints['max_output']
            if max_tokens > max_output:
                warnings.append(f"max_tokens {max_tokens} exceeds model limit {max_output}, capping")
                adjusted['max_tokens'] = max_output
            else:
                adjusted['max_tokens'] = max_tokens

        # Handle reasoning_effort - only for reasoning models
        if reasoning_effort is not None:
            if not constraints['supports_reasoning']:
                warnings.append(f"Model {model_id} does not support reasoning, ignoring reasoning_effort")
            else:
                adjusted['reasoning_effort'] = reasoning_effort

        return {
            'params': adjusted,
            'warnings': warnings,
            'constraints': constraints,
        }

    def list_available_models(self) -> Dict[str, Any]:
        """List all available models"""
        return self.models_data or {}

    def get_provider_models(self, provider_id: str) -> Dict[str, Any]:
        """Get all models for a specific provider"""
        if not self.models_data or provider_id not in self.models_data:
            return {}
        return self.models_data[provider_id]['models']

    def get_providers(self) -> Dict[str, str]:
        """Get all available providers with their names"""
        if not self.models_data:
            return {}
        return {pid: provider['name'] for pid, provider in self.models_data.items()}


# Global model selector
model_selector = ModelSelector()