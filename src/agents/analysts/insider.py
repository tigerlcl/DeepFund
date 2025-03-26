import pandas as pd
import numpy as np

from graph.constants import Signal, AgentKey
from graph.prompt import INSIDER_PROMPT
from graph.schema import FundState, AnalystSignal
from llm.inference import agent_call
from apis.hub import get_insider_trades
from util.logger import logger


# thresholds
thresholds = {
    "insider_limit": 100,
}


def insider_agent(state: FundState):
    """Insider trading specialist analyzing insider activity patterns."""
    agent_name = AgentKey.INSIDER
    end_date = state["end_date"]
    ticker = state["ticker"]
    llm_config = state["llm_config"]

    logger.log_agent_status(agent_name, ticker, "Fetching insider trades")
    
    # Get the insider trades
    insider_trades = get_insider_trades(
        ticker=ticker,
        end_date=end_date,
        limit=thresholds["insider_limit"],
    )

    if not insider_trades:
        return state

    # Analyze insider trading patterns
    insider_analysis = analyze_insider_trades(insider_trades)
    
    # Make prompt
    prompt = INSIDER_PROMPT.format(
        ticker=ticker,
        analysis=insider_analysis
    )

    # Get LLM signal
    signal = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=AnalystSignal
    )

    logger.log_signal(agent_name, ticker, signal)
    
    return {"analyst_signals": [signal]}


def analyze_insider_trades(insider_trades):
    """Analyze patterns from insider trades."""
    # Get the signals from the insider trades
    transaction_shares = pd.Series([t.transaction_shares for t in insider_trades]).dropna()
    insider_signals = np.where(transaction_shares < 0, Signal.BEARISH, Signal.BULLISH).tolist()
    
    pos_insider_signals = insider_signals.count(Signal.BULLISH)
    neg_insider_signals = insider_signals.count(Signal.BEARISH)

    if pos_insider_signals > neg_insider_signals:
        overall_signal = Signal.BULLISH
    elif neg_insider_signals > pos_insider_signals:
        overall_signal = Signal.BEARISH
    else:
        overall_signal = Signal.NEUTRAL

    return {
        "positive_insider": pos_insider_signals,
        "negative_insider": neg_insider_signals,
        "overall_signal": overall_signal
    }
