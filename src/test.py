"""Test script"""

from apis.hub import get_financial_metrics


if __name__ == "__main__":
    metrics = get_financial_metrics(ticker="AAPL")
    print(metrics)