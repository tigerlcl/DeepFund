"""Unified data models across multiple APIs."""

from typing import Optional
from pydantic import BaseModel, Field

class TickerPrice(BaseModel):
    """Unified price data model."""
    open: float
    close: float
    high: float
    low: float
    volume: int
    

class MediaNews(BaseModel):
    """Unified news item model."""
    ticker: str
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    source_name: str = Field(..., description="Name of the news source")
    url: str
    sentiment: Optional[str] = Field(None, description="Positive, Negative, or Neutral")