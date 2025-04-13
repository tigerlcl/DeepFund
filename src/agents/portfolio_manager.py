from graph.constants import AgentKey
from llm.prompt import PORTFOLIO_PROMPT, RISK_CONTROL_PROMPT
from graph.schema import Decision, FundState, PositionRisk
from llm.inference import agent_call
from apis.router import Router, APISource
from util.db_helper import get_db
from util.logger import logger

# Portfolio Manager Thresholds
thresholds = {
    "decision_memory_limit": 5
}

def portfolio_agent(state: FundState):
    """Makes final trading decisions and generates orders"""
    agent_name = AgentKey.PORTFOLIO
    portfolio = state["portfolio"]
    ticker = state["ticker"]
    exp_name = state["exp_name"]
    trading_date = state["trading_date"]
    analyst_signals = state["analyst_signals"]
    llm_config = state["llm_config"]
    num_tickers = state["num_tickers"]

    # Get database instance
    db = get_db()

    # Get price data
    router = Router(APISource.ALPHA_VANTAGE)
    try:
        current_price = router.get_us_stock_last_close_price(ticker=ticker, trading_date=trading_date)
    except Exception as e:
        logger.error(f"Failed to fetch price data for {ticker}: {e}")
        raise RuntimeError(f"Failed to make decision")
    
    # calculate the max position ratio
    max_position_ratio = 1
    if num_tickers > 1:
        # suppose a single ticker can occupy its own base allocation (1/N) plus that of one other ticker maximally, round to the nearest 0.05
        max_position_ratio = round(2 / num_tickers * 20) / 20
    

    # risk control
    risk_prompt = RISK_CONTROL_PROMPT.format(
        ticker_signals=analyst_signals,
        portfolio=portfolio.model_dump_json(),
        max_position_ratio=max_position_ratio,

    )

    position_risk = agent_call(
        prompt=risk_prompt,
        llm_config=llm_config,
        pydantic_model=PositionRisk,
    )
    
    logger.log_agent_status(agent_name, ticker, "Risk control")
    logger.log_risk(ticker, position_risk)

    # verify the position ratio if it is in the range
    if position_risk.optimal_position_ratio > max_position_ratio:
        # too bullish, set to the max
        position_risk.optimal_position_ratio = max_position_ratio
    elif position_risk.optimal_position_ratio < 0:
        # too bearish, set to the min
        position_risk.optimal_position_ratio = 0

    logger.log_agent_status(agent_name, ticker, "Making trading decisions")

    # Get decision memory
    decision_memory = db.get_decision_memory(exp_name, ticker, thresholds["decision_memory_limit"])
    current_shares, remaining_shares = calculate_ticker_shares(portfolio, current_price, ticker, position_risk.optimal_position_ratio)

    # make trading decision
    prompt = PORTFOLIO_PROMPT.format(
        decision_memory=decision_memory,
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
    db.save_decision(portfolio.id, ticker, prompt, ticker_decision, trading_date)

    return {"decision": ticker_decision}


def calculate_ticker_shares(portfolio, current_price, ticker, optimal_position_ratio):
    """calculate the remaining shares for a given ticker based on portfolio"""

    # Get current position value (0 if no position exists)
    current_position_value = 0
    current_shares = 0 
    if ticker in portfolio.positions:
        current_shares = portfolio.positions[ticker].shares
        current_position_value = current_shares * current_price
    total_portfolio_value = portfolio.cashflow + sum(portfolio.positions[t].value for t in portfolio.positions)
    
    # single ticker position should be less than optimal_position_ratio of total portfolio value
    position_value_limit = total_portfolio_value * optimal_position_ratio
    remaining_position_limit = position_value_limit - current_position_value
    # remaining shares should not exceed the cashflow
    if remaining_position_limit < portfolio.cashflow:
        remaining_shares = int(remaining_position_limit // current_price)
    else:
        remaining_shares = int(portfolio.cashflow // current_price)
        
    return current_shares, remaining_shares

    
