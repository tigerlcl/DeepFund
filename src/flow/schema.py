from typing import  List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Decision(BaseModel):
    """Decision Structured Output from agent"""

    name: str = Field(
        description="Name for the agent",
    )
    action: str = Field( 
        description="Choose from Buy, Sell, or Hold",
        enum=["Buy", "Sell", "Hold"]
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1",
        ge=0.0,
        le=1.0
    )
    justification: str = Field(
        description="Brief explanation for the decision"
    )


class Position(BaseModel):
    cash: float = Field(
        default=0.0,
        description="Cash for the position."
    )
    shares: int = Field(
        default=0,
        description="Shares for the position."
    )
    ticker: str = Field(
        default="",
        description="Ticker for the position."
    )


class FundState(BaseModel):
    """Fund state when running the workflow."""

    # from environment
    balance: float = Field(
        default=100000.0,
        description="Balance for the fund."
    )
    positions: dict[str, Position] = Field(
        description="Positions for the fund."
    )
    start_date: str = Field(
        description="Start date for the information window."
    )
    end_date: str = Field(
        description="End date for the information window."
    )
    tickers: List[str] = Field(
        description="List of tickers to analyze"
    )

    # from workflow
    analyst_in_the_loop: Optional[List[str]] = Field(
        default=None,
        description="List of analyst agents to analyze the ticker."
    )
    ticker: Optional[str] = Field(
        default=None,
        description="Current ticker."
    )
    # manager aggregated from analyst signals per ticker
    decisions: Optional[List[Dict[str, Decision]]] = Field(
        default=None,
        description="decisions for the portfolio in current workflow."
    )