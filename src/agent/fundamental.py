from typing import Dict, Any
from flow.schema import FundState, Signal
from flow.prompt import FUNDAMENTAL_PROMPT
from ingestion.api import get_financial_metrics
from util.logger import logger
from flow.state import make_decision
from agent.registry import AgentKey


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
    """
    Analyzes fundamental data and generates trading signals using an LLM.
    
    Dependencies:
        - get_financial_metrics
        - Fundamental Thresholds
        - FUNDAMENTAL_PROMPT
    """
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
        ticker=ticker,
        analysis=signal_results,
    )
    
    # Get LLM decision
    decision = make_decision(
        prompt=prompt, 
        llm_config=llm_config, 
        agent_name=agent_name, 
        ticker=ticker)
    
    logger.log_agent_status(agent_name, ticker, "Done")
    return {"analyst_decisions": [decision]}


def analyze_profitability(metrics: Dict[str, Any], params: Dict[str, float]) -> Signal:
    """Analyze company profitability metrics."""
    score = sum(
        metric > threshold for metric, threshold in [
            (metrics.get("return_on_equity", 0), params["return_on_equity"]),
            (metrics.get("net_margin", 0), params["net_margin"]),
            (metrics.get("operating_margin", 0), params["operating_margin"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL


def analyze_growth(metrics: Dict[str, Any], params: Dict[str, float]) -> Signal:
    """Analyze company growth metrics."""
    score = sum(
        metric > threshold for metric, threshold in [
            (metrics.get("revenue_growth", 0), params["revenue_growth"]),
            (metrics.get("earnings_growth", 0), params["earnings_growth"]),
            (metrics.get("book_value_growth", 0), params["book_value_growth"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL


def analyze_financial_health(metrics: Dict[str, Any], params: Dict[str, float]) -> Signal:
    """Analyze company financial health metrics."""
    score = 0
    if metrics.get("current_ratio") and metrics["current_ratio"] > params["current_ratio"]:
        score += 1
    if metrics.get("debt_to_equity") and metrics["debt_to_equity"] < params["debt_to_equity"]:
        score += 1
    if (metrics.get("free_cash_flow_per_share") and metrics.get("earnings_per_share") and 
        metrics["free_cash_flow_per_share"] > metrics["earnings_per_share"] * params["fcf_to_eps_ratio"]):
        score += 1
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL


def analyze_price_ratios(metrics: Dict[str, Any], params: Dict[str, float]) -> Signal:
    """Analyze company price ratio metrics."""
    score = sum(
        metric < threshold for metric, threshold in [
            (metrics.get("price_to_earnings_ratio", float('inf')), params["pe_ratio"]),
            (metrics.get("price_to_book_ratio", float('inf')), params["pb_ratio"]),
            (metrics.get("price_to_sales_ratio", float('inf')), params["ps_ratio"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL


