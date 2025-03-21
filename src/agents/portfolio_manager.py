from graph.constants import AgentKey
from graph.workflow import FundState
from util.logger import logger
from graph.state import agent_call
from graph.prompt import PORTFOLIO_PROMPT
from graph.schema import Signal, Decision, Position
from apis.api import get_price_data
from typing import Dict, Any

# Risk Thresholds
thresholds = {
    "position_factor_lt": 0.15,
    "position_factor_gt": 0.25, 
}


def portfolio_agent(state: FundState):
    """Makes final trading decisions and generates orders"""
    agent_name = AgentKey.PORTFOLIO
    portfolio = state["portfolio"]
    ticker = state["ticker"]
    analyst_signals = state["analyst_signals"]
    start_date = state["start_date"]
    end_date = state["end_date"]
    llm_config = state["llm_config"]

    # Aggregate signals by ticker
    logger.log_agent_status(agent_name, ticker, "Analyzing ticker risk")

    # Get price data and analyze risk
    prices_df = get_price_data(ticker=ticker, start_date=start_date, end_date=end_date)
    if prices_df is None:
        return {"decision": Decision(ticker=ticker)}
    
    current_price = prices_df["close"].iloc[-1]
    risk_data = analyze_ticker_risk(portfolio, current_price, ticker)
    position_limit = risk_data["position_limit"]

    # Calculate maximum shares allowed based on position limit and price
    max_shares = int(position_limit / current_price) if current_price > 0 else 0
    ticker_positions = portfolio.positions.get(ticker, Position(shares=0, value=0))

    logger.log_agent_status(agent_name, ticker, "Making trading decisions")

    # make prompt
    prompt = PORTFOLIO_PROMPT.format(
        ticker_signals=analyst_signals,
        current_price=current_price,
        max_shares=max_shares,
        portfolio_cash=portfolio.cashflow,
        ticker_positions=ticker_positions
    )

    # Generate the trading decision
    ticker_decision = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=Decision
    )

    logger.log_decision(ticker, ticker_decision)

    return {"decision": ticker_decision, "trading_price": current_price}


def analyze_ticker_risk(portfolio,latest_price, ticker) -> Dict[str, Any]:
    """Analyzes risk factors for a given ticker based on portfolio composition"""
    current_position_value = portfolio.positions[ticker].shares * latest_price
    total_portfolio_value = portfolio.cashflow + sum(portfolio.positions[t].value for t in portfolio.positions)
    
    position_limit = total_portfolio_value * thresholds["position_factor_gt"]
    remaining_position_limit = position_limit - current_position_value
    
    position_factor = current_position_value / total_portfolio_value
    if position_factor < thresholds["position_factor_lt"]:
        position_factor = Signal.BULLISH
    elif position_factor > thresholds["position_factor_gt"]:
        position_factor = Signal.BEARISH
    else:
        position_factor = Signal.NEUTRAL
        
    return {
        "risk_signal": position_factor,
        "latest_price": float(latest_price),
        "current_position_value": float(current_position_value),
        "total_portfolio_value": float(total_portfolio_value),
        "remaining_position_limit": float(remaining_position_limit),
        "position_limit": float(position_limit),
    }