import argparse
from typing import Dict, Any
from dotenv import load_dotenv
from graph.workflow import AgentWorkflow
from util.config import ConfigParser
from util.logger import logger
from util.db_helper import db_initialize, get_db

# Load environment variables from .env file
load_dotenv()

def load_portfolio(cfg: Dict[str, Any], db):
    """Load or initialize portfolio based on experiment configuration."""
    config_id = db.get_config_id_by_name(cfg["exp_name"])
    if not config_id:
        logger.info(f"Creating new config for {cfg['exp_name']}")
        config_id = db.create_config(cfg)
        if not config_id:
            raise RuntimeError(f"Failed to create config for {cfg['exp_name']}")
    
    # validate config
    db_config = db.get_config(config_id)
    if db_config and any([
        db_config["llm_provider"] != cfg["llm"]["provider"],
        db_config["llm_model"] != cfg["llm"]["model"]
    ]):
        raise RuntimeError(
            f"Config mismatch for {cfg['exp_name']}. Please use a different experiment name for different configurations."
        )

    portfolio = db.get_latest_portfolio(config_id)    
    if portfolio:
        return config_id, portfolio
    
    # Create new portfolio if it doesn't exist
    logger.info(f"Creating new portfolio for config {cfg['exp_name']}")
    portfolio_id = db.create_portfolio(
        config_id=config_id,
        cashflow=cfg["cashflow"]
    )
    if not portfolio_id:
        raise RuntimeError(f"Failed to create portfolio for config {cfg['exp_name']}")
        
    # Get the newly created portfolio
    portfolio = db.get_latest_portfolio(config_id)
    if not portfolio:
        raise RuntimeError(f"Failed to load newly created portfolio for config {cfg['exp_name']}")
    
    return config_id, portfolio

def main():
    """Main entry point for the DeepFund multi-agent system."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the deep fund trading system")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to configuration file"
    )
    parser.add_argument(
        "--local-db", action="store_true", help="Use local SQLite database"
    )
    args = parser.parse_args()
    cfg = ConfigParser(args).get_config()

    # Initialize the global database connection based on the local-db flag
    db_initialize(use_local_db=args.local_db)
    db = get_db()

    logger.info(f"Loading portfolio for {cfg['exp_name']}")
    
    try:
        config_id, portfolio = load_portfolio(cfg, db)
        logger.log_portfolio("Initial Portfolio", portfolio)

        logger.info("Init DeepFund and run")
        app = AgentWorkflow(cfg, portfolio)
        new_portfolio = app.run()
        logger.log_portfolio("Final Portfolio", new_portfolio)
        
        logger.info("Updating portfolio to Database")
        db.update_portfolio(config_id, new_portfolio)
        logger.info("DeepFund run completed")
                        
    except Exception as e:
        logger.error(f"Error during portfolio operations: {e}")
        raise


if __name__ == "__main__":
    main()
