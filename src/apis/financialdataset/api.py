import os
import requests
from .api_model import FinancialMetrics, InsiderTrade

class FinancialDatasetAPI:      
    """Financial Datasets API client implementation."""

    def __init__(self):
        self.api_key = os.environ.get("FINANCIAL_DATASETS_API_KEY")
        self.base_url = "https://api.financialdatasets.ai"

    def get_financial_metrics(self, ticker: str) -> FinancialMetrics:
        """Get a real-time snapshot of key financial metrics and ratios for a ticker."""
        response = requests.get(
            url=f"{self.base_url}/financial-metrics/snapshot", 
            headers={"X-API-KEY": self.api_key}, 
            params={"ticker": ticker}
            )
        if response.status_code != 200:
            response.raise_for_status()
        
        # parse response into FinancialMetric object
        snapshot = response.json().get("snapshot")
        metrics = FinancialMetrics(**snapshot)
        
        return metrics


    def get_insider_trades(self, ticker: str, limit: int) -> list[InsiderTrade]:
        """
        Get insider trades like buys and sells for a ticker by a company insider.
        Trades are sorted by transaction date from the most recent date.

        Args:
            ticker (str): The ticker symbol of the company to get insider trades for.
            limit (int): The maximum number of insider trades to return.

        Returns:
            list[InsiderTrade]: A list of InsiderTrade objects.
        """
        response = requests.get(
            url=f"{self.base_url}/insider-trades", 
            headers={"X-API-KEY": self.api_key}, 
            params={"ticker": ticker, "limit": limit}
            )
        if response.status_code != 200:
            response.raise_for_status()

        insider_trades = response.json().get('insider_trades')
        trades = [InsiderTrade(**trade) for trade in insider_trades]

        return trades


    # def get_company_news(self, end_date: str, start_date: str | None = None, limit: int,) -> list[MediaNews]:
    #     """Fetch company news from API."""
    #     response = requests.get(
    #         url=f"{self.base_url}/news", 
    #         headers={"X-API-KEY": self.api_key}, 
    #         params={"ticker": self.ticker, "end_date": end_date, "start_date": start_date, "limit": limit}
    #         )

# def get_company_news(
#     ticker: str,
#     end_date: str,
#     start_date: str | None = None,
#     limit: int = 1000,
# ) -> list[NewsItem]:
#     """Fetch company news from API."""
#     headers = {}
#     if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
#         headers["X-API-KEY"] = api_key

#     all_news = []
#     current_end_date = end_date
    
#     while True:
#         url = f"https://api.financialdatasets.ai/news/?ticker={ticker}&end_date={current_end_date}"
#         if start_date:
#             url += f"&start_date={start_date}"
#         url += f"&limit={limit}"
        
#         response = requests.get(url, headers=headers)
#         if response.status_code != 200:
#             raise Exception(f"Error fetching data: {response.status_code} - {response.text}")
        
#         raw_data = response.json()
#         news_items = [
#             NewsItem(
#                 ticker=n["ticker"],
#                 title=n["title"],
#                 author=n.get("author"),
#                 source_name=n["source"],
#                 published_at=datetime.fromisoformat(n["date"].replace('Z', '+00:00')),
#                 url=n["url"],
#                 sentiment=n.get("sentiment"),
#                 data_source="financialdataset"
#             )
#             for n in raw_data["news"]
#         ]
        
#         if not news_items:
#             break
            
#         all_news.extend(news_items)
        
#         # Only continue pagination if we have a start_date and got a full page
#         if not start_date or len(news_items) < limit:
#             break
            
#         # Update end_date to the oldest date from current batch for next iteration
#         current_end_date = min(n.published_at.date().isoformat() for n in news_items)
        
#         # If we've reached or passed the start_date, we can stop
#         if current_end_date <= start_date:
#             break

#     return NewsResponse(
#         ticker=ticker,
#         news_items=all_news,
#         source="financialdataset"
#     ).news_items


# def _prices_to_df(prices: list[PriceData]) -> pd.DataFrame:
#     """Convert prices to a DataFrame."""
#     df = pd.DataFrame([p.model_dump() for p in prices])
#     df["Date"] = pd.to_datetime(df["timestamp"])
#     df.set_index("Date", inplace=True)
#     numeric_cols = ["open", "close", "high", "low", "volume"]
#     for col in numeric_cols:
#         df[col] = pd.to_numeric(df[col], errors="coerce")
#     df.sort_index(inplace=True)
#     return df


# def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
#     """Get price data as a DataFrame."""
#     try:
#         prices = _get_prices(ticker, start_date, end_date)
#         return _prices_to_df(prices)
#     except Exception as e:
#         logger.error(f"Failed to fetch price data for {ticker}: {e}")
#         return None 
