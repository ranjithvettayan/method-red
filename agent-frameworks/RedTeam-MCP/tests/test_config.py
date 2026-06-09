#!/usr/bin/env python3
"""
Unit tests for configuration management
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.config import ConfigManager, setup_logging


class TestConfigManager:
    """Test cases for ConfigManager class"""

    def test_init_default_config_file(self):
        """Test initialization with default config file"""
        config = ConfigManager()
        assert config.config_file == "config/config.yaml"
        assert 'api' in config.config
        assert 'logging' in config.config
        assert 'models' in config.config

    def test_init_custom_config_file(self):
        """Test initialization with custom config file"""
        config = ConfigManager("custom.yaml")
        assert config.config_file == "custom.yaml"

    def test_load_config_file_exists(self):
        """Test loading config when file exists"""
        yaml_content = """
api:
  host: test-host
  port: 9000
models:
  default: test-model
"""

        with patch('src.config.Path') as mock_path, \
             patch('src.config.YAML_AVAILABLE', True), \
             patch('builtins.open', mock_open(read_data=yaml_content)), \
             patch('src.config.yaml.safe_load') as mock_yaml, \
             patch('src.config.ConfigManager._load_env_config') as mock_env_config:

            mock_yaml.return_value = {'api': {'host': 'test-host', 'port': 9000}}
            mock_path.return_value.exists.return_value = True
            mock_env_config.return_value = {}  # No env overrides

            config = ConfigManager()
            # Config should merge YAML with defaults, so host should be from YAML
            assert config.config['api']['host'] == 'test-host'

    def test_load_config_file_not_exists(self):
        """Test loading config when file doesn't exist"""
        with patch('src.config.Path') as mock_path:
            mock_path.return_value.exists.return_value = False

            config = ConfigManager()
            # Should still have default values
            assert 'api' in config.config

    def test_load_env_config(self):
        """Test loading configuration from environment variables"""
        env_vars = {
            'API_HOST': 'env-host',
            'API_PORT': '8080',
            'API_RATE_LIMIT': '200/minute',
            'API_COST_LIMIT': '20.0',
            'LOG_LEVEL': 'DEBUG',
            'LOG_FILE': 'custom.log'
        }

        with patch.dict(os.environ, env_vars):
            config = ConfigManager()
            env_config = config._load_env_config()

            assert env_config['api']['host'] == 'env-host'
            assert env_config['api']['port'] == 8080
            assert env_config['api']['rate_limit'] == '200/minute'
            assert env_config['api']['cost_limit'] == 20.0

    def test_config_defaults(self):
        """Test that default configuration values are set"""
        config = ConfigManager()

        # API defaults
        assert config.config['api']['host'] == '0.0.0.0'
        assert config.config['api']['port'] == 8000
        assert config.config['api']['rate_limit'] == '100/minute'
        assert config.config['api']['cost_limit'] == 10.0

        # Logging defaults
        assert config.config['logging']['level'] == 'INFO'
        assert 'file' in config.config['logging']

        # Models defaults
        assert config.config['models']['default'] == 'claude-3-haiku-20240307'

        # Agent defaults
        assert 'default_role' in config.config['agents']
        assert 'default_goal' in config.config['agents']
        assert 'default_backstory' in config.config['agents']


class TestSetupLogging:
    """Test cases for setup_logging function"""

    def test_setup_logging_basic(self):
        """Test basic logging setup"""
        with patch('src.config.logging.config.dictConfig') as mock_dictConfig:
            setup_logging()

            # Verify dictConfig was called
            assert mock_dictConfig.called

            # Check the config structure
            call_args = mock_dictConfig.call_args[0][0]
            assert 'version' in call_args
            assert 'formatters' in call_args
            assert 'handlers' in call_args
            assert 'root' in call_args

    def test_setup_logging_with_custom_level(self):
        """Test logging setup with custom log level"""
        with patch('src.config.logging.config.dictConfig') as mock_dictConfig:
            setup_logging(log_level='DEBUG')

            call_args = mock_dictConfig.call_args[0][0]
            assert call_args['handlers']['console']['level'] == 'DEBUG'
            assert call_args['root']['level'] == 'DEBUG'

    def test_setup_logging_with_custom_file(self):
        """Test logging setup with custom log file"""
        with patch('src.config.logging.config.dictConfig') as mock_dictConfig:
            setup_logging(log_file='custom.log')

            call_args = mock_dictConfig.call_args[0][0]
            assert call_args['handlers']['file']['filename'] == 'custom.log'


if __name__ == "__main__":
    pytest.main([__file__])