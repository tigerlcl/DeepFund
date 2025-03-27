"""Helper functions to route API data to the corresponding agent."""


# import all APIs
from apis.financialdataset import FinancialDatasetAPI
# from apis.yfinance import YFinanceAPI
# from apis.joinquant import JoinQuantAPI

# constants
class Source:
    FINANCIAL_DATASET = "fd"
    # YFINANCE = "yf"
    # JOINQUANT = "jq"


class APIHub:   

    API_COLLECTION = {
        Source.FINANCIAL_DATASET: FinancialDatasetAPI,
        # Source.YFINANCE: YFinanceAPI,
        # Source.JOINQUANT: JoinQuantAPI,
    }

    @classmethod
    def get_api(cls, source: Source):
        return cls.API_COLLECTION[source]()