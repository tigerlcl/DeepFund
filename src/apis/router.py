"""Router for APIs"""

from apis import YFinanceAPI, AlphaVantageAPI

class APISource:
    YFINANCE = "yfinance"
    ALPHA_VANTAGE = "alpha_vantage"

class Router():
    """Router for APIs"""
    
    def __init__(self, source: APISource):
        if source == APISource.YFINANCE:
            self.api = YFinanceAPI()
        elif source == APISource.ALPHA_VANTAGE:
            self.api = AlphaVantageAPI()
        else:
            raise ValueError(f"Invalid API source: {source}")
    

    def get_us_stock_news(self, ticker: str, news_count: int = 10):
        """Get news for a ticker"""
        return self.api.get_news(ticker, news_count)

    def get_us_stock_insider_trades(self, ticker: str, limit: int = 10):
        """Get insider trades for a ticker"""
        return self.api.get_insider_trades(ticker, limit)
    
    def get_us_stock_daily_candles_df(self, ticker: str):
        """Get daily candles for a ticker as a pandas DataFrame"""
        return self.api.get_daily_candles_df(ticker)
    
    def get_us_stock_last_close_price(self, ticker: str):
        """Get the last close price for a ticker"""
        return self.api.get_last_close_price(ticker)

    def get_us_stock_fundamentals(self, ticker: str):
        """Get fundamentals for a ticker"""
        return self.api.get_fundamentals(ticker)
    
    def get_economic_indicators(self):
        """Get economic indicators."""
        return self.api.get_economic_indicators()
    
    def get_topic_news_sentiment(self, limit: int, topic: str):
        """Get market news and sentiment."""
        return self.api.get_market_news_sentiment(limit, topic)

