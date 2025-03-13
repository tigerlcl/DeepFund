import os
import logging
from datetime import datetime

class DeepFundLogger:
    """Logger for the Deep Fund application."""

    def __init__(self):
        """Initialize the logger.
        
        Args:
            log_dict: Dictionary containing log configuration.
        """
        self.log_dir = 'logs'
        self.log_level = 'INFO'
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("deep_fund")
        self.logger.setLevel(self.log_level)
        
        
        # Create file handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"deepfund_{timestamp}.log")
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

    def log_agent_status(self, agent_name: str, ticker: str, status: str):
        """Log the status of an agent."""
        if ticker:
            msg = f"Agent: {agent_name} | Ticker: {ticker} | Status: {status}"
        else:
            msg = f"Agent: {agent_name} | Status: {status}"

        self.info(msg)
        
# Create a global logger instance
logger = DeepFundLogger()
