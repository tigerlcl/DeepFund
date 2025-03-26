"""
Unified shared data models across all APIs.
"""

from typing import Optional
from pydantic import BaseModel, Field

class TickerPrice(BaseModel):
    """Unified price data model."""
    open: float
    close: float
    high: float
    low: float
    volume: int
    

class FinancialMetrics(BaseModel):
    """
    Financial metrics model.
    
    Related APIs:
    FinancialDataset 

    Related Agents:
    Fundamental Analysis Agent
    """
    ticker: str

    # Profitability metrics
    return_on_equity: Optional[float] = None
    net_margin: Optional[float] = None
    operating_margin: Optional[float] = None

    # Growth metrics
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    book_value_growth: Optional[float] = None

    # Financial health metrics
    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    earnings_per_share: Optional[float] = None
    free_cash_flow_per_share: Optional[float] = None


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


class MediaNews(BaseModel):
    """Unified news item model."""
    ticker: str
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    source_name: str = Field(..., description="Name of the news source")
    url: str
    sentiment: Optional[str] = Field(None, description="Positive, Negative, or Neutral")