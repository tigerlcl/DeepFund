import sys
import argparse
from time import perf_counter
from dotenv import load_dotenv
from config.config_manager import ConfigManager
from core.deep_fund import DeepFund
from core.logger import logger

# Load environment variables from .env file
load_dotenv()


def run_deep_fund(
    tickers: list[str],
    start_date: str,
    end_date: str,
    portfolio: dict,
    selected_analysts: list[str] = [],
    model_name: str = "gpt-4o",
    model_provider: str = "OpenAI",
):
    """Run the deep fund with the given parameters.
    
    Args:
        tickers: List of stock ticker symbols.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        portfolio: Portfolio configuration.
        selected_analysts: List of selected analysts.
        model_name: Name of the LLM model to use.
        model_provider: Provider of the LLM model.
        
    Returns:
        Dictionary containing trading decisions and analyst signals.
    """
    logger.info("Initializing DeepFund")
    deep_fund = DeepFund(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        portfolio=portfolio,
        show_reasoning=False,  # Always set to False for automatic workflow
        selected_analysts=selected_analysts,
        model_name=model_name,
        model_provider=model_provider,
    )
    
    logger.info("Running DeepFund")
    return deep_fund.run()


def main():
    """Main entry point for the deep fund CLI."""
    start_time = perf_counter()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the deep fund trading system")
    parser.add_argument(
        "--config", type=str, help="Path to configuration file"
    )

    args = parser.parse_args()
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    
    # Get configuration sections
    portfolio_config = config_manager.get_portfolio_config()
    trading_config = config_manager.get_trading_config()
    analysts_config = config_manager.get_analysts_config()
    llm_config = config_manager.get_llm_config()
    
    # Override tickers if provided via command line
    tickers = trading_config.get("tickers", [])
    if args.ticker:
        tickers = [ticker.strip() for ticker in args.ticker.split(",")]
    
    if not tickers:
        logger.error("No tickers specified")
        sys.exit(1)
    
    logger.info(f"Running deep fund for tickers: {', '.join(tickers)}")
    
    # Initialize portfolio
    portfolio = {
        "cash": portfolio_config.get("initial_cash", 100000.0),
        "margin_requirement": portfolio_config.get("margin_requirement", 0.0),
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
    
    # Run the deep fund
    result = run_deep_fund(
        tickers=tickers,
        start_date=trading_config.get("start_date"),
        end_date=trading_config.get("end_date"),
        portfolio=portfolio,
        selected_analysts=analysts_config,
        model_name=llm_config.get("model", "gpt-4o"),
        model_provider=llm_config.get("provider", "OpenAI"),
    )
    
    # Log the trading decisions
    logger.info(f"Trading run completed for tickers: {', '.join(tickers)}")
    for ticker, decision in result.get("decisions", {}).items():
        logger.info(f"Decision for {ticker}: {decision.get('action')} {decision.get('quantity')} shares (Confidence: {decision.get('confidence'):.1f}%)")
    
    # Print performance information
    logger.info(f"Total execution time: {perf_counter() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
