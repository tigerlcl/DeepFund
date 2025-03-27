from typing import Dict, Any, List
from graph.constants import AgentKey, Signal
from graph.prompt import PORTFOLIO_PROMPT
from graph.schema import Decision, Position, FundState
from llm.inference import agent_call
from apis import YFinanceAPI
from util.logger import logger

def portfolio_agent(state: FundState):
    """Makes final trading decisions and generates orders"""
    agent_name = AgentKey.PORTFOLIO
    portfolio = state["portfolio"]
    ticker = state["ticker"]
    analyst_signals = state["analyst_signals"]
    llm_config = state["llm_config"]

    # Aggregate signals by ticker
    logger.log_agent_status(agent_name, ticker, "Analyzing ticker risk")

    # Get price data and analyze risk
    yf_api = YFinanceAPI()
    current_price = yf_api.get_last_close_price(ticker=ticker)
    if current_price is None:
        return {"decision": Decision(ticker=ticker)}
    
    risk_data = analyze_ticker_risk(portfolio, current_price, ticker)
    position_limit = risk_data["position_limit"]

    # Calculate maximum shares allowed based on position limit and price
    max_shares = int(position_limit / current_price) if current_price > 0 else 0
    ticker_positions = portfolio.positions.get(ticker, Position(shares=0, value=0))

    logger.log_agent_status(agent_name, ticker, "Making trading decisions")

    # make prompt
    prompt = PORTFOLIO_PROMPT.format(
        ticker_signals=signal_to_prompt(analyst_signals),
        current_price=current_price,
        max_shares=max_shares,
        portfolio_cash=portfolio.cashflow,
        ticker_positions=ticker_positions
    )

    # Generate the trading decision
    ticker_decision = agent_call(
        prompt=prompt,
        config=llm_config,
        pydantic_model=Decision
    )

    logger.log_decision(ticker, ticker_decision)

    return {"decision": ticker_decision, "trading_price": current_price}


def analyze_ticker_risk(portfolio,latest_price, ticker) -> Dict[str, Any]:
    """Analyzes risk factors for a given ticker based on portfolio composition"""

    # Risk Thresholds
    thresholds = {
        "position_factor_lt": 0.15,
        "position_factor_gt": 0.25, 
    }

    # Get current position value (0 if no position exists)
    current_position_value = 0
    if ticker in portfolio.positions:
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

def signal_to_prompt(signals: List[Signal]) -> str:
    """Converts a list of signals to a string for the portfolio manager prompt"""
    return "\n".join([f"{s.signal}: {s.justification}" for s in signals])