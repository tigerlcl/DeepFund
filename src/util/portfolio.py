# Portfolio Loading and Saving

import json
from util.logger import logger
from flow.schema import Portfolio as PortfolioModel, Position

class Portfolio:
    def __init__(self):
        self.local_path = "config/local_portfolio.json"

    def load_local_portfolio(self) -> PortfolioModel:
        """Load portfolio from JSON file and convert to Pydantic model."""
        try:
            with open(self.local_path, 'r') as f:
                logger.info(f"Loading portfolio from local")
                data = json.load(f)
                
                # Convert positions dict from JSON to Position objects
                if "positions" in data and isinstance(data["positions"], list):
                    # If positions is a list in JSON, convert to dict
                    positions_dict = {}
                    for position in data["positions"]:
                        if isinstance(position, dict) and "ticker" in position:
                            ticker = position.pop("ticker")
                            positions_dict[ticker] = Position(**position)
                    data["positions"] = positions_dict
                elif "positions" in data and isinstance(data["positions"], dict):
                    # If positions is already a dict, convert values to Position objects
                    data["positions"] = {k: Position(**v) if isinstance(v, dict) else v 
                                        for k, v in data["positions"].items()}
                
                # Create and return a Pydantic model instance
                return PortfolioModel(**data)
        except FileNotFoundError:
            raise ValueError(f"Portfolio file not found: {self.local_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing portfolio file: {e}")
        

    def save_local_portfolio(self, portfolio: PortfolioModel):
        """Save Pydantic portfolio model to JSON file."""
        try:
            # Convert Pydantic model to dict
            portfolio_dict = portfolio.model_dump()
            
            with open(self.local_path, 'w') as f:
                json.dump(portfolio_dict, f, indent=4)
                logger.info(f"Portfolio saved to {self.local_path}")
        except Exception as e:
            raise ValueError(f"Error saving portfolio file: {e}")
        
    def load_api_portfolio(self):
        """Load portfolio from API."""
        pass
    
    def save_api_portfolio(self, portfolio: PortfolioModel):
        """Save portfolio to API."""
        pass