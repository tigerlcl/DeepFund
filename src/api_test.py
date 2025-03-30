from apis.alphavantage import AlphaVantageAPI
from dotenv import load_dotenv

load_dotenv()

api = AlphaVantageAPI()

# Get just fundamentals
fundamentals = api.get_fundamentals("IBM")
print(fundamentals.pe_ratio)  
print(fundamentals.return_on_equity_ttm)
