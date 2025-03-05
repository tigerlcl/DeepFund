import os
import logging
from datetime import datetime
from typing import Dict, Optional


class DeepFundLogger:
    """Logger for the Deep Fund application."""

    def __init__(self, log_dir: str, log_level: str, file_prefix: str):
        """Initialize the logger.
        
        Args:
            log_dir: Directory to store log files.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            file_prefix: Prefix for log files.
        """
        self.log_dir = log_dir
        self.log_level = self._get_log_level(log_level)
        self.file_prefix = file_prefix
        
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
