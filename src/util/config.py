import os
import yaml
from datetime import datetime, timedelta
from util.logger import logger
from typing import Dict, Any

class ConfigParser:
    """Manages configuration loading and validation."""

    def __init__(self, args):
        """Initialize the configuration manager."""
        self.config_path = f"config/{args.config}"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                logger.info(f"Loading configuration from {self.config_path}")
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {e}")

    def get_config(self) -> Dict[str, Any]:
        """Get the configuration."""
        return self.config
