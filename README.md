# DeepFund

[![arXiv](https://img.shields.io/badge/arXiv-2503.18313-<COLOR>.svg)](https://arxiv.org/abs/2503.18313)

This project serves as an ideal solution to the below key question:

**Will LLM Be Professional At Fund Investment? A Live Arena perspective**

We evaluate the trading capability of LLM across various financial market given a standard environment. We present the performance in a nearly live view of trading arena. The LLM shall ingest external information and make trading decisions. 


> Disclaimer: This project is for educational and research purposes only, it does not actually trade.

## Market Coverage
- US Stock (Magnificent Seven)
- More ...


## Setup
Pre-requisite: Install Conda (if not already installed): Go to [anaconda.com/download](https://www.anaconda.com/download/).

1. Clone the repository:
```bash
git clone https://github.com/tigerlcl/deepfund.git
cd deepfund
```

2. Create a virtual env from the env configuration file:
```bash
conda env create -f environment.yml
```

3. Set up environment variables:
```bash
# Create .env file for your API keys
cp .env.example .env
```

## Running the System
Enter the `src` directory and run the `main.py` file with configuration:
```bash
cd src
python main.py --config xxx.yaml
```
> configs are saved in `src/config`

Config file sample:
```yaml
# Trading settings
tickers:
  - MSFT
  - NVDA

# Analysts to run, refer to graph.constants.py
workflow_analysts:
  - fundamental
  - technical
  - insider
  - news

# LLM model settings, refer to llm/inference.py: LLMConfig
llm:
  provider: "DeepSeek" 
  model: "deepseek-chat" # DeepSeek-V3
```

Running output (NVDA on Date 2025-03-28, Fundamental + News Analyst, DeepSeek-V3)
```log
INFO - NVDA workflow compiled successfully
INFO - Agent: fundamental | Ticker: NVDA | Status: Fetching financial metrics
INFO - Agent: news | Ticker: NVDA | Status: Fetching company news
INFO - Agent: fundamental | Ticker: NVDA | Signal: Bullish | Justification: The analysis indicates strong bullish signals across all key metrics: Profitability, Growth, and Financial Health. This comprehensive strength suggests a robust financial position and potential for future outperformance.
INFO - Agent: news | Ticker: NVDA | Signal: Bullish | Justification: The majority of the recent news articles about Nvidia (NVDA) are overwhelmingly positive, highlighting strong fundamentals, growth potential, and bullish endorsements from analysts and institutions. Titles such as 'Nvidia Stock Is Down Over 20% From Its All-Time High. Here's Why It Could Soar by the End of 2025' and 'Bank of America: NVDA Will Ultimately Head Higher, Driven by Very Strong Fundamentals' suggest optimism about the stock's future performance. Additionally, mentions of Nvidia's role in AI and partnerships (e.g., Cisco deal) further bolster the bullish sentiment. While there is one neutral piece about a shortage of Nvidia chips in China, it does not outweigh the positive sentiment from the other articles.
INFO - Agent: portfolio manager | Ticker: NVDA | Status: Making trading decisions
INFO - Decision for NVDA: Buy | Shares: 2 | Price: 110.3 | Reason: Despite the overwhelmingly bullish signals from the analysts, the remaining shares allowed for purchases are limited to 2.0. Given the strong fundamentals, growth potential, and positive sentiment, it is prudent to fully utilize the remaining allocation to capitalize on the bullish trend.
INFO - NVDA position update: cashflow=74819.08 positions={'NVDA': Position(value=220.6, shares=226), ...}
```
> Running fact: time 36 sec, LLM cost: 0.01 CNY

## Project Structure 
```
deepfund/
├── src/
│   ├── main.py                   # Main entry point
│   ├── agents/                   # Agent build and registry
│   ├── apis/                     # APIs for external financial data
│   ├── llm/                      # LLM providers
│   ├── util/                     # Utility functions and helpers
│   ├── graph/                    # Workflow, prompt and schema
│   ├── config/                   # Configuration files
│   ├── logs/                     # Log files (auto created)
├── environment.yml               # For Conda
├── README.md                     # Project documentation
├── ...
```


# Data Source Dependency
- Financial Dataset API
  - Fundamental Analyst
- Alpha Vantage API
  - Insider Trades Analyst
  - Technical Analyst
- YFinance API
  - News Analysts
  - Portfolio Manager


## Acknowledgements
The project get inspiration from the following projects:
- [AI Hedge Fund](https://github.com/virattt/ai-hedge-fund)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/tutorials/workflows)
- [OpenManus](https://github.com/mannaandpoem/OpenManus)


## Roadmap
MCPify Deepfund


## License
This project is licensed under the MIT License - see the LICENSE file for details.
