import os
import argparse
from graph.workflow import AgentWorkflow
from util.config import ConfigParser
from util.dataloader import DataLoader
from util.logger import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# set working directory to the directory of the main.py file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the DeepFund multi-agent system."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the deep fund trading system")
    parser.add_argument(
        "--config", type=str, 
        default="default_config.yaml",
        help="Name of configuration file"
    )
    args = parser.parse_args()
    cfg = ConfigParser(args).get_config()

    # load portfolio and tickers
    dataloader = DataLoader()
    portfolio = dataloader.load_local_portfolio()
    tickers = dataloader.get_tickers(cfg['trading']['ticker_scope'])

    logger.info("Init DeepFund and run")
    app = AgentWorkflow(cfg, portfolio, tickers)
    new_portfolio = app.run()
    
    logger.info("DeepFund run completed, update portfolio")
    dataloader.save_local_portfolio(new_portfolio)


if __name__ == "__main__":
    main()
