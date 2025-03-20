import yaml
from datetime import datetime, timedelta
from util.logger import logger
from typing import Dict, Any


class ConfigManager:
    """Manages configuration loading and validation."""

    def __init__(self, config_file: str):
        """Initialize the configuration manager."""
        self.config_path = f"config/{config_file}"

        self.config = self._load_config()
        self._validate_and_normalize_config()


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
            

    def _validate_and_normalize_config(self) -> None:
        """Validate and normalize configuration values."""
        # Set default dates if not provided
        if not self.config['trading']['end_date']:
            self.config['trading']['end_date'] = datetime.now().strftime("%Y-%m-%d")
        
        if not self.config['trading']['start_date']:
            end_date_obj = datetime.strptime(self.config['trading']['end_date'], "%Y-%m-%d")
            self.config['trading']['start_date'] = (
                end_date_obj - timedelta(days=90)  # Approximate 3 months as 90 days
            ).strftime("%Y-%m-%d")
    