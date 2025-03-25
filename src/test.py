from apis.router import get_financial_metrics


# test router
if __name__ == "__main__":
    metrics = get_financial_metrics(ticker="AAPL")
    print(metrics)