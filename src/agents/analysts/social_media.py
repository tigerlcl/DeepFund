from graph.schema import FundState, AnalystSignal
from graph.constants import AgentKey
from util.db_helper import get_db
from util.logger import logger
from apis.router import Router, APISource
from llm.prompt import SOCIAL_MEDIA_PROMPT
from llm.inference import agent_call

thresholds = {
    "tweets_count": 10
}

def social_media_agent(state: FundState):
    """Twitter Sentiment Analysis"""
    agent_name = AgentKey.SOCIAL_MEDIA
    ticker = state["ticker"]
    llm_config = state["llm_config"]
    portfolio_id = state["portfolio"].id

    logger.log_agent_status(agent_name, ticker, "Fetching social media sentiment")
    db = get_db()

    # Get social media sentiment
    router = Router(APISource.TWITTER)
    try:
        twitter_posts = router.get_twitter_posts(ticker, thresholds["tweets_count"])
    except Exception as e:
        logger.error(f"Failed to fetch social media posts: {e}")
        return state
    
    if twitter_posts is None:
        logger.error(f"No social media posts found for {ticker}")
        return state

    prompt = SOCIAL_MEDIA_PROMPT.format(
        ticker=ticker,
        posts_data=twitter_posts.model_dump_json()
    )

    signal = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=AnalystSignal,
    )

    logger.log_signal(agent_name, ticker, signal)
    db.save_signal(portfolio_id, agent_name, ticker, prompt, signal)

    return {"analyst_signals": [signal]}

