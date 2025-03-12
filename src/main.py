import argparse
from flow.workflow import AgentWorkflow
from util.config import ConfigManager
from util.logger import logger
from util.portfolio import Portfolio

from dotenv import load_dotenv

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
    cfg = ConfigManager(args.config)

    logger.info("Load Portfolio")
    portfolio_driver = Portfolio()
    portfolio = portfolio_driver.load_local_portfolio()

    logger.info("Init DeepFund and run")
    workflow = AgentWorkflow(cfg, portfolio)
    new_portfolio = workflow.run()
    
    logger.info("DeepFund run completed, update portfolio")
    portfolio_driver.save_local_portfolio(new_portfolio)


if __name__ == "__main__":
    main()
