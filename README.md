# DeepFund

This project serves as an ideal solution to the below key question:

**Will LLM Be Professional At Fund Investment? A Live Arena perspective**

We evaluate the trading capability of LLM across various financial market given a standard environment. We present the performance in a nearly live view of trading arena. The LLM shall ingest external information and make trading decisions. 


## Disclaimer

This project is for **educational and research purposes only, it does not actually trade.** 


## Overview
This environment covers 5 key services, which are Data Ingestion, Trading Simulator, Analytics, Live Arena and Storage.

DONE: Trading Simulator

TODO: Data Ingestion | Analytics | Live Arena | Storage



## Setup
Pre-requisite: Install Conda (if not already installed): Go to [anaconda.com/download](https://www.anaconda.com/download/).

1. Clone the repository:
```bash
git clone https://github.com/IatomicreactorI/deepfund.git
cd deepfund
```

2. Create an virtual env from the conda env configuration file:
```bash
conda env create -f environment.yml
```

3. Set up environment variables:
```bash
# Create .env file for your API keys
cp .env.example .env
```

**Important**: You must set API keys for the services to work.  If you want to use LLMs from all providers, you will need to set all API keys.

Financial data for AAPL, GOOGL, MSFT, NVDA, and TSLA is `free` and does not require an API key.

For any other ticker, you will need to set the `FINANCIAL_DATASETS_API_KEY` in the .env file.

## Usage

### Running the System
```bash
python src/main.py --ticker NVDA
```

**Example Output:**
<img width="992" alt="Screenshot 2025-01-06 at 5 50 17 PM" src="https://github.com/user-attachments/assets/e8ca04bf-9989-4a7d-a8b4-34e04666663b" />

You can also specify a `--show-reasoning` flag to print the reasoning of each agent to the console.

```bash
python src/main.py --ticker AAPL,MSFT,NVDA --show-reasoning
```
You can optionally specify the start and end dates to make decisions for a specific time period.

```bash
python src/main.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 
```

### Running the Backtester

```bash
python src/backtester.py --ticker AAPL,MSFT,NVDA
```

**Example Output:**
<img width="941" alt="Screenshot 2025-01-06 at 5 47 52 PM" src="https://github.com/user-attachments/assets/00e794ea-8628-44e6-9a84-8f8a31ad3b47" />

You can optionally specify the start and end dates to backtest over a specific time period.

```bash
python src/backtester.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01
```

## Project Structure 
```
deepfund/
├── src/
│   ├── agents/                   # Agent definitions and workflow
│   │   ├── bill_ackman.py        # Bill Ackman agent
│   │   ├── fundamentals.py       # Fundamental analysis agent
│   │   ├── portfolio_manager.py  # Portfolio management agent
│   │   ├── risk_manager.py       # Risk management agent
│   │   ├── sentiment.py          # Sentiment analysis agent
│   │   ├── technicals.py         # Technical analysis agent
│   │   ├── valuation.py          # Valuation analysis agent
│   │   ├── warren_buffett.py     # Warren Buffett agent
│   ├── tools/                    # Agent tools
│   │   ├── api.py                # API tools
│   ├── backtester.py             # Backtesting tools
│   ├── main.py # Main entry point
├── environment.yml # For Conda
├── ...
```


## Acknowledgements
- [AI Hedge Fund](https://github.com/virattt/ai-hedge-fund)
- [Financial Datasets](https://financialdatasets.ai/)
- [LangChain](https://langchain.com/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
