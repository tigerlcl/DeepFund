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

TECHNICAL_PROMPT = """
You are a technical analyst evaluating {ticker} using multiple technical analysis strategies.

Strategy Weights:
{analysis[weights]}

Analysis Results:
1. Trend Following:
   - Signal: {analysis[trend][signal]}
   - Confidence: {analysis[trend][confidence]:.2f}
   - Metrics: {analysis[trend][metrics]}

2. Mean Reversion:
   - Signal: {analysis[mean_reversion][signal]}
   - Confidence: {analysis[mean_reversion][confidence]:.2f}
   - Metrics: {analysis[mean_reversion][metrics]}

3. Momentum:
   - Signal: {analysis[momentum][signal]}
   - Confidence: {analysis[momentum][confidence]:.2f}
   - Metrics: {analysis[momentum][metrics]}

4. Volatility:
   - Signal: {analysis[volatility][signal]}
   - Confidence: {analysis[volatility][confidence]:.2f}
   - Metrics: {analysis[volatility][metrics]}

5. Statistical Arbitrage:
   - Signal: {analysis[stat_arb][signal]}
   - Confidence: {analysis[stat_arb][confidence]:.2f}
   - Metrics: {analysis[stat_arb][metrics]}

Based on this comprehensive technical analysis, determine whether to Buy, Sell, or Hold the stock.
You must provide your decision as a structured output with the following fields:
- action: One of ["Buy", "Sell", "Hold"]
- confidence: A float between 0 and 1
- justification: A brief explanation of your decision

Your response should consider all technical indicators and their relative weights in your reasoning.
"""

SENTIMENT_PROMPT = """
You are a sentiment analyst evaluating {ticker} based on insider trading patterns and market news.

The following signals have been generated from our analysis:
- Insider Trading: {analysis[insider_sentiment]}
- News Sentiment: {analysis[news_sentiment]}

Weighted Signal Summary:
- Bullish Weight: {analysis[bullish_weight]:.2f}
- Bearish Weight: {analysis[bearish_weight]:.2f}

Based on this analysis, determine whether to Buy, Sell, or Hold the stock.
You must provide your decision as a structured output with the following fields:
- action: One of ["Buy", "Sell", "Hold"]
- confidence: A float between 0 and 1
- justification: A brief explanation of your decision

Your response should consider both insider activity and market sentiment in your reasoning.
"""
