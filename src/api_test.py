from apis.router import Router, APISource
from dotenv import load_dotenv

load_dotenv()

router = Router(APISource.ALPHA_VANTAGE)

# Get just fundamentals
# fundamentals = router.get_us_stock_fundamentals("IBM")
# print(fundamentals.pe_ratio)  
# print(fundamentals.return_on_equity_ttm)

economic_indicators = router.get_economic_indicators()
print(economic_indicators)