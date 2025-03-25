"""
Price data models for financial data APIs.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class PriceData(BaseModel):
    """Unified price data model."""
    open: float
    close: float
    high: float
    low: float
    volume: int
    timestamp: datetime = Field(..., description="UTC timestamp of the price data")
    source: str = Field(..., description="Data source identifier (e.g., 'financialdataset', 'yfinance', 'akshare')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "open": 150.25,
                "close": 151.50,
                "high": 152.00,
                "low": 149.75,
                "volume": 1000000,
                "timestamp": "2024-03-25T10:30:00Z",
                "source": "financialdataset"
            }
        }
