from graph.schema import FundState, AnalystSignal
from graph.constants import Signal, AgentKey
from graph.prompt import FUNDAMENTAL_PROMPT
from graph.state import agent_call
from apis.api import get_financial_metrics
from util.logger import logger


# Fundamental Thresholds
thresholds = {
    "profitability": {
        "return_on_equity": 0.15,
        "net_margin": 0.20,
        "operating_margin": 0.15
    },
    "growth": {
        "revenue_growth": 0.10,
        "earnings_growth": 0.10,
        "book_value_growth": 0.10
    },
    "financial_health": {
        "current_ratio": 1.5,
        "debt_to_equity": 0.5,
        "fcf_to_eps_ratio": 0.8
    },
    "price_ratios": {
        "pe_ratio": 25,
        "pb_ratio": 3,
        "ps_ratio": 5
    }
}


def fundamental_agent(state: FundState):
    """Fundamental analysis specialist focusing on company financial health and valuation."""
    agent_name = AgentKey.FUNDAMENTAL
    end_date = state["end_date"]
    ticker = state["ticker"]
    llm_config = state["llm_config"]

    logger.log_agent_status(agent_name, ticker, "Fetching financial metrics")

    # Get the financial metrics
    financial_metrics = get_financial_metrics(ticker=ticker,end_date=end_date)
    if not financial_metrics:
        logger.error(f"Failed to fetch financial metrics for {ticker}")
        return state

    # Pull the most recent metrics and thresholds
    metrics = financial_metrics[0]
    
    # Run analysis
    signal_results = {
        "profitability": analyze_profitability(metrics, thresholds["profitability"]),
        "growth": analyze_growth(metrics, thresholds["growth"]),
        "financial_health": analyze_financial_health(metrics, thresholds["financial_health"]),
        "price_ratios": analyze_price_ratios(metrics, thresholds["price_ratios"])
    }
    
    # Make prompt
    prompt = FUNDAMENTAL_PROMPT.format(
        analysis=signal_results,
    )
    
    # Get LLM signal
    signal = agent_call(
        prompt=prompt, 
        llm_config=llm_config, 
        pydantic_model=AnalystSignal)
    
    logger.log_signal(agent_name, ticker, signal)
    
    return {"analyst_signals": [signal]}


def analyze_profitability(metrics, params):
    """Analyze company profitability metrics."""
    score = sum(
        metric > threshold for metric, threshold in [
            (metrics.return_on_equity, params["return_on_equity"]),
            (metrics.net_margin, params["net_margin"]),
            (metrics.operating_margin, params["operating_margin"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL


def analyze_growth(metrics, params):
    """Analyze company growth metrics."""
    score = sum(
        metric > threshold for metric, threshold in [
            (metrics.revenue_growth, params["revenue_growth"]),
            (metrics.earnings_growth, params["earnings_growth"]),
            (metrics.book_value_growth, params["book_value_growth"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL


def analyze_financial_health(metrics, params):
    """Analyze company financial health metrics."""
    score = 0
    if metrics.current_ratio and metrics.current_ratio > params["current_ratio"]:
        score += 1
    if metrics.debt_to_equity and metrics.debt_to_equity < params["debt_to_equity"]:
        score += 1
    if (metrics.free_cash_flow_per_share and metrics.earnings_per_share and 
        metrics.free_cash_flow_per_share > metrics.earnings_per_share * params["fcf_to_eps_ratio"]):
        score += 1
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL


def analyze_price_ratios(metrics, params):
    """Analyze company price ratio metrics."""
    score = sum(
        metric < threshold for metric, threshold in [
            (metrics.price_to_earnings_ratio, params["pe_ratio"]),
            (metrics.price_to_book_ratio, params["pb_ratio"]),
            (metrics.price_to_sales_ratio, params["ps_ratio"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL


