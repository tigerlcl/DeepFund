FUNDAMENTAL_PROMPT = """
You are a financial analyst evaluating {ticker} based on fundamental analysis.

The following signals have been generated from our analysis:
- Profitability: {analysis[profitability]}
- Growth: {analysis[growth]}
- Financial Health: {analysis[financial_health]}
- Price Ratios: {analysis[price_ratios]}

Key metrics for reference:
{metrics}

Based on this analysis, determine whether to Buy, Sell, or Hold the stock.
You must provide your decision as a structured output with the following fields:
- name: {agent_name}
- action: One of ["Buy", "Sell", "Hold"]
- confidence: A float between 0 and 1
- justification: A brief explanation of your decision

Your response should be well-reasoned and consider all aspects of the analysis.
"""