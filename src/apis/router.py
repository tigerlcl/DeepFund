"""
Helper functions to route API data to the corresponding agent.
"""

from typing import Any

import apis.datamodel as mod

# Financial Datasets API exports
from apis.financialdataset import FinancialDatasetAPI, FinancialMetrics

# YFinance API exports (to be implemented)
# from apis.yfinance import (
#     get_price_data as yf_get_price_data,
#     get_financial_metrics as yf_get_financial_metrics,
#     ...
# )

# Jin10 API exports (to be implemented)
# from apis.jin10 import (
#     get_news as jin10_get_news,
#     ...
# )

# AKShare API exports (to be implemented)
# from apis.akshare import (
#     get_stock_data as ak_get_stock_data,
#     ...
# )


# def get_price_data(source: str = "financialdataset", **kwargs: Any) -> list[mod.PriceData]:
#     """
#     Get price data from the specified data source.
    
#     Args:
#         source: The data source to use ("financialdataset", "yfinance", etc.)
#         **kwargs: Arguments to pass to the underlying API function
    
#     Returns:
#         Price data in the format specified by the chosen API
#     """
#     if source == "financialdataset":
#         return fd_get_price_data(**kwargs)
#     # elif source == "yfinance":
#     #     return yf_get_price_data(**kwargs)
#     # elif source == "akshare":
#     #     return ak_get_price_data(**kwargs)
#     else:
#         raise ValueError(f"Unsupported data source: {source}")

def get_financial_metrics(ticker: str, source: str = "financialdataset") -> FinancialMetrics:
    """
    Get financial metrics from the specified data source.
    
    Args:
        source: The data source to use ("financialdataset", "yfinance", etc.)
        **kwargs: Arguments to pass to the underlying API function
    
    Returns:
        Financial metrics in the format specified by the chosen API
    """
    if source == "financialdataset":
        api = FinancialDatasetAPI(ticker=ticker)
        return api.get_financial_metrics()
    # elif source == "yfinance":
    #     return yf_get_financial_metrics(**kwargs)
    else:
        raise ValueError(f"Unsupported data source: {source}")

# def get_insider_trades(source: str = "financialdataset", **kwargs: Any) -> Any:
#     """
#     Get insider trades from the specified data source.
    
#     Args:
#         source: The data source to use ("financialdataset", "yfinance", etc.)
#         **kwargs: Arguments to pass to the underlying API function
    
#     Returns:
#         Insider trades data in the format specified by the chosen API
#     """
#     if source == "financialdataset":
#         return fd_get_insider_trades(**kwargs)
#     else:
#         raise ValueError(f"Unsupported data source: {source}")

# def get_company_news(source: str = "financialdataset", **kwargs: Any) -> Any:
#     """
#     Get company news from the specified data source.
    
#     Args:
#         source: The data source to use ("financialdataset", "jin10", etc.)
#         **kwargs: Arguments to pass to the underlying API function
    
#     Returns:
#         Company news data in the format specified by the chosen API
#     """
#     if source == "financialdataset":
#         return fd_get_company_news(**kwargs)
#     # elif source == "jin10":
#     #     return jin10_get_news(**kwargs)
#     else:
#         raise ValueError(f"Unsupported data source: {source}") 
