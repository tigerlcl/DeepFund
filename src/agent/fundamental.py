import os
import json
from typing import Dict, Any
from flow.schema import FundState, Signal
from ingestion.api import get_financial_metrics
from prompt.fundamental import FUNDAMENTAL_PROMPT
from util.logger import logger
from util.agent import make_decision


def load_thresholds() -> Dict[str, Any] | None:
    """Load threshold values from external configuration file."""
    config_path = "data/fundamental_thresholds.json"
    if not os.path.exists(config_path):
        return None
    
    with open(config_path, "r") as f:
        return json.load(f)

def _analyze_profitability(metrics: Dict[str, Any], thresholds: Dict[str, float]) -> Signal:
    """Analyze company profitability metrics."""
    score = sum(
        metric > threshold for metric, threshold in [
            (metrics.get("return_on_equity", 0), thresholds["return_on_equity"]),
            (metrics.get("net_margin", 0), thresholds["net_margin"]),
            (metrics.get("operating_margin", 0), thresholds["operating_margin"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL

def _analyze_growth(metrics: Dict[str, Any], thresholds: Dict[str, float]) -> Signal:
    """Analyze company growth metrics."""
    score = sum(
        metric > threshold for metric, threshold in [
            (metrics.get("revenue_growth", 0), thresholds["revenue_growth"]),
            (metrics.get("earnings_growth", 0), thresholds["earnings_growth"]),
            (metrics.get("book_value_growth", 0), thresholds["book_value_growth"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL

def _analyze_financial_health(metrics: Dict[str, Any], thresholds: Dict[str, float]) -> Signal:
    """Analyze company financial health metrics."""
    score = 0
    if metrics.get("current_ratio") and metrics["current_ratio"] > thresholds["current_ratio"]:
        score += 1
    if metrics.get("debt_to_equity") and metrics["debt_to_equity"] < thresholds["debt_to_equity"]:
        score += 1
    if (metrics.get("free_cash_flow_per_share") and metrics.get("earnings_per_share") and 
        metrics["free_cash_flow_per_share"] > metrics["earnings_per_share"] * thresholds["fcf_to_eps_ratio"]):
        score += 1
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL

def _analyze_price_ratios(metrics: Dict[str, Any], thresholds: Dict[str, float]) -> Signal:
    """Analyze company price ratio metrics."""
    score = sum(
        metric < threshold for metric, threshold in [
            (metrics.get("price_to_earnings_ratio", float('inf')), thresholds["pe_ratio"]),
            (metrics.get("price_to_book_ratio", float('inf')), thresholds["pb_ratio"]),
            (metrics.get("price_to_sales_ratio", float('inf')), thresholds["ps_ratio"])
        ] if metric is not None
    )
    return Signal.BULLISH if score >= 2 else Signal.BEARISH if score == 0 else Signal.NEUTRAL

##### Fundamental Agent #####
def fundamental_agent(state: FundState):
    """
    Analyzes fundamental data and generates trading signals using an LLM.
    
    Dependencies:
        - get_financial_metrics
        - Fundamental Thresholds
        - FUNDAMENTAL_PROMPT
    """
    agent_name = "fundamentals_agent"
    end_date = state["end_date"]
    ticker = state["ticker"]
    llm_config = state["llm_config"]
    logger.log_agent_status(agent_name, ticker, "Fetching financial metrics")

    # Get the financial metrics
    financial_metrics = get_financial_metrics(
        ticker=ticker,
        end_date=end_date,
        period="ttm",
        limit=10,
    )

    if not financial_metrics:
        logger.error(f"Failed to fetch financial metrics for {ticker}")
        return {"decisions": state.get("decisions", [])}

    # Pull the most recent metrics and thresholds
    metrics = financial_metrics[0]
    thresholds = load_thresholds()
    if not thresholds:
        logger.error(f"Failed to load fundamental thresholds")
        return {"decisions": state.get("decisions", [])}
    
    # Run analysis
    analysis_results = {
        "profitability": _analyze_profitability(metrics, thresholds["profitability"]),
        "growth": _analyze_growth(metrics, thresholds["growth"]),
        "financial_health": _analyze_financial_health(metrics, thresholds["financial_health"]),
        "price_ratios": _analyze_price_ratios(metrics, thresholds["price_ratios"])
    }
    
    # Make prompt
    context = {
        "ticker": ticker,
        "metrics": metrics,
        "analysis": analysis_results,
        "agent_name": agent_name
    }
    prompt = FUNDAMENTAL_PROMPT.format(**context)
    
    # Get LLM decision
    decision = make_decision(
        prompt=prompt, 
        llm_config=llm_config, 
        agent_name=agent_name, 
        ticker=ticker)
    
    # Update state
    state["agent_decisions"].update({agent_name: decision})
    
    logger.log_agent_status(agent_name, ticker, "Done")
    
    return {"agent_decisions": state["agent_decisions"]}
