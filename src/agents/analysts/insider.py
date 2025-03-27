from graph.constants import Signal, AgentKey
from graph.prompt import INSIDER_PROMPT
from graph.schema import FundState, AnalystSignal
from llm.inference import agent_call
from apis.hub import APIHub, Source
from util.logger import logger

# Insider trading thresholds
thresholds = {
    "num_trades": 30,
}

def insider_agent(state: FundState):
    """Insider trading specialist analyzing insider activity patterns."""
    agent_name = AgentKey.INSIDER
    llm_config = state["llm_config"]
    ticker = state["ticker"]

    logger.log_agent_status(agent_name, ticker, "Fetching insider trades")
    
    # Get the insider trades
    fd_api = APIHub.get_api(Source.FINANCIAL_DATASET)
    insider_trades = fd_api.get_insider_trades(
        ticker=ticker,
        limit=thresholds["num_trades"],
    )

    if not insider_trades:
        return state
    
    # Filter out trades with no shares
    insider_trades = filter(lambda t: t.transaction_shares is not None, insider_trades)

    insider_trades_str = "\n".join([
        f"""Transaction Date: {trade.transaction_date} | Shares: {trade.transaction_shares} | Shares Before: {trade.shares_owned_before_transaction} | Shares After: {trade.shares_owned_after_transaction} | Security Title: {trade.security_title}\n"""
        for trade in insider_trades
    ])

    # Analyze insider trading signal via LLM
    prompt = INSIDER_PROMPT.format(
        num_trades=thresholds["num_trades"],
        trades=insider_trades_str,
    )

    signal = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=AnalystSignal
    )

    logger.log_signal(agent_name, ticker, signal)
    
    return {"analyst_signals": [signal]}


