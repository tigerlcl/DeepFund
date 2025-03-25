import os
import requests
from typing import Optional
from pydantic import BaseModel


class FinancialMetrics(BaseModel):
    """
    Financial metrics model.
    Feed into the fundamental analysis agent.
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


class FinancialDatasetAPI:      
    """Financial Datasets API client implementation."""

    def __init__(self, ticker: str):
        self.api_key = os.environ.get("FINANCIAL_DATASETS_API_KEY")
        self.base_url = "https://api.financialdatasets.ai"
        self.ticker = ticker
        # self.start_date = kwargs.get("start_date")
        # self.end_date = kwargs.get("end_date")
        # self.period = kwargs.get("period")
        # self.limit = kwargs.get("limit")

    # def _get_prices(self, ticker: str, start_date: str, end_date: str) -> list[PriceData]:
    #     """Fetch price data from API."""
    # headers = {}
    # if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
    #     headers["X-API-KEY"] = api_key

    # url = f"https://api.financialdatasets.ai/prices/?ticker={ticker}&interval=day&interval_multiplier=1&start_date={start_date}&end_date={end_date}"
    # response = requests.get(url, headers=headers)
    # if response.status_code != 200:
    #     raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    # # Convert raw response to unified model
    # raw_data = response.json()
    # prices = [
    #     PriceData(
    #         open=p["open"],
    #         close=p["close"],
    #         high=p["high"],
    #         low=p["low"],
    #         volume=p["volume"],
    #         timestamp=datetime.fromisoformat(p["time"].replace('Z', '+00:00')),
    #         source="financialdataset"
    #     )
    #     for p in raw_data["prices"]
    # ]
    
    # return PriceResponse(
    #     ticker=ticker,
    #     prices=prices,
    #     source="financialdataset"
    # ).prices


    def get_financial_metrics(self) -> FinancialMetrics:

        # url = f"https://api.financialdatasets.ai/financial-metrics/?ticker={ticker}&report_period_lte={end_date}&limit={limit}&period={period}"
        response = requests.get(
            url=f"{self.base_url}/financial-metrics/snapshot", #  real-time snapshot
            headers={"X-API-KEY": self.api_key}, 
            params={"ticker": self.ticker}
            )
        if response.status_code != 200:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

        # parse response into FinancialMetric object
        snapshot = response.json().get("snapshot")
        metrics = FinancialMetrics(**snapshot)
        
        return metrics


# def get_insider_trades(
#     ticker: str,
#     end_date: str,
#     start_date: str | None = None,
#     limit: int = 1000,
# ) -> list[InsiderTrade]:
#     """Fetch insider trades from API."""
#     headers = {}
#     if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
#         headers["X-API-KEY"] = api_key

#     all_trades = []
#     current_end_date = end_date
    
#     while True:
#         url = f"https://api.financialdatasets.ai/insider-trades/?ticker={ticker}&filing_date_lte={current_end_date}"
#         if start_date:
#             url += f"&filing_date_gte={start_date}"
#         url += f"&limit={limit}"
        
#         response = requests.get(url, headers=headers)
#         if response.status_code != 200:
#             raise Exception(f"Error fetching data: {response.status_code} - {response.text}")
        
#         raw_data = response.json()
#         trades = [
#             InsiderTrade(
#                 ticker=t["ticker"],
#                 insider_name=t.get("name"),
#                 title=t.get("title"),
#                 is_director=t.get("is_board_director"),
#                 transaction_date=t.get("transaction_date", "").split('T')[0],
#                 filing_date=t["filing_date"].split('T')[0],
#                 transaction_type="Buy" if (t.get("transaction_shares", 0) or 0) > 0 else "Sell",
#                 shares=abs(t.get("transaction_shares", 0) or 0),
#                 price_per_share=t.get("transaction_price_per_share"),
#                 total_value=t.get("transaction_value"),
#                 shares_owned_after=t.get("shares_owned_after_transaction"),
#                 source="financialdataset"
#             )
#             for t in raw_data["insider_trades"]
#         ]
        
#         if not trades:
#             break
            
#         all_trades.extend(trades)
        
#         # Only continue pagination if we have a start_date and got a full page
#         if not start_date or len(trades) < limit:
#             break
            
#         # Update end_date to the oldest filing date from current batch for next iteration
#         current_end_date = min(t.filing_date for t in trades)
        
#         # If we've reached or passed the start_date, we can stop
#         if current_end_date <= start_date:
#             break

#     return InsiderTradesResponse(
#         ticker=ticker,
#         trades=all_trades,
#         source="financialdataset"
#     ).trades


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
