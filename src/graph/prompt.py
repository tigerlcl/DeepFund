ANALYST_OUTPUT_FORMAT = """
You must provide your analysis as a structured output with the following fields:
- signal: One of ["Bullish", "Bearish", "Neutral"]
- justification: A brief explanation of your analysis

Your response should be well-reasoned and consider all aspects of the analysis.
"""

FUNDAMENTAL_PROMPT = """
You are a financial analyst evaluating ticker based on fundamental analysis.

The following signals have been generated from our analysis:
- Profitability: {analysis[profitability]}
- Growth: {analysis[growth]}
- Financial Health: {analysis[financial_health]}

""" + ANALYST_OUTPUT_FORMAT

TECHNICAL_PROMPT = """
You are a technical analyst evaluating ticker using multiple technical analysis strategies.

The following signals have been generated from our analysis:
- Trend Following: {analysis[trend]}
- Mean Reversion: {analysis[mean_reversion]}
- RSI: {analysis[rsi]}
- Momentum: {analysis[momentum]}
- Volatility: {analysis[volatility]}

""" + ANALYST_OUTPUT_FORMAT

INSIDER_PROMPT = """
You are an insider trading analyst evaluating ticker based on company insider trades, the stock buys and sales of public company insiders like CEOs, CFOs, and Directors.

Here are recent {num_trades} insider trades:
{trades}

""" + ANALYST_OUTPUT_FORMAT

NEWS_PROMPT = """
You are a news sentiment analyst evaluating ticker based on recent news. Title, publisher, and publish time are provided.

Here are recent news:
{news}

""" + ANALYST_OUTPUT_FORMAT

DECISION_OUTPUT_FORMAT = """
You must provide your decision as a structured output with the following fields:
- action: One of ["Buy", "Sell", "Hold"]
- shares: Number of shares to buy or sell, set 0 for hold
- justification: A brief explanation of your decision

Your response should be well-reasoned and consider all aspects of the analysis.
"""

PORTFOLIO_PROMPT = """
You are a portfolio manager making final trading decisions based on the signals from the analysts.

Here are the analyst signals:
{ticker_signals}

Current Price:
{current_price}

Maximum Shares Allowed For Purchases:
{max_shares}

Portfolio Cash: {portfolio_cash}
Current Positions: Value: {ticker_positions.value}, Shares: {ticker_positions.shares}

""" + DECISION_OUTPUT_FORMAT

PLANNER_PROMPT = """
You are a planner agent that decides which analysts to perform based on the your knowledge of the ticker and features of analysts.

Here is the ticker:
{ticker}

Here are the available analysts:
{analysts}

You must provide your decision as a structured output with the following fields:
- analysts: selected one or at most 5 analysts
- justification: brief explanation of your selection
"""