import json
from agent.registry import AgentKey 
from flow.workflow import FundState
from util.logger import logger
from flow.state import make_decision
from flow.prompt import PORTFOLIO_PROMPT

def portfolio_agent(state: FundState):
    """Makes final trading decisions and generates orders"""

    agent_name = AgentKey.PORTFOLIO
    portfolio = state["portfolio"]
    tickers = state["tickers"]
    analyst_decisions = state["analyst_decisions"]
    risk_data = state["risk_data"]
    llm_config = state["llm_config"]

    logger.log_agent_status(agent_name, None, "Analyzing signals")

    # Aggregate signals by ticker
    signals_by_ticker = {}
    for decision in analyst_decisions:
        signals_by_ticker[decision.ticker] = {
            "agent_name": decision.agent_name,
            "signal": decision.action, 
            "confidence": decision.confidence, 
            "justification": decision.justification
        }

    all_decisions = []
    for ticker in tickers:
        # Get position limits, current prices, and signals for every ticker

        logger.log_agent_status(agent_name, ticker, "Processing analyst signals")

        # Get position limit and current price from Risk Agent
        position_limit = risk_data[ticker].get("position_limit", 0)
        current_price = risk_data[ticker].get("latest_price", 0)

        # Calculate maximum shares allowed based on position limit and price
        if current_price > 0:
            max_shares = int(position_limit / current_price)
        else:
            max_shares = 0

        ticker_positions = portfolio["positions"][ticker]

        logger.log_agent_status(agent_name, ticker, "Making trading decisions")

        # make prompt
        prompt = PORTFOLIO_PROMPT.format(
            ticker_signals=signals_by_ticker[ticker],
            current_price=current_price,
            max_shares=max_shares,
            portfolio_cash=portfolio["cashflow"],
            ticker_positions=ticker_positions
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