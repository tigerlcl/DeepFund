import pandas as pd
import numpy as np
from graph.schema import FundState, AnalystSignal
from graph.constants import Signal, AgentKey
from graph.prompt import SENTIMENT_PROMPT
from graph.state import agent_call
from apis.api import get_insider_trades, get_company_news
from util.logger import logger


# thresholds
thresholds = {
    "insider_limit": 100,
    "news_limit": 100,
    "insider_weight": 0.3,
    "news_weight": 0.7,
}

# TODO: Enhance sentiment analysis
def sentiment_agent(state: FundState):
    """Market sentiment specialist analyzing insider activity and news sentiment."""
    agent_name = AgentKey.SENTIMENT
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

    logger.log_agent_status(agent_name, ticker, "Fetching company news")
    
    # Get the company news
    company_news = get_company_news(
        ticker=ticker,
        end_date=end_date,
        limit=thresholds["news_limit"]
    )
    
    if not company_news:
        return state

    # Analyze sentiment
    sentiment_analysis = analyze_sentiment(insider_trades, company_news, thresholds)
    
    # Make prompt
    prompt = SENTIMENT_PROMPT.format(
        ticker=ticker,
        analysis=sentiment_analysis
    )

    # Get LLM signal
    signal = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=AnalystSignal
    )

    logger.log_signal(agent_name, ticker, signal)
    
    return {"analyst_signals": [signal]}


def analyze_sentiment(insider_trades, company_news, params):
    """Analyze sentiment from insider trades and news."""
    # Get the signals from the insider trades
    transaction_shares = pd.Series([t.transaction_shares for t in insider_trades]).dropna()
    insider_signals = np.where(transaction_shares < 0, Signal.BEARISH, Signal.BULLISH).tolist()

    # Get the sentiment from the company news
    sentiment = pd.Series([n.sentiment for n in company_news]).dropna()
    news_signals = np.where(sentiment == "negative", Signal.BEARISH, 
                          np.where(sentiment == "positive", Signal.BULLISH, Signal.NEUTRAL)).tolist()
    
    pos_news_signals = news_signals.count(Signal.BULLISH)
    neg_news_signals = news_signals.count(Signal.BEARISH)

    pos_insider_signals = insider_signals.count(Signal.BULLISH)
    neg_insider_signals = insider_signals.count(Signal.BEARISH)

    # Combine signals from both sources with weights
    insider_weight = params["insider_weight"]
    news_weight = params["news_weight"]
    
    # Calculate weighted signal counts
    bullish_signals = (
        pos_insider_signals * insider_weight +
        pos_news_signals * news_weight
    )
    bearish_signals = (
        neg_insider_signals * insider_weight +
        neg_news_signals * news_weight
    )

    if bullish_signals > bearish_signals:
        overall_signal = Signal.BULLISH
    elif bearish_signals > bullish_signals:
        overall_signal = Signal.BEARISH
    else:
        overall_signal = Signal.NEUTRAL

    return {
        "positive_insider": pos_insider_signals,
        "negative_insider": neg_insider_signals,
        "positive_news": pos_news_signals,
        "negative_news": neg_news_signals,
        "overall_signal": overall_signal
    }
