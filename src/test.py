"""Test script"""

from apis import AlphaVantageAPI, YFinanceAPI

if __name__ == "__main__":

    ticker = "MSFT"

    av_api = AlphaVantageAPI()
    result = av_api.get_insider_trades(ticker=ticker, limit=10)
    print(result)