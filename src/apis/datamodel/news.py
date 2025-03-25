"""
News data models for financial data APIs.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    """Unified news item model."""
    ticker: str
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    source_name: str = Field(..., description="Name of the news source")
    published_at: datetime = Field(..., description="UTC timestamp of publication")
    url: str
    sentiment: Optional[str] = Field(None, description="Positive, Negative, or Neutral")
    data_source: str = Field(..., description="Data source identifier")


class NewsResponse(BaseModel):
    """Unified news response."""
    ticker: str
    news_items: list[NewsItem]
    source: str = Field(..., description="Data source identifier") 