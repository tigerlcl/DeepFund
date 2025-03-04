import os
import yaml
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Any, Optional


class ConfigManager:
    """Manages configuration loading and validation."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default.
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "default_config.yaml"
        )

        self.config = self._load_config()
        self.ticker_scopes = self._load_ticker_scopes()
        self._validate_and_normalize_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def _load_ticker_scopes(self) -> Dict[str, List[str]]:
        """Load ticker scopes from tailor-made JSON file."""
        try:
            with open('tickers.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading ticker scopes: {e}")
            return {"default": []}

    def _validate_and_normalize_config(self) -> None:
        """Validate and normalize configuration values."""
        # Set default dates if not provided
        if not self.config.get('trading', {}).get('end_date'):
            self.config.setdefault('trading', {})['end_date'] = datetime.now().strftime("%Y-%m-%d")
        
        if not self.config.get('trading', {}).get('start_date'):
            end_date_obj = datetime.strptime(self.config['trading']['end_date'], "%Y-%m-%d")
            self.config['trading']['start_date'] = (
                end_date_obj - relativedelta(months=3)
            ).strftime("%Y-%m-%d")
        
        # Load tickers from the specified scope
        ticker_scope = self.config.get('trading', {}).get('ticker_scope', 'default')
        if ticker_scope in self.ticker_scopes:
            self.config.setdefault('trading', {})['tickers'] = self.ticker_scopes[ticker_scope]
        else:
            # If scope not found, use default or empty list
            self.config.setdefault('trading', {})['tickers'] = self.ticker_scopes.get('default', [])
            print(f"Warning: Ticker scope '{ticker_scope}' not found, using default scope")
            
        # Ensure tickers are properly formatted
        if isinstance(self.config.get('trading', {}).get('tickers'), list):
            self.config['trading']['tickers'] = [
                ticker.strip() for ticker in self.config['trading']['tickers']
            ]
            
        # Ensure logging directory exists
        log_dir = self.config.get('logging', {}).get('log_dir', 'logs')
        os.makedirs(log_dir, exist_ok=True)

    def get_config(self) -> Dict[str, Any]:
        """Get the full configuration."""
        return self.config

    def get_portfolio_config(self) -> Dict[str, Any]:
        """Get portfolio configuration."""
        return self.config.get('portfolio', {})

    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading configuration."""
        return self.config.get('trading', {})

    def get_analysts_config(self) -> List[str]:
        """Get analysts."""
        return self.config.get('analysts', {})

    def get_llm_config(self) -> Dict[str, str]:
        """Get LLM configuration."""
        return self.config.get('llm', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config.get('logging', {})