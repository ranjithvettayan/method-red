import os
import logging
import logging.config
from typing import Dict, Any, Optional, List
from pathlib import Path

# YAML configuration support
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("python-dotenv not available, .env file will not be loaded")


def setup_logging(log_level: str = "INFO", log_file: str = "agent.log"):
    """Setup comprehensive logging configuration"""
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "simple": {"format": "%(levelname)s - %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": log_file,
                "mode": "a",
            },
        },
        "root": {"level": log_level, "handlers": ["console", "file"]},
        "loggers": {
            "agent": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(log_config)


class ConfigManager:
    """Advanced configuration management with YAML and environment variable support"""

    def __init__(self, config_file: str = "config/config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file and environment variables"""
        config = {}

        # Load YAML config if available
        if YAML_AVAILABLE and Path(self.config_file).exists():
            try:
                with open(self.config_file, "r") as f:
                    config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config file {self.config_file}: {e}")

        # Override with environment variables
        env_config = self._load_env_config()
        # Merge environment config, but preserve YAML structure for complex sections
        for key, value in env_config.items():
            if key == "agents" and key in config:
                # Merge agents section instead of replacing
                config[key].update(value)
            else:
                config[key] = value

        # Set defaults
        config.setdefault("api", {})
        config["api"].setdefault("host", "0.0.0.0")
        config["api"].setdefault("port", 8000)
        config["api"].setdefault("rate_limit", "100/minute")
        config["api"].setdefault("cost_limit", 10.0)  # $10 per hour
        config["api"].setdefault("max_request_size", 1048576)  # 1MB

        config.setdefault("logging", {})
        config["logging"].setdefault("level", "INFO")
        config["logging"].setdefault("file", "agent.log")

        config.setdefault("models", {})
        config["models"].setdefault("default", "claude-3-haiku-20240307")

        config.setdefault("agents", {})
        config["agents"].setdefault("default_role", "Assistant")
        config["agents"].setdefault(
            "default_goal",
            "Help users with their requests using advanced AI capabilities",
        )
        config["agents"].setdefault(
            "default_backstory",
            "A versatile AI assistant capable of handling various tasks with access to multiple AI models",
        )

        return config

    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_config = {}

        # API settings
        env_config["api"] = {
            "host": os.getenv("API_HOST", "0.0.0.0"),
            "port": int(os.getenv("API_PORT", "8000")),
            "rate_limit": os.getenv("API_RATE_LIMIT", "100/minute"),
            "cost_limit": float(os.getenv("API_COST_LIMIT", "10.0")),
            "max_request_size": int(os.getenv("MAX_REQUEST_SIZE", "1048576")),
        }

        # Logging settings
        env_config["logging"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "file": os.getenv("LOG_FILE", "agent.log"),
        }

        # Model settings - API keys for all providers
        env_config["models"] = {
            "default": os.getenv("MODEL_ID", "claude-3-haiku-20240307"),
            # Anthropic
            "anthropic_key": os.getenv("ANTHROPIC_API_KEY"),
            # OpenAI
            "openai_key": os.getenv("OPENAI_API_KEY"),
            # Google
            "google_generative_ai_api_key": os.getenv("GOOGLE_GENERATIVE_AI_API_KEY"),
            "gemini_api_key": os.getenv("GEMINI_API_KEY"),
            # Groq
            "groq_key": os.getenv("GROQ_API_KEY"),
            # Mistral
            "mistral_key": os.getenv("MISTRAL_API_KEY"),
            # Cohere
            "cohere_key": os.getenv("COHERE_API_KEY"),
            # Together AI
            "together_key": os.getenv("TOGETHER_API_KEY"),
            # Fireworks AI
            "fireworks_key": os.getenv("FIREWORKS_API_KEY"),
            # DeepSeek
            "deepseek_key": os.getenv("DEEPSEEK_API_KEY"),
            # Moonshot AI
            "moonshot_key": os.getenv("MOONSHOT_API_KEY"),
            # Zhipu AI
            "zhipu_key": os.getenv("ZHIPU_API_KEY"),
            # Minimax
            "minimax_key": os.getenv("MINIMAX_API_KEY"),
            # SiliconFlow
            "siliconflow_key": os.getenv("SILICONFLOW_API_KEY"),
            # Cerebras
            "cerebras_key": os.getenv("CEREBRAS_API_KEY"),
            # Nebius
            "nebius_key": os.getenv("NEBIUS_API_KEY"),
            # Upstage
            "upstage_key": os.getenv("UPSTAGE_API_KEY"),
            # Perplexity
            "perplexity_key": os.getenv("PERPLEXITY_API_KEY"),
            # Scaleway
            "scaleway_key": os.getenv("SCALEWAY_API_KEY"),
            # OVHcloud
            "ovhcloud_key": os.getenv("OVHCLOUD_API_KEY"),
            # Azure
            "azure_key": os.getenv("AZURE_API_KEY"),
            "azure_endpoint": os.getenv("AZURE_ENDPOINT"),
            # GitHub
            "github_token": os.getenv("GITHUB_TOKEN"),
            # HuggingFace
            "huggingface_key": os.getenv("HUGGINGFACE_API_KEY"),
        }

        # Agent settings - only override specific values, preserve YAML structure
        if "agents" not in env_config:
            env_config["agents"] = {}
        env_config["agents"]["default_role"] = os.getenv(
            "AGENT_ROLE", env_config["agents"].get("default_role", "Assistant")
        )
        env_config["agents"]["default_goal"] = os.getenv(
            "AGENT_GOAL",
            env_config["agents"].get(
                "default_goal",
                "Help users with their requests using advanced AI capabilities",
            ),
        )
        env_config["agents"]["default_backstory"] = os.getenv(
            "AGENT_BACKSTORY",
            env_config["agents"].get(
                "default_backstory",
                "A versatile AI assistant capable of handling various tasks with access to multiple AI models",
            ),
        )

        return env_config

    def get(self, key: str, default=None):
        """Get configuration value using dot notation (e.g., 'api.host')"""
        keys = key.split(".")
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value

    def get_predefined_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined agents from configuration"""
        agents = self.get("agents.predefined", [])
        result = {}
        if isinstance(agents, list):
            for agent in agents:
                if isinstance(agent, dict) and "id" in agent:
                    result[agent["id"]] = agent
        return result

    def get_teams(self) -> Dict[str, Dict[str, Any]]:
        """Get agent teams from configuration"""
        teams = self.get("agents.teams", [])
        result = {}
        if isinstance(teams, list):
            for team in teams:
                if isinstance(team, dict) and "id" in team:
                    result[team["id"]] = team
        return result

    def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific team by ID"""
        teams = self.get_teams()
        return teams.get(team_id)

    def get_team_agents(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all agent configurations for a team"""
        team = self.get_team(team_id)
        if not team:
            return []
        
        agent_ids = team.get("agents", [])
        predefined_agents = self.get_predefined_agents()
        
        return [
            predefined_agents[agent_id]
            for agent_id in agent_ids
            if agent_id in predefined_agents
        ]

    def save(self):
        """Save current configuration to YAML file"""
        if YAML_AVAILABLE:
            try:
                with open(self.config_file, "w") as f:
                    yaml.dump(self.config, f, default_flow_style=False)
                logger.info(f"Configuration saved to {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to save config file: {e}")

    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()
        logger.info(f"Configuration reloaded from {self.config_file}")


# Global configuration manager
config = ConfigManager()
