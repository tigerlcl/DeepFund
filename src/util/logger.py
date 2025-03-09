import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any


class DeepFundLogger:
    """Logger for the Deep Fund application."""

    def __init__(self, log_dict: Dict[str, Any]):
        """Initialize the logger.
        
        Args:
            log_dict: Dictionary containing log configuration.
        """
        self.log_dir = log_dict['log_dir']
        self.log_level = self._get_log_level(log_dict['log_level'])
        self.file_prefix = log_dict['file_prefix']
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("deep_fund")
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers if any
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create file handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"{self.file_prefix}_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(self.log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Store agent status
        self.agent_status: Dict[str, Dict[str, str]] = {}

    def _get_log_level(self, level_str: str) -> int:
        """Convert string log level to logging level."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(level_str.upper(), logging.INFO)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)

    def update_agent_status(self, agent_name: str, ticker: Optional[str] = None, status: str = ""):
        """Update the status of an agent and log it."""
        if agent_name not in self.agent_status:
            self.agent_status[agent_name] = {"status": "", "ticker": None}

        if ticker:
            self.agent_status[agent_name]["ticker"] = ticker
        if status:
            self.agent_status[agent_name]["status"] = status

        # Log the status update
        log_message = f"Agent: {agent_name}"
        if ticker:
            log_message += f" | Ticker: {ticker}"
        if status:
            log_message += f" | Status: {status}"
        
        self.info(log_message)

    def log_reasoning(self, output: Any, agent_name: str) -> None:
            """
            Log agent reasoning to the logger.
            
            Args:
                output: The output to log
                agent_name: The name of the agent
            """
            self.info(f"Agent reasoning from {agent_name}")
            
            serializable_output = self._convert_to_serializable(output)
            
            if isinstance(serializable_output, (dict, list)):
                self.debug(json.dumps(serializable_output, indent=2))
            else:
                try:
                    # Parse the string as JSON and pretty print it
                    parsed_output = json.loads(serializable_output)
                    self.debug(json.dumps(parsed_output, indent=2))
                except (json.JSONDecodeError, TypeError):
                    # Fallback to original string if not valid JSON
                    self.debug(serializable_output)
        

    def _convert_to_serializable(self, obj: Any) -> Any:
        """Convert an object to a JSON-serializable format."""
        if hasattr(obj, "to_dict"):  # Handle Pandas Series/DataFrame
            return obj.to_dict()
        elif hasattr(obj, "__dict__"):  # Handle custom objects
            return obj.__dict__
        elif isinstance(obj, (int, float, bool, str)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        else:
            return str(obj)  # Fallback to string representation 