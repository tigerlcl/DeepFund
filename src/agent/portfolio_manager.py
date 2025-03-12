import json
from agent.registry import AgentKey 
from flow.workflow import FundState
from util.logger import logger
from flow.state import make_decision, search_decision
from flow.prompt import PORTFOLIO_PROMPT

def portfolio_agent(state: FundState):
    """Makes final trading decisions and generates orders"""

    agent_name = AgentKey.PORTFOLIO
    portfolio = state["portfolio"]
    analyst_decisions = state["agent_decisions"]
    tickers = state["tickers"]
    llm_config = state["llm_config"]

    logger.log_agent_status(agent_name, None, "Analyzing signals")

    # Get position limits, current prices, and signals for every ticker
    position_limits = {}
    current_prices = {}
    max_shares = {}
    signals_by_ticker = {}

    all_decisions = []
    for ticker in tickers:
        logger.log_agent_status(agent_name, ticker, "Processing analyst signals")

        # Get position limit and current price for the ticker
        risk_data = search_decision(analyst_decisions, AgentKey.RISK, ticker)
        position_limits[ticker] = risk_data.get("remaining_position_limit", 0)
        current_prices[ticker] = risk_data.get("current_price", 0)

        # Calculate maximum shares allowed based on position limit and price
        if current_prices[ticker] > 0:
            max_shares[ticker] = int(position_limits[ticker] / current_prices[ticker])
        else:
            max_shares[ticker] = 0

        # Get signals for the ticker
        ticker_signals = {}
        for agent, signals in analyst_decisions.items():
            if agent != AgentKey.RISK and ticker in signals:
                ticker_signals[agent] = {"signal": signals[ticker]["signal"], "confidence": signals[ticker]["confidence"]}
        signals_by_ticker[ticker] = ticker_signals

        logger.log_agent_status(agent_name, ticker, "Making trading decisions")

        # make prompt
        prompt = PORTFOLIO_PROMPT.format(
            signals_by_ticker=signals_by_ticker,
            current_prices=current_prices,
            max_shares=max_shares,
            portfolio_cash=portfolio["cashflow"],
            portfolio_positions=portfolio["positions"]
        )

        # Generate the trading decision
        ticker_decision = make_decision(
            prompt=prompt,
            llm_config=llm_config,
            agent_name=agent_name,
            ticker=ticker
        )
        all_decisions.append(ticker_decision)

    logger.log_agent_status(agent_name, None, "Done")

    return {"final_decisions": all_decisions}