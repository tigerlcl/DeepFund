"""Cache manager for Alpha Vantage API responses"""

from datetime import datetime
from typing import Dict, Tuple, Optional, TypeVar
from apis.common_model import OHLCVCandle

T = TypeVar('T')

class CacheManager:
    """Singleton cache manager for API responses"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_candles_cache'):
            self._candles_cache: Dict[Tuple[str, Optional[datetime]], list[OHLCVCandle]] = {}
    
    @property
    def candles_cache(self) -> Dict[Tuple[str, Optional[datetime]], list[OHLCVCandle]]:
        """Get the candles cache"""
        return self._candles_cache
    
    def get_candles(self, ticker: str, trading_date: Optional[datetime] = None) -> Optional[list[OHLCVCandle]]:
        """Get candles from cache if available"""
        cache_key = (ticker, trading_date)
        return self._candles_cache.get(cache_key)
    
    def set_candles(self, ticker: str, trading_date: Optional[datetime], candles: list[OHLCVCandle]):
        """Store candles in cache"""
        cache_key = (ticker, trading_date)
        self._candles_cache[cache_key] = candles 