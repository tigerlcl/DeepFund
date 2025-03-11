import json
from langchain_core.messages import HumanMessage
from typing import Dict, Any

from flow.schema import FundState, Decision
from util.logger import logger
from ingestion.api import get_financial_metrics, get_market_cap, search_line_items
from agent.registry import AgentKey
from flow.prompt import VALUATION_PROMPT
from util.agent import make_decision


##### Valuation Agent #####
def _analyze_valuation(metrics, line_items, market_cap) -> Dict[str, Any]:
    """Analyze valuation using multiple methods."""
    # Calculate working capital change
    working_capital_change = line_items[0].working_capital - line_items[1].working_capital

    # Owner Earnings Valuation
    owner_earnings_value = calculate_owner_earnings_value(
        net_income=line_items[0].net_income,
        depreciation=line_items[0].depreciation_and_amortization,
        capex=line_items[0].capital_expenditure,
        working_capital_change=working_capital_change,
        growth_rate=metrics.earnings_growth
    )

    # DCF Valuation
    dcf_value = calculate_intrinsic_value(
        free_cash_flow=line_items[0].free_cash_flow,
        growth_rate=metrics.earnings_growth
    )

    return {
        "owner_earnings_value": float(owner_earnings_value),
        "dcf_value": float(dcf_value),
        "market_cap": float(market_cap),
        "metrics": metrics
    }

def valuation_agent(state: FundState):
    """Performs detailed valuation analysis."""
    agent_name = AgentKey.VALUATION
    end_date = state["end_date"]
    ticker = state["ticker"]
    llm_config = state["llm_config"]

    logger.log_agent_status(agent_name, ticker, "Fetching financial data")

    # Get financial metrics
    financial_metrics = get_financial_metrics(
        ticker=ticker,
        end_date=end_date,
        period="ttm"
    )

    if not financial_metrics:
        return state

    # Get line items
    line_items = search_line_items(
        ticker=ticker,
        line_items=[
            "free_cash_flow",
            "net_income",
            "depreciation_and_amortization",
            "capital_expenditure",
            "working_capital"
        ],
        end_date=end_date,
        period="ttm",
        limit=2
    )

    if len(line_items) < 2:
        return state

    # Get market cap
    market_cap = get_market_cap(ticker=ticker, end_date=end_date)
    
    if not market_cap:
        return state

    # Analyze valuation
    valuation_analysis = _analyze_valuation(
        financial_metrics[0], 
        line_items,
        market_cap
    )

    # Make prompt
    prompt = VALUATION_PROMPT.format(
        ticker=ticker,
        analysis=valuation_analysis
    )

    # Get LLM decision
    decision = make_decision(
        prompt=prompt,
        llm_config=llm_config,
        agent_name=agent_name,
        ticker=ticker
    )

    logger.log_agent_status(agent_name, ticker, "Done")
    return {"agent_decisions": decision}


def calculate_owner_earnings_value(
    net_income: float,
    depreciation: float,
    capex: float,
    working_capital_change: float,
    growth_rate: float = 0.05,
    required_return: float = 0.15,
    margin_of_safety: float = 0.25,
    num_years: int = 5,
) -> float:
    """
    Calculates the intrinsic value using Buffett's Owner Earnings method.

    Owner Earnings = Net Income
                    + Depreciation/Amortization
                    - Capital Expenditures
                    - Working Capital Changes

    Args:
        net_income: Annual net income
        depreciation: Annual depreciation and amortization
        capex: Annual capital expenditures
        working_capital_change: Annual change in working capital
        growth_rate: Expected growth rate
        required_return: Required rate of return (Buffett typically uses 15%)
        margin_of_safety: Margin of safety to apply to final value
        num_years: Number of years to project

    Returns:
        float: Intrinsic value with margin of safety
    """
    if not all([isinstance(x, (int, float)) for x in [net_income, depreciation, capex, working_capital_change]]):
        return 0

    # Calculate initial owner earnings
    owner_earnings = net_income + depreciation - capex - working_capital_change

    if owner_earnings <= 0:
        return 0

    # Project future owner earnings
    future_values = []
    for year in range(1, num_years + 1):
        future_value = owner_earnings * (1 + growth_rate) ** year
        discounted_value = future_value / (1 + required_return) ** year
        future_values.append(discounted_value)

    # Calculate terminal value (using perpetuity growth formula)
    terminal_growth = min(growth_rate, 0.03)  # Cap terminal growth at 3%
    terminal_value = (future_values[-1] * (1 + terminal_growth)) / (required_return - terminal_growth)
    terminal_value_discounted = terminal_value / (1 + required_return) ** num_years

    # Sum all values and apply margin of safety
    intrinsic_value = sum(future_values) + terminal_value_discounted
    value_with_safety_margin = intrinsic_value * (1 - margin_of_safety)

    return value_with_safety_margin


def calculate_intrinsic_value(
    free_cash_flow: float,
    growth_rate: float = 0.05,
    discount_rate: float = 0.10,
    terminal_growth_rate: float = 0.02,
    num_years: int = 5,
) -> float:
    """
    Computes the discounted cash flow (DCF) for a given company based on the current free cash flow.
    Use this function to calculate the intrinsic value of a stock.
    """
    # Estimate the future cash flows based on the growth rate
    cash_flows = [free_cash_flow * (1 + growth_rate) ** i for i in range(num_years)]

    # Calculate the present value of projected cash flows
    present_values = []
    for i in range(num_years):
        present_value = cash_flows[i] / (1 + discount_rate) ** (i + 1)
        present_values.append(present_value)

    # Calculate the terminal value
    terminal_value = cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    terminal_present_value = terminal_value / (1 + discount_rate) ** num_years

    # Sum up the present values and terminal value
    dcf_value = sum(present_values) + terminal_present_value

    return dcf_value


def calculate_working_capital_change(
    current_working_capital: float,
    previous_working_capital: float,
) -> float:
    """
    Calculate the absolute change in working capital between two periods.
    A positive change means more capital is tied up in working capital (cash outflow).
    A negative change means less capital is tied up (cash inflow).

    Args:
        current_working_capital: Current period's working capital
        previous_working_capital: Previous period's working capital

    Returns:
        float: Change in working capital (current - previous)
    """
    return current_working_capital - previous_working_capital
