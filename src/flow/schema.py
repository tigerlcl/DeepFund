from typing import  List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


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
    ticker: str
    action: Action = Field( 
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

class Portfolio(BaseModel):
    """Portfolio state when running the workflow."""
    balance: float = Field(
        description="Balance for the fund."
    )
    positions: dict[str, Position] = Field(
        description="Positions for the fund."
    )
    trading_datetime: str = Field(
        description="Trading datetime for the fund."
    )

class FundState(BaseModel):
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
    ticker: Optional[str] = Field(
        default="",
        description="Current ticker."
    )
    # agent_name -> decision
    agent_decisions: Optional[Dict[str, Decision]] = Field(
        default={},
        description="decisions from all agents."
    )