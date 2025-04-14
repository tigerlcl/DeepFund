from graph.schema import FundState, AnalystSignal
from graph.constants import AgentKey
from util.db_helper import get_db
from util.logger import logger
from apis.router import Router, APISource
from llm.prompt import SENTIMENT_PROMPT
from llm.inference import agent_call

"""
Sentiment Trend Analysis
"""

def social_media_agent(state: FundState):
    """Twitter Sentiment Analysis"""
    agent_name = AgentKey.SOCIAL_MEDIA
    ticker = state["ticker"]
    llm_config = state["llm_config"]
    portfolio_id = state["portfolio"].id

    # Get db instance
    db = get_db()

    thresholds = {
        "social_media_post_count": 10
    }

    logger.log_agent_status(agent_name, ticker, "Fetching sentiment analysis")
    
    router = Router(APISource.TWITTER)
   
    # Social media sentiment
    logger.log_agent_status(agent_name, ticker, "Fetching social media sentiment")
    social_sentiment = router.get_twitter_sentiment(ticker, thresholds["social_media_post_count"])
    
    if not social_sentiment:
        logger.error(f"Failed to fetch sentiment analysis")
        return state
    
    # Extract only content and platform from posts
    posts_data = []
    for post in social_sentiment.posts:
        posts_data.append({
            "platform": post.platform,
            "content": post.content
        })
    
    sentiment_data = {
        "social_media": {
            "posts": posts_data,
            "total_posts": social_sentiment.total_posts
        }
    }
    print(sentiment_data)  

    prompt = SENTIMENT_PROMPT.format(
        ticker=ticker,
        sentiment_analysis=sentiment_data
    )
    signal = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=AnalystSignal,
    )

    logger.log_signal(agent_name, ticker, signal)
    db.save_signal(portfolio_id, agent_name, ticker, prompt, signal)

    return {"analyst_signals": [signal]}

