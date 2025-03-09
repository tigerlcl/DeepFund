import operator
from typing import  List, Dict, Any, Annotated, TypedDict
from pydantic import BaseModel, Field


class AnalystSignal(BaseModel):
    """Analyst signal definition for the workflow.
    Accessible to analyst agents.
    """

    name: str = Field(
        description="Name for the analyst agent.",
    )
    decision: str = Field(
        description="Choose from Buy, Sell, or Hold",
        enum=["Buy", "Sell", "Hold"]
    )
    confidence_score: float = Field(
        description="Confidence score between 0 and 1",
        ge=0.0,
        le=1.0
    )
    justification: str = Field(
        description="Brief explanation for the decision"
    )


class TickerSignal(BaseModel):
    """Ticker-level signal definition for the workflow.
    Accessible to manager agents.
    """

    ticker: str = Field(
        description="Current ticker."
    )
    analyst_signals: List[AnalystSignal] = Field(
        description="Signals from the analyst agents."
    )
    last_position: float = Field(
        description="Last position."
    )
    new_position: float = Field(
        description="New position."
    )
    final_decision: str = Field(
        description="Final decision for the ticker.",
        enum=["Buy", "Sell", "Hold"]
    )
    

class FundState(TypedDict):
    """Fund state when running the workflow."""

    tickers : List[str]
    signals: Annotated[List[TickerSignal], operator.add]
    portfolio_settings: Dict[str, Any]
