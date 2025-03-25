# DeepFund

This project serves as an ideal solution to the below key question:

**Will LLM Be Professional At Fund Investment? A Live Arena perspective**

We evaluate the trading capability of LLM across various financial market given a standard environment. We present the performance in a nearly live view of trading arena. The LLM shall ingest external information and make trading decisions. 




> Disclaimer: This project is for educational and research purposes only, it does not actually trade.


## Setup
Pre-requisite: Install Conda (if not already installed): Go to [anaconda.com/download](https://www.anaconda.com/download/).

1. Clone the repository:
```bash
git clone https://github.com/tigerlcl/deepfund.git
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


## API Keys

### Financial Datasets
Financial data for AAPL, GOOGL, MSFT, NVDA, and TSLA is `free` and does not require an API key. For any other ticker, you will need to set the `FINANCIAL_DATASETS_API_KEY` in the .env file.


### LLM Providers
AUTH_KEYS for LLM providers are stored in the .env file.


## Running the System
Enter the `src` directory and run the `main.py` file:
```bash
cd src
python main.py --config default_config.yaml
# file default_config.yaml is in the config folder
```

<!-- **Example Output:** -->


## Project Structure 
```
deepfund/
├── src/
│   ├── main.py                   # Main entry point
│   ├── agents/                   # Agent build and registry
│   ├── apis/                     # APIs for external financial data
│   ├── llm/                     # LLM providers
│   ├── storage/                  # Storage (memory) for portfolio, worflow, etc
│   ├── util/                     # Utility functions and helpers
│   ├── graph/                    # Workflow, prompt and schema
│   ├── config/                   # Configuration files
│   ├── logs/                     # Log files (auto created)
├── environment.yml               # For Conda
├── README.md                     # Project documentation
├── ...
```


## Acknowledgements
- [AI Hedge Fund](https://github.com/virattt/ai-hedge-fund)
- [Financial Datasets](https://financialdatasets.ai/)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/tutorials/workflows)

## License
This project is licensed under the MIT License - see the LICENSE file for details.
