import pandas as pd
import numpy as np

from graph.constants import Signal, AgentKey
from graph.prompt import NEWS_PROMPT
from graph.schema import FundState, AnalystSignal
from llm.inference import agent_call
from apis.hub import get_company_news
from util.logger import logger


# thresholds
thresholds = {
    "news_limit": 100,
}


def news_agent(state: FundState):
    """News sentiment specialist analyzing market news and media coverage."""
    agent_name = AgentKey.NEWS
    end_date = state["end_date"]
    ticker = state["ticker"]
    llm_config = state["llm_config"]

    logger.log_agent_status(agent_name, ticker, "Fetching company news")
    
    # Get the company news
    company_news = get_company_news(
        ticker=ticker,
        end_date=end_date,
        limit=thresholds["news_limit"]
    )
    
    if not company_news:
        return state

    # Analyze news sentiment
    news_analysis = analyze_news_sentiment(company_news)
    
    # Make prompt
    prompt = NEWS_PROMPT.format(
        ticker=ticker,
        analysis=news_analysis
    )

    # Get LLM signal
    signal = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=AnalystSignal
    )

    logger.log_signal(agent_name, ticker, signal)
    
    return {"analyst_signals": [signal]}


def analyze_news_sentiment(company_news):
    """Analyze sentiment from news coverage."""
    # Get the sentiment from the company news
    sentiment = pd.Series([n.sentiment for n in company_news]).dropna()
    news_signals = np.where(sentiment == "negative", Signal.BEARISH, 
                          np.where(sentiment == "positive", Signal.BULLISH, Signal.NEUTRAL)).tolist()
    
    pos_news_signals = news_signals.count(Signal.BULLISH)
    neg_news_signals = news_signals.count(Signal.BEARISH)

    if pos_news_signals > neg_news_signals:
        overall_signal = Signal.BULLISH
    elif neg_news_signals > pos_news_signals:
        overall_signal = Signal.BEARISH
    else:
        overall_signal = Signal.NEUTRAL

    return {
        "positive_news": pos_news_signals,
        "negative_news": neg_news_signals,
        "overall_signal": overall_signal
    } 