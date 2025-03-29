from graph.schema import FundState, AnalystSignal
from graph.constants import Signal, AgentKey
from graph.prompt import FUNDAMENTAL_PROMPT
from llm.inference import agent_call
from apis import FinancialDatasetAPI
from database.helper import db
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
    "cash_flow": {
        "cash_ratio": 0.6,
        "free_cash_flow_yield": 0.035, # compare to 10-year treasury yield
        "free_cash_flow_growth": 0.025 # compare to inflation rate
    },
    "financial_health": {
        "current_ratio": 1.5,
        "debt_to_equity": 0.5,
        "fcf_to_eps_ratio": 0.8
    },
}


def fundamental_agent(state: FundState):
    """Fundamental analysis specialist focusing on company profitability, growth, cashflow and financial health."""
    agent_name = AgentKey.FUNDAMENTAL
    ticker = state["ticker"]
    llm_config = state["llm_config"]
    portfolio_id = state["portfolio"].id

    logger.log_agent_status(agent_name, ticker, "Fetching financial metrics")

    # Get the financial metrics
    fd_api = FinancialDatasetAPI()
    metrics = fd_api.get_financial_metrics(ticker=ticker)
    if not metrics:
        logger.error(f"Failed to fetch financial metrics for {ticker}")
        return state
    
    # Run analysis
    signal_results = {
        "profitability": analyze_profitability(metrics, thresholds["profitability"]),
        "growth": analyze_growth(metrics, thresholds["growth"]),
        "financial_health": analyze_financial_health(metrics, thresholds["financial_health"]),
        "cashflow": analyze_cashflow(metrics, thresholds["cash_flow"])
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
    
    # save signal
    logger.log_signal(agent_name, ticker, signal)
    db.save_signal(portfolio_id, agent_name, ticker, prompt, signal)
    
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


def analyze_cashflow(metrics, params):
    """Analyze company cashflow metrics."""
    score = sum(
        metric > threshold for metric, threshold in [
            (metrics.free_cash_flow_yield, params["free_cash_flow_yield"]),
            (metrics.free_cash_flow_growth, params["free_cash_flow_growth"]),
            (metrics.cash_ratio, params["cash_ratio"])
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

