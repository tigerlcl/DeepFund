"""Unified data models across multiple APIs."""

from pydantic import BaseModel

class OHLCVCandle(BaseModel):
    """Unified OHLCV candle data model."""
    open: float
    high: float
    low: float
    close: float
    volume: int
    date: str

class MediaNews(BaseModel):
    """Unified news item model."""
    title: str
    publish_time: str
    publisher: str
    link: str