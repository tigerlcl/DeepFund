from agent.registry import AgentKey
from flow.schema import FundState, Signal
from flow.prompt import RISK_PROMPT
from util.logger import logger
from util.agent_helper import make_decision
from ingestion.api import get_price_data
from typing import Dict, Any

# Risk Thresholds
thresholds = {
    "position_factor_lt": 0.15,
    "position_factor_gt": 0.25, 
}

def _risk_analysis(portfolio, prices_df, ticker) -> Dict[str, Any]:
    #  Calculate portfolio value
    latest_price = prices_df["close"].iloc[-1]

    # Calculate current position value for this ticker
    estimated_position_value = portfolio["positions"][ticker].shares * latest_price

    # Calculate total portfolio value using stored prices
    total_portfolio_value = portfolio["cashflow"]+ sum(portfolio["positions"][t].value for t in portfolio["positions"])

    position_factor = estimated_position_value / total_portfolio_value
    if position_factor < thresholds["position_factor_lt"]:
        position_factor = Signal.BULLISH
    elif position_factor > thresholds["position_factor_gt"]:
        position_factor = Signal.BEARISH
    else:
        position_factor = Signal.NEUTRAL

    ticker_risk = {
        "risk_signal": position_factor,
        "latest_price": float(latest_price),
        "estimated_position_value": float(estimated_position_value),
        "portfolio_value": float(total_portfolio_value),
        "available_cash": float(portfolio["cashflow"]),
    }

    return ticker_risk

##### Ticker Risk Agent #####
def risk_agent(state: FundState):
    """Analyzes risk factors for the target ticker based on the portfolio."""
    agent_name = AgentKey.RISK
    portfolio = state["portfolio"]
    end_date = state["end_date"]
    ticker = state["ticker"]
    llm_config = state["llm_config"]

    logger.log_agent_status(agent_name, ticker, "Analyzing price data")

    prices_df = get_price_data(
        ticker=ticker,
        end_date=end_date,
    )

    if not prices_df:
        return state

    ticker_risk = _risk_analysis(portfolio, prices_df, ticker)

    prompt = RISK_PROMPT.format(
        ticker=ticker,
        analysis=ticker_risk,
    )
    # Get LLM decision
    decision = make_decision(
        prompt=prompt, 
        llm_config=llm_config, 
        agent_name=agent_name, 
        ticker=ticker)

    logger.log_agent_status(agent_name, ticker, "Done")
    return {"agent_decisions": decision}