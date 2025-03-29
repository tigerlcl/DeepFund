import json
from util.logger import logger
from graph.schema import Portfolio, Position

class DataLoader:
    """
    DataLoader class for portfolio
    """
    def __init__(self):
        self.local_path = "asset/local_portfolio.json"

    def load_local_portfolio(self) -> Portfolio:
        """Load portfolio from JSON file and convert to Pydantic model."""
        try:
            with open(self.local_path, 'r') as f:
                logger.info(f"Loading portfolio from local")
                data = json.load(f)
                
                # Convert positions dict from JSON to Position objects
                data["positions"] = {k: Position(**v) if isinstance(v, dict) else v 
                                    for k, v in data["positions"].items()}
                
                # Create and return a Pydantic model instance
                return Portfolio(**data)
        except FileNotFoundError:
            raise ValueError(f"Portfolio file not found: {self.local_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing portfolio file: {e}")
        

    def save_local_portfolio(self, portfolio: Portfolio):
        """Save Pydantic portfolio model to JSON file."""
        try:
            # Convert Pydantic model to dict
            portfolio_dict = portfolio.model_dump()
            
            with open(self.local_path, 'w') as f:
                json.dump(portfolio_dict, f, indent=4)
                logger.info(f"Portfolio saved to {self.local_path}")
        except Exception as e:
            raise ValueError(f"Error saving portfolio file: {e}")
        

