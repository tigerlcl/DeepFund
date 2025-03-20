import json
from util.logger import logger
from graph.schema import Portfolio as PortfolioModel, Position

class DataLoader:
    """
    DataLoader class for portfolio and ticker data processing.
    """
    def __init__(self, ticker_scope: str):
        self.local_path = "config/local_portfolio.json"
        self.ticker_pool_path =  "config/tickers.json"
        self.ticker_scope = ticker_scope

        # Load ticker pool
        try:
            with open(self.ticker_pool_path, 'r') as f:
                self.ticker_pool = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading ticker pool: {e}")


    def load_local_portfolio(self) -> PortfolioModel:
        """Load portfolio from JSON file and convert to Pydantic model."""
        try:
            with open(self.local_path, 'r') as f:
                logger.info(f"Loading portfolio from local")
                data = json.load(f)
                
                # Convert positions dict from JSON to Position objects
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

    def get_tickers(self, ticker_scope: str = 'test'):
        """Load tickers from the specified scope. Default to test scope."""

        if ticker_scope not in self.ticker_pool:
            logger.warning(f"Ticker scope not found, using default")

        tickers = self.ticker_pool.get(ticker_scope)

        return tickers

