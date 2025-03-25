"""
Insider trading data models for financial data APIs.
"""

from typing import Optional
from pydantic import BaseModel, Field


class InsiderTrade(BaseModel):
    """Unified insider trading data model."""
    ticker: str
    insider_name: Optional[str] = None
    title: Optional[str] = None
    is_director: Optional[bool] = None
    transaction_date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    filing_date: str = Field(..., description="Filing date (YYYY-MM-DD)")
    transaction_type: str = Field(..., description="Buy or Sell")
    shares: Optional[float] = None
    price_per_share: Optional[float] = None
    total_value: Optional[float] = None
    shares_owned_after: Optional[float] = None
    source: str = Field(..., description="Data source identifier")


class InsiderTradesResponse(BaseModel):
    """Unified insider trades response."""
    ticker: str
    trades: list[InsiderTrade]
    source: str = Field(..., description="Data source identifier") 