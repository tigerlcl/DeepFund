FUNDAMENTAL_PROMPT = """
You are a financial analyst evaluating {ticker} based on fundamental analysis.

The following signals have been generated from our analysis:
- Profitability: {analysis[profitability]}
- Growth: {analysis[growth]}
- Financial Health: {analysis[financial_health]}
- Price Ratios: {analysis[price_ratios]}

Based on this analysis, determine action with your confidence score and justification. Your response should be well-reasoned and consider all aspects of the analysis.
"""

RISK_PROMPT = """
You are a financial analyst evaluating {ticker} based on risk analysis.

The following signals have been generated from our analysis:
- Risk Signal: {analysis[risk_signal]}
- Latest Price: {analysis[latest_price]}
- Estimated Position Value: {analysis[estimated_position_value]}
- Portfolio Value: {analysis[portfolio_value]}
- Available Cash: {analysis[available_cash]}

Based on this analysis, determine action with your confidence score and justification. Your response should be well-reasoned and consider all aspects of the analysis.
"""
