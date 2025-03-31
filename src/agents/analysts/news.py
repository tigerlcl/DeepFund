from graph.constants import AgentKey
from graph.prompt import NEWS_PROMPT
from graph.schema import FundState, AnalystSignal
from llm.inference import agent_call
from apis.router import Router, APISource
from util.db_helper import db
from util.logger import logger

# thresholds
thresholds = {
    "news_count": 10,
}

def news_agent(state: FundState):
    """News sentiment specialist analyzing market news to provide a signal."""
    agent_name = AgentKey.NEWS
    ticker = state["ticker"]
    llm_config = state["llm_config"]
    portfolio_id = state["portfolio"].id
    logger.log_agent_status(agent_name, ticker, "Fetching company news")
    
    # Get the company news
    router = Router(APISource.YFINANCE)
    company_news = router.get_us_stock_news(ticker, thresholds["news_count"])
    if not company_news:
        return state

    # Analyze news sentiment via LLM
    news_dict = [m.model_dump() for m in company_news]
    prompt = NEWS_PROMPT.format(news=news_dict)

    # Get LLM signal
    signal = agent_call(
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=AnalystSignal,
    )

    # save signal
    logger.log_signal(agent_name, ticker, signal)
    db.save_signal(portfolio_id, agent_name, ticker, prompt, signal)
    
    return {"analyst_signals": [signal]}
