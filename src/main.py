import json
import argparse
from time import perf_counter
from dotenv import load_dotenv
from typing import Dict, Any

from config.config_manager import ConfigManager
from core.logger import logger
from core.factory import WorkflowFactory
from langchain_core.messages import HumanMessage

# Load environment variables from .env file
load_dotenv()

def main():
    """Main entry point for the deep fund CLI."""

    logger.info("Initializing DeepFund")

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the deep fund trading system")
    parser.add_argument(
        "--config", type=str, help="Path to configuration file"
    )
    args = parser.parse_args()
    
    # Load configuration and Run
    config_manager = ConfigManager(args.config)
    tickers = config_manager.config['trading']['tickers']

    # Initialize portfolio
    init_portfolio = {
        "cash": config_manager.config['portfolio']['initial_cash'],
        "margin_requirement": config_manager.config['portfolio']['margin_requirement'],
        "positions": {
                ticker: {
                    "long": 0,
                    "short": 0,
                    "long_cost_basis": 0.0,
                    "short_cost_basis": 0.0,
                } for ticker in tickers
            },
            "realized_gains": {
                ticker: {
                    "long": 0.0,
                    "short": 0.0,
                } for ticker in tickers
            }
        }
        
     # Create workflow
    logger.info("Creating workflow")
    workflow = WorkflowFactory.create_workflow(config_manager.config['analysts'])
    agent = workflow.compile()
    logger.info("Workflow compiled successfully")


    start_date = config_manager.config['trading']['start_date']
    end_date = config_manager.config['trading']['end_date']
    logger.info(f"Date range: {start_date} to {end_date}")
    
    start_time = perf_counter()
        
    try:
        logger.info("Invoking agent workflow")
        final_state = agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content="Make trading decisions based on the provided data.",
                    )
                ],
                "data": {
                    "tickers": tickers,
                    "portfolio": init_portfolio,
                    "start_date": start_date,
                    "end_date": end_date,
                    "analyst_signals": {},
                },
                "metadata": {
                    "model_name": config_manager.config['llm']['model'],
                    "model_provider": config_manager.config['llm']['provider'],
                },
            },
        )
        
        logger.info("Agent workflow completed successfully")

    except Exception as e:
        logger.error(f"Error running deep fund: {str(e)}")
        raise

    # Parse the response
    logger.info(f"Trading run completed for tickers: {', '.join(tickers)}")

    # Log the trading decisions
    decisions = json.loads(final_state["messages"][-1].content)
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
