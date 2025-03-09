import json
import argparse
from time import perf_counter
from dotenv import load_dotenv

from flow.workflow import AgentWorkflow
from util import ConfigManager, DeepFundLogger

# Load environment variables from .env file
load_dotenv()

def main():
    """Main entry point for the deep fund CLI."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the deep fund trading system")
    parser.add_argument(
        "--config", type=str, 
        default="../config/default_config.yaml",
        help="Path to configuration file"
    )
    args = parser.parse_args()
    
    # Load configuration
    cfg = ConfigManager(args.config)
    # set logger
    logger = DeepFundLogger(log_dict=cfg.config['log'])
    logger.info("Initializing DeepFund")
    
    # Create workflow
    workflow = AgentWorkflow(cfg)
    agent = workflow.compile()
    

    start_date =  cfg.config['trading']['start_date']
    end_date =  cfg.config['trading']['end_date']
    logger.info(f"Date range: {start_date} to {end_date}")

    # Initialize portfolio
    tickers =   cfg.config['trading']['tickers']
    init_portfolio = {
        "cash": cfg.config['portfolio']['initial_cash'],
        "margin_requirement":   cfg.config['portfolio']['margin_requirement'],
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
        
    
    start_time = perf_counter()
    try:
        logger.info("Invoking agent workflow")
        final_state = agent.invoke(
            {
                "data": {
                    "tickers": tickers,
                    "portfolio": init_portfolio,
                    "start_date": start_date,
                    "end_date": end_date,
                    "analyst_signals": {},
                },
                "metadata": {
                    "model_name":   cfg.config['llm']['model'],
                    "model_provider":   cfg.config['llm']['provider'],
                },
            },
        )
        
        logger.info("Agent workflow completed successfully")

    except Exception as e:
        logger.error(f"Error running deep fund: {str(e)}")
        raise

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
