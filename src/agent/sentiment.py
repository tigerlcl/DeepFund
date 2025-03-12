from agent.registry import AgentKey
from flow.schema import FundState, Signal
from flow.prompt import SENTIMENT_PROMPT
from util.logger import logger
from flow.state import make_decision
from ingestion.api import get_insider_trades, get_company_news
import pandas as pd
import numpy as np
from typing import Dict, Any

##### Sentiment Agent #####
def _analyze_sentiment(insider_trades, company_news) -> Dict[str, Any]:
    """Analyze sentiment from insider trades and news."""
    # Get the signals from the insider trades
    transaction_shares = pd.Series([t.transaction_shares for t in insider_trades]).dropna()
    insider_signals = np.where(transaction_shares < 0, Signal.BEARISH, Signal.BULLISH).tolist()

    # Get the sentiment from the company news
    sentiment = pd.Series([n.sentiment for n in company_news]).dropna()
    news_signals = np.where(sentiment == "negative", Signal.BEARISH, 
                          np.where(sentiment == "positive", Signal.BULLISH, Signal.NEUTRAL)).tolist()
    
    # Combine signals from both sources with weights
    insider_weight = 0.3
    news_weight = 0.7
    
    # Calculate weighted signal counts
    bullish_signals = (
        insider_signals.count(Signal.BULLISH) * insider_weight +
        news_signals.count(Signal.BULLISH) * news_weight
    )
    bearish_signals = (
        insider_signals.count(Signal.BEARISH) * insider_weight +
        news_signals.count(Signal.BEARISH) * news_weight
    )

    return {
        "insider_sentiment": insider_signals,
        "news_sentiment": news_signals,
        "bullish_weight": float(bullish_signals),
        "bearish_weight": float(bearish_signals)
    }

def sentiment_agent(state: FundState):
    """Analyzes market sentiment and generates trading signals."""
    agent_name = AgentKey.SENTIMENT
    end_date = state["end_date"]
    ticker = state["ticker"]
    llm_config = state["llm_config"]

    logger.log_agent_status(agent_name, ticker, "Fetching insider trades")
    
    # Get the insider trades
    insider_trades = get_insider_trades(
        ticker=ticker,
        end_date=end_date,
        limit=1000,
    )

    if not insider_trades:
        return state

    logger.log_agent_status(agent_name, ticker, "Fetching company news")
    
    # Get the company news
    company_news = get_company_news(ticker, end_date, limit=100)
    
    if not company_news:
        return state

    # Analyze sentiment
    sentiment_analysis = _analyze_sentiment(insider_trades, company_news)
    
    # Make prompt
    prompt = SENTIMENT_PROMPT.format(
        ticker=ticker,
        analysis=sentiment_analysis
    )

    # Get LLM decision
    decision = make_decision(
        prompt=prompt,
        llm_config=llm_config,
        agent_name=agent_name,
        ticker=ticker
    )

    logger.log_agent_status(agent_name, ticker, "Done")
    return {"agent_decisions": decision}
