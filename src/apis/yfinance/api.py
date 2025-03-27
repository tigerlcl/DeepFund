"""
YFinance API client implementation.
Link: https://yfinance-python.org/
"""

import yfinance as yf
from typing import Optional
from datetime import datetime
from apis.common_model import MediaNews


class YFinanceAPI:
    """YFinance API Wrapper."""

    def __init__(self):
        pass
    
    def get_news(self, query: str, news_count: int) -> list[MediaNews]:
        """Get news for a ticker. Default news count is 8."""
        search_result = yf.Search(query=query, news_count=news_count)
        
        news_list = []
        for item in search_result.news:
            # process timestamp to human readable format
            publish_time = datetime.fromtimestamp(item["providerPublishTime"]).strftime("%Y-%m-%d %H:%M:%S")

            news_list.append(MediaNews(
                title=item["title"],
                publish_time=publish_time,
                publisher=item["publisher"],
                link=item["link"],
            ))

        return news_list

    def get_last_close_price(self, ticker: str) -> float:
        """Get the last close price for a ticker."""
        ticker_info = yf.Ticker(ticker).fast_info
        last_price = round(ticker_info["last_price"], 2)        
        return last_price
