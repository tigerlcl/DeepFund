import yaml
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from util.logger import logger
from typing import Dict, List, Any


class ConfigManager:
    """Manages configuration loading and validation."""

    def __init__(self, config_file: str):
        """Initialize the configuration manager."""
        self.config_path = f"config/{config_file}"
        self.ticker_scope_json =  "config/tickers.json"

        self.config = self._load_config()
        self.ticker_scopes = self._load_ticker_scopes()
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
            
    def _load_ticker_scopes(self) -> Dict[str, List[str]]:
        """Load ticker scopes from tailor-made JSON file."""
        try:
            with open(self.ticker_scope_json, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading ticker scopes: {e}")

    def _validate_and_normalize_config(self) -> None:
        """Validate and normalize configuration values."""
        # Set default dates if not provided
        if not self.config['trading']['end_date']:
            self.config['trading']['end_date'] = datetime.now().strftime("%Y-%m-%d")
        
        if not self.config['trading']['start_date']:
            end_date_obj = datetime.strptime(self.config['trading']['end_date'], "%Y-%m-%d")
            self.config['trading']['start_date'] = (
                end_date_obj - relativedelta(months=3)
            ).strftime("%Y-%m-%d")
        
        # Load tickers from the specified scope
        ticker_scope = self.config['trading']['ticker_scope']
        if ticker_scope in self.ticker_scopes:
            self.config['trading']['tickers'] = self.ticker_scopes.get(ticker_scope)
        else:
            # If scope not found, use test list
            logger.warning(f"Ticker scope not found: {ticker_scope}, using test scope")
            self.config['trading']['tickers'] = self.ticker_scopes.get('test')