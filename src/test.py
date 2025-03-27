"""Test script"""

from apis import YFinanceAPI

if __name__ == "__main__":

    ticker = "MSFT"
    yf_api = YFinanceAPI()
    result = yf_api.get_news(ticker=ticker)
    print(result)