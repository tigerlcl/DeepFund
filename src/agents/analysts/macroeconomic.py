import math
import pandas as pd
from graph.schema import FundState, AnalystSignal
from graph.constants import Signal, AgentKey
from graph.prompt import MACROECONOMIC_PROMPT
from llm.inference import agent_call
from apis.router import Router, APISource
from util.db_helper import get_db
from util.logger import logger

def macroeconomic_agent(state: FundState):
    """Macroeconomic analysis specialist focusing on economic indicators, interest rates, inflation and market trends."""
    agent_name = AgentKey.MACROECONOMIC
    ticker = state["ticker"]
    llm_config = state["llm_config"]
    portfolio_id = state["portfolio"].id

    # Get db instance
    db = get_db()

    logger.log_agent_status(agent_name, ticker, "Fetching economic indicators")

    # Get the economic indicators
    router = Router(APISource.ALPHA_VANTAGE)
    economic_indicators = router.get_economic_indicators()
    if not economic_indicators:
        logger.error(f"Failed to fetch economic indicators")
        return state
    
    prompt = MACROECONOMIC_PROMPT.format(economic_indicators=economic_indicators, ticker=ticker)
    signal = agent_call(
        prompt=prompt, 
        llm_config=llm_config, 
        pydantic_model=AnalystSignal)
    
    # save signal
    logger.log_signal(agent_name, ticker, signal)
    db.save_signal(portfolio_id, agent_name, ticker, prompt, signal)
    
    return {"analyst_signals": [signal]}