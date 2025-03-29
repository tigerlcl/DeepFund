from graph.constants import AgentKey
from graph.prompt import INSIDER_PROMPT
from graph.schema import FundState, AnalystSignal
from llm.inference import agent_call
from apis import AlphaVantageAPI
from database.helper import db
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
    portfolio_id = state["portfolio"].id

    logger.log_agent_status(agent_name, ticker, "Fetching insider trades")
    
    # Get the insider trades
    av_api = AlphaVantageAPI()
    insider_trades = av_api.get_insider_trades(
        ticker=ticker,
        limit=thresholds["num_trades"],
    )
    if not insider_trades:
        return state

    insider_trades_str = "\n".join([
        f"""Transaction Date: {trade.transaction_date} | Executive: {trade.executive} | Title: {trade.executive_title} | Security Type: {trade.security_type} | Acquisition(A)/Disposal(D): {trade.acquisition_or_disposal} | Shares: {trade.shares} | Share Price: {trade.share_price}\n"""
        for trade in insider_trades
    ])

    # Analyze insider trading signal via LLM
    prompt = INSIDER_PROMPT.format(num_trades=thresholds["num_trades"],trades=insider_trades_str)

    signal = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=AnalystSignal
    )

    # save signal
    logger.log_signal(agent_name, ticker, signal)
    db.save_signal(portfolio_id, agent_name, ticker, prompt, signal)
    
    return {"analyst_signals": [signal]}


