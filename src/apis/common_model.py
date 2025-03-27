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
    title: str
    publish_time: str
    publisher: str
    link: str