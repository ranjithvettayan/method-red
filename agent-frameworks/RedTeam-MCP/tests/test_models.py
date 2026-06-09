#!/usr/bin/env python3
"""
Unit tests for model selector functionality
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.models import ModelSelector


class TestModelSelector:
    """Test cases for ModelSelector class"""

    def test_init_loads_models(self):
        """Test that ModelSelector loads models on initialization"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku-20240307': {'name': 'Claude 3 Haiku'}
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            assert selector.models_data is not None
            assert 'anthropic' in selector.models_data

    def test_load_models_failure(self):
        """Test handling of failed model loading"""
        with patch('src.models.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            selector = ModelSelector()
            assert selector.models_data == {}

    def test_get_model_info_found(self):
        """Test getting model info for existing model"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku-20240307': {'name': 'Claude 3 Haiku'}
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            model_info = selector.get_model_info('claude-3-haiku-20240307')

            assert model_info is not None
            assert model_info['provider'] == 'anthropic'
            assert model_info['provider_name'] == 'Anthropic'
            assert model_info['model']['name'] == 'Claude 3 Haiku'

    def test_get_model_info_not_found(self):
        """Test getting model info for non-existent model"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku-20240307': {'name': 'Claude 3 Haiku'}
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            model_info = selector.get_model_info('nonexistent-model')

            assert model_info is None

    def test_get_model_info_no_data(self):
        """Test getting model info when no data is loaded"""
        with patch('src.models.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            selector = ModelSelector()
            model_info = selector.get_model_info('any-model')

            assert model_info is None

    def test_list_available_models(self):
        """Test listing all available models"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            test_data = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku-20240307': {'name': 'Claude 3 Haiku'}
                    }
                },
                'openai': {
                    'name': 'OpenAI',
                    'models': {
                        'gpt-4': {'name': 'GPT-4'}
                    }
                }
            }
            mock_response.json.return_value = test_data
            mock_get.return_value = mock_response

            selector = ModelSelector()
            models = selector.list_available_models()

            assert models == test_data

    def test_list_available_models_empty(self):
        """Test listing models when no data is available"""
        with patch('src.models.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            selector = ModelSelector()
            models = selector.list_available_models()

            assert models == {}

    def test_get_provider_models(self):
        """Test getting models for a specific provider"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku-20240307': {'name': 'Claude 3 Haiku'},
                        'claude-3-sonnet-20240229': {'name': 'Claude 3 Sonnet'}
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            provider_models = selector.get_provider_models('anthropic')

            expected_models = {
                'claude-3-haiku-20240307': {'name': 'Claude 3 Haiku'},
                'claude-3-sonnet-20240229': {'name': 'Claude 3 Sonnet'}
            }
            assert provider_models == expected_models

    def test_get_provider_models_not_found(self):
        """Test getting models for non-existent provider"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku-20240307': {'name': 'Claude 3 Haiku'}
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            provider_models = selector.get_provider_models('nonexistent')

            assert provider_models == {}

    def test_get_provider_models_no_data(self):
        """Test getting provider models when no data is loaded"""
        with patch('src.models.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            selector = ModelSelector()
            provider_models = selector.get_provider_models('anthropic')

            assert provider_models == {}

    def test_get_model_constraints(self):
        """Test getting model constraints from models.dev data"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku-20240307': {
                            'name': 'Claude 3 Haiku',
                            'temperature': True,
                            'reasoning': False,
                            'tool_call': True,
                            'limit': {
                                'context': 200000,
                                'output': 4096
                            }
                        }
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            constraints = selector.get_model_constraints('claude-3-haiku-20240307')

            assert constraints['context_length'] == 200000
            assert constraints['max_output'] == 4096
            assert constraints['supports_temperature'] is True
            assert constraints['supports_reasoning'] is False
            assert constraints['tool_call'] is True

    def test_get_model_constraints_not_found(self):
        """Test getting constraints for non-existent model returns defaults"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {}
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            constraints = selector.get_model_constraints('nonexistent-model')

            # Should return sensible defaults
            assert constraints['context_length'] == 128000
            assert constraints['max_output'] == 8192
            assert constraints['supports_temperature'] is True
            assert constraints['supports_reasoning'] is False

    def test_validate_and_adjust_params_temperature_not_supported(self):
        """Test that temperature is ignored when model doesn't support it"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'openai': {
                    'name': 'OpenAI',
                    'models': {
                        'o1': {
                            'name': 'o1',
                            'temperature': False,  # o1 doesn't support temperature
                            'reasoning': True,
                            'limit': {'context': 200000, 'output': 100000}
                        }
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            result = selector.validate_and_adjust_params(
                model_id='o1',
                temperature=0.7
            )

            assert 'temperature' not in result['params']
            assert len(result['warnings']) == 1
            assert 'does not support temperature' in result['warnings'][0]

    def test_validate_and_adjust_params_max_tokens_capped(self):
        """Test that max_tokens is capped at model's max output"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku': {
                            'name': 'Claude 3 Haiku',
                            'temperature': True,
                            'limit': {'context': 200000, 'output': 4096}
                        }
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            result = selector.validate_and_adjust_params(
                model_id='claude-3-haiku',
                max_tokens=10000  # Exceeds model's max output
            )

            assert result['params']['max_tokens'] == 4096  # Capped
            assert len(result['warnings']) == 1
            assert 'exceeds model limit' in result['warnings'][0]

    def test_validate_and_adjust_params_reasoning_not_supported(self):
        """Test that reasoning_effort is ignored for non-reasoning models"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'anthropic': {
                    'name': 'Anthropic',
                    'models': {
                        'claude-3-haiku': {
                            'name': 'Claude 3 Haiku',
                            'reasoning': False,
                            'limit': {'context': 200000, 'output': 4096}
                        }
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            result = selector.validate_and_adjust_params(
                model_id='claude-3-haiku',
                reasoning_effort='high'
            )

            assert 'reasoning_effort' not in result['params']
            assert len(result['warnings']) == 1
            assert 'does not support reasoning' in result['warnings'][0]

    def test_validate_and_adjust_params_all_valid(self):
        """Test that all valid params are passed through"""
        with patch('src.models.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'openai': {
                    'name': 'OpenAI',
                    'models': {
                        'o3-mini': {
                            'name': 'o3 mini',
                            'temperature': True,
                            'reasoning': True,
                            'limit': {'context': 200000, 'output': 100000}
                        }
                    }
                }
            }
            mock_get.return_value = mock_response

            selector = ModelSelector()
            result = selector.validate_and_adjust_params(
                model_id='o3-mini',
                temperature=0.5,
                max_tokens=8000,
                reasoning_effort='medium'
            )

            assert result['params']['temperature'] == 0.5
            assert result['params']['max_tokens'] == 8000
            assert result['params']['reasoning_effort'] == 'medium'
            assert len(result['warnings']) == 0


if __name__ == "__main__":
    pytest.main([__file__])