"""
Alpha Vantage API client implementation.
Link: https://www.alphavantage.co/documentation/
Free tier: 25 API requests per day
"""


import os
import requests
import pandas as pd
from apis.common_model import OHLCVCandle
from .api_model import InsiderTrade, Fundamentals

class AlphaVantageAPI:
    """Alpha Vantage API Wrapper."""

    def __init__(self):
        self.api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"

    def get_daily_candles(self, ticker: str) -> list[OHLCVCandle]: 
        """
        Get daily candles for a ticker. 
        It defaults to latest 100 data points.
        """
        response = requests.get(
            url=self.base_url,
            params={
                "function": "TIME_SERIES_DAILY", 
                "symbol": ticker, 
                "apikey": self.api_key}
        )

        if response.status_code != 200:
            response.raise_for_status()
        
        # parse response into OHLCVCandle objects
        candle_series = response.json()["Time Series (Daily)"]
        daily_candles = []
        
        for date, data in candle_series.items():
            candle = OHLCVCandle(
                date=date,
                open=float(data["1. open"]),
                high=float(data["2. high"]),
                low=float(data["3. low"]),
                close=float(data["4. close"]),
                volume=int(data["5. volume"])
            )
            daily_candles.append(candle)

        return daily_candles

    def get_daily_candles_df(self, ticker: str) -> pd.DataFrame:
        """
        Get daily candles for a ticker as a pandas DataFrame.
        Returns a DataFrame with datetime index and numeric columns.
        """
        daily_candles = self.get_daily_candles(ticker)
        
        # Convert list of OHLCVCandle objects to DataFrame
        df = pd.DataFrame([candle.model_dump() for candle in daily_candles])
        
        # Convert date column to datetime and set as index
        df["Date"] = pd.to_datetime(df["date"])
        df.set_index("Date", inplace=True)
        df.drop("date", axis=1, inplace=True)  # Remove original date column
        
        # Convert price and volume columns to numeric
        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
        # Sort by date index
        df.sort_index(inplace=True)
        
        return df


    def get_insider_trades(self, ticker: str, limit: int) -> list[InsiderTrade]:
        """
        Get insider trades for a ticker.
        This API returns the latest and historical insider transactions made be key stakeholders (e.g., founders, executives, board members, etc.) of a specific company.
        """
        response = requests.get(
            url=self.base_url,
            params={"function": "INSIDER_TRANSACTIONS", "symbol": ticker, "apikey": self.api_key})
        
        if response.status_code != 200:
            response.raise_for_status()

        recent_trades = response.json()["data"][:limit]
        
        return [InsiderTrade(**trade) for trade in recent_trades]

    def get_fundamentals(self, ticker: str) -> Fundamentals:
        """Get company fundamentals from Alpha Vantage."""
        response = requests.get(
            url=self.base_url,
            params={"function": "OVERVIEW", "symbol": ticker, "apikey": self.api_key}
        )
        if response.status_code != 200:
            response.raise_for_status()

        data = response.json()
        
        # The field names in data match our model's aliases automatically
        try:
            fundamentals = Fundamentals(**data)  # Automatic field mapping happens here
            return fundamentals
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None

