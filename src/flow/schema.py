from typing import  List, Dict, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, Literal
from enum import Enum
import operator

class Signal(str, Enum):
    """Signal type"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class Action(str, Enum):
    """Action type"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class Decision(BaseModel):
    """Decision Structured Output from agent"""
    agent_name: str
    ticker: str
    action: Literal[Action.BUY, Action.SELL, Action.HOLD] = Field( 
        description="Choose from Buy, Sell, or Hold",
        default=Action.HOLD
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1",
        ge=0.0,
        le=1.0,
        default=0.0
    )
    justification: str = Field(
        description="Brief explanation for the decision",
        default="No decision made due to error"
    )

class Position(BaseModel):
    value: float = Field(
        default=0.0,
        description="Monetary value for the position."
    )
    shares: int = Field(
        default=0,
        description="Shares for the position."
    )

class Portfolio(BaseModel):
    """Portfolio state when running the workflow."""
    cashflow: float = Field(
        description="Cashflow for the fund."
    )
    positions: dict[str, Position] = Field(
        description="Positions for each ticker."
    )

class FundState(TypedDict):
    """Fund state when running the workflow."""

    # from environment
    portfolio: Portfolio = Field(
        description="Portfolio for the fund."
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
    llm_config: Dict[str, Any] = Field(
        description="LLM configuration."
    )

    # from workflow
    ticker: str
    # ticker:->decision of all analyst agents
    agent_decisions: Annotated[Decision, operator.add]