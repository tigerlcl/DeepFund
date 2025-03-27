from graph.constants import AgentKey
from graph.prompt import NEWS_PROMPT
from graph.schema import FundState, AnalystSignal
from llm.inference import agent_call
from apis import YFinanceAPI
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

    logger.log_agent_status(agent_name, ticker, "Fetching company news")
    
    # Get the company news
    yf_api = YFinanceAPI()
    company_news = yf_api.get_news(query=ticker, news_count=thresholds["news_count"])
    if not company_news:
        return state

    # Analyze news sentiment via LLM
    news_str = "\n".join([
        f"""Title: {news.title} | Publisher: {news.publisher} | Publish Time: {news.publish_time}\n"""
        for news in company_news
    ])
    prompt = NEWS_PROMPT.format(news=news_str)

    # Get LLM signal
    signal = agent_call(
        prompt=prompt,
        config=llm_config,
        pydantic_model=AnalystSignal
    )

    logger.log_signal(agent_name, ticker, signal)
    
    return {"analyst_signals": [signal]}
