import operator
from datetime import datetime
from typing import  List, Dict, Any
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field
from graph.constants import Signal, Action


class AnalystSignal(BaseModel):
    """Signal from analyst"""
    signal: Signal = Field(
        description=f"Choose from {Signal.BULLISH}, {Signal.BEARISH}, or {Signal.NEUTRAL}",
        default=Signal.NEUTRAL
    )
    justification: str = Field(
        description="Brief explanation for the signal",
        default="No justification provided due to error"
    )

class Decision(BaseModel):
    """Decision made by portfolio manager"""
    action: Action = Field( 
        description=f"Choose from {Action.BUY}, {Action.SELL}, or {Action.HOLD}",
        default=Action.HOLD
    )
    shares: int = Field(
        description="Number of shares to buy or sell, set 0 for hold",
        default=0
    )
    price: float = Field(
        description="Current price for the ticker",
    )
    justification: str = Field(
        description="Brief explanation for the decision",
        default="Just hold due to error"
    )

class Position(BaseModel):
    """Position for a single ticker"""
    value: float = Field(
        default=0.0,
        description="Monetary value for the position."
    )
    shares: int = Field(
        default=0,
        description="Shares for the position."
    )

class RiskAssessment(BaseModel):
    """Risk assessment for a single ticker"""
    current_price: float = Field(
        description="Current price of the stock",
        default=0.0
    )
    stop_loss: float = Field(
        description="The price at which the stock should be sold to limit losses",
        default=0.0
    )
    max_position: float = Field(
        description="The maximum allowed holding position, float number between 0 and 0.8, the more bullish the signal, the larger max_position",
        default=0.0
    )
    justification: str = Field(
        description="Detailed risk assessment rationale explaining the recommendations",
        default="No assessment provided due to insufficient data"
    )

class Portfolio(BaseModel):
    """Portfolio state when running the workflow."""
    id: str = Field(description="Portfolio id.")
    cashflow: float = Field(description="Cashflow for the fund.")
    positions: dict[str, Position] = Field(description="Positions for each ticker.")

class FundState(TypedDict):
    """Fund state when running the workflow."""

    # from environment
    exp_name: str = Field(description="Experiment name.")
    trading_date: datetime = Field(description="Trading date.")
    ticker: str = Field(description="Ticker in-the-flow.")
    llm_config: Dict[str, Any] = Field(description="LLM configuration.")
    portfolio: Portfolio = Field(description="Portfolio for the fund.")

    # updated by workflow
    # ticker -> signal of all analysts
    analyst_signals: Annotated[List[AnalystSignal], operator.add]
    # portfolio manager output
    decision: Decision
    risk_assessment: RiskAssessment
    