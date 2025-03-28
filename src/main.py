import argparse
from dotenv import load_dotenv

from graph.workflow import AgentWorkflow
from util.config import ConfigParser
from util.logger import logger
from util.data_loader import DataLoader

# Load environment variables from .env file
load_dotenv()

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

    # load portfolio
    dataloader = DataLoader()
    portfolio = dataloader.load_local_portfolio()
    logger.log_portfolio("Initial Portfolio", portfolio)

    logger.info("Init DeepFund and run")
    app = AgentWorkflow(cfg, portfolio)
    new_portfolio = app.run()
    logger.log_portfolio("Final Portfolio", new_portfolio)
    
    # logger.info("DeepFund run completed, update portfolio")
    # dataloader.save_local_portfolio(new_portfolio)


if __name__ == "__main__":
    main()
