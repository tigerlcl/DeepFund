import json
import argparse
from time import perf_counter
from dotenv import load_dotenv

from flow.workflow import AgentWorkflow
from flow.schema import FundState
from util.config import ConfigManager
from util.logger import logger

# Load environment variables from .env file
load_dotenv()

def main():
    """Main entry point for the deep fund CLI."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the deep fund trading system")
    parser.add_argument(
        "--config-file", type=str, 
        default="default_config.yaml",
        help="Name of configuration file"
    )
    args = parser.parse_args()
    
    logger.info("Initializing DeepFund")
    
    # Load configuration
    cfg = ConfigManager(args.config_file)

    start_time = perf_counter()
    
    # Create workflow
    workflow = AgentWorkflow(cfg)
    agent_app = workflow.build()
    
    # Initialize FundState
    init_state = FundState(
        portfolio=portfolio,
        start_date =  cfg.config['trading']['start_date'],
        end_date =  cfg.config['trading']['end_date'],
        tickers = cfg.config['trading']['tickers'],
    )
    
    try:
        logger.info("Invoking agent workflow")
        final_state = agent_app.invoke(init_state)
        logger.info("Agent workflow completed successfully")

    except Exception as e:
        logger.error(f"Error running deep fund: {str(e)}")
        raise

    # Log the trading decisions
    decisions = final_state["decisions"]
    for ticker, decision in decisions.items():
        logger.info(f"Decision for {ticker}: {decision.get('action')} {decision.get('quantity')} shares (Confidence: {decision.get('confidence'):.1f}%)")

    
    # TODO: log analyst signals
    analyst_signals = final_state["data"]["analyst_signals"]
    # for ticker, signal in analyst_signals.items():
    #     logger.info(f"Analyst signal for {ticker}: {signal}")


    # Log execution time
    execution_time = perf_counter() - start_time
    logger.info(f"Total execution time: {execution_time:.2f} seconds")
    
    logger.info("DeepFund run completed")


if __name__ == "__main__":
    main()
