from typing import List
from graph.constants import AgentKey, Signal
from graph.prompt import PORTFOLIO_PROMPT
from graph.schema import Decision, FundState
from llm.inference import agent_call
from apis.router import Router, APISource
from database.helper import db
from util.logger import logger

# Portfolio Manager Thresholds
thresholds = {
    "position_factor_gt": 0.25, 
}

def portfolio_agent(state: FundState):
    """Makes final trading decisions and generates orders"""
    agent_name = AgentKey.PORTFOLIO
    portfolio = state["portfolio"]
    ticker = state["ticker"]
    exp_name = state["exp_name"]
    analyst_signals = state["analyst_signals"]
    llm_config = state["llm_config"]

    # Get price data
    router = Router(APISource.YFINANCE)
    current_price = router.get_us_stock_last_close_price(ticker=ticker)
    if current_price is None:
        return {"decision": Decision(ticker=ticker)}
    
    current_shares, remaining_shares = calculate_ticker_shares(portfolio, current_price, ticker)

    # Get decision memory
    decision_memory = db.get_decision_memory(exp_name, ticker)

    logger.log_agent_status(agent_name, ticker, "Making trading decisions")

    # make prompt
    prompt = PORTFOLIO_PROMPT.format(
        decision_memory=decision_memory,
        ticker_signals=signal_to_prompt(analyst_signals),
        current_price=current_price,
        current_shares=current_shares,
        remaining_shares=remaining_shares,
    )

    # Generate the trading decision
    ticker_decision = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=Decision
    )

    # save decision
    logger.log_decision(ticker, ticker_decision)
    db.save_decision(portfolio.id, ticker, prompt, ticker_decision)

    return {"decision": ticker_decision}


def calculate_ticker_shares(portfolio, current_price, ticker) -> float:
    """calculate the remaining shares allowed for purchases for a given ticker based on portfolio composition"""

    # Get current position value (0 if no position exists)
    current_position_value = 0
    current_shares = 0 
    if ticker in portfolio.positions:
        current_shares = portfolio.positions[ticker].shares
        current_position_value = current_shares * current_price
    total_portfolio_value = portfolio.cashflow + sum(portfolio.positions[t].value for t in portfolio.positions)
    
    # single ticker position should be less than 25% of total portfolio value
    position_limit = total_portfolio_value * thresholds["position_factor_gt"]
    remaining_position_limit = position_limit - current_position_value
    # round down to the nearest integer
    remaining_shares = remaining_position_limit // current_price
    if remaining_shares < 1:
        remaining_shares = 0
        
    return current_shares, remaining_shares
    

def signal_to_prompt(signals: List[Signal]) -> str:
    """Converts a list of signals to a string for the portfolio manager prompt"""
    return "\n".join([f"{s.signal}: {s.justification}" for s in signals])