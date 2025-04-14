from graph.schema import FundState, AnalystSignal
from graph.constants import AgentKey
from util.db_helper import get_db
from util.logger import logger
from apis.router import Router, APISource
from llm.prompt import SOCIAL_MEDIA_PROMPT
from llm.inference import agent_call

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

    logger.log_agent_status(agent_name, ticker, "Fetching social media sentiment")
    
    # Get social media sentiment
    router = Router(APISource.TWITTER)
    try:
        twitter_posts = router.get_twitter_posts(ticker, thresholds["social_media_post_count"])
    except Exception as e:
        logger.error(f"Failed to fetch social media sentiment: {e}")
        return state
    
    if not twitter_posts:
        logger.error(f"Failed to fetch sentiment analysis")
        return state
    
    # Extract only content and platform from posts
    posts_data = []
    for post in twitter_posts:
        posts_data.append({
            "platform": post.platform,
            "content": post.content
        })
    
    sentiment_data = {
        "social_media": {
            "posts_data": posts_data,
            "total_posts": len(twitter_posts)
        }
    }

    prompt = SOCIAL_MEDIA_PROMPT.format(
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

