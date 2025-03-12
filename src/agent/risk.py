from agent.registry import AgentKey
from flow.schema import FundState, Signal
from flow.prompt import RISK_PROMPT
from util.logger import logger
from flow.state import make_decision
from ingestion.api import get_price_data
from typing import Dict, Any

# Risk Thresholds
thresholds = {
    "position_factor_lt": 0.15,
    "position_factor_gt": 0.25, 
}

##### Ticker Risk Agent #####
def risk_agent(state: FundState):
    """Analyzes risk factors for the target ticker based on the portfolio."""
    agent_name = AgentKey.RISK
    portfolio = state["portfolio"]
    end_date = state["end_date"]
    ticker = state["ticker"]

    logger.log_agent_status(agent_name, ticker, "Analyzing risk based on portfolio")

    prices_df = get_price_data(ticker=ticker, end_date=end_date)
    if not prices_df:
        return state

    ticker_risk = risk_analysis(portfolio, prices_df, ticker)

    logger.log_agent_status(agent_name, ticker, "Done")

    return {"risk_data": {ticker: ticker_risk}}

def risk_analysis(portfolio, prices_df, ticker) -> Dict[str, Any]:
    #  Calculate portfolio value
    latest_price = prices_df["close"].iloc[-1]

    # Calculate current position value for this ticker
    current_position_value = portfolio["positions"][ticker].shares * latest_price

    # Calculate total portfolio value using stored prices
    total_portfolio_value = portfolio["cashflow"]+ sum(portfolio["positions"][t].value for t in portfolio["positions"])

    # Base limit is 20% of portfolio for any single position
    position_limit = total_portfolio_value * thresholds["position_factor_gt"]

    # For existing positions, subtract current position value from limit
    remaining_position_limit = position_limit - current_position_value

    # Calculate position factor
    position_factor = current_position_value / total_portfolio_value
    if position_factor < thresholds["position_factor_lt"]:
        position_factor = Signal.BULLISH
    elif position_factor > thresholds["position_factor_gt"]:
        position_factor = Signal.BEARISH
    else:
        position_factor = Signal.NEUTRAL

    ticker_risk = {
        "risk_signal": position_factor,
        "latest_price": float(latest_price),
        "current_position_value": float(current_position_value),
        "total_portfolio_value": float(total_portfolio_value),
        "remaining_position_limit": float(remaining_position_limit),
        "position_limit": float(position_limit),
    }

    return ticker_risk