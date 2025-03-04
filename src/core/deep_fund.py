"""Core deep fund execution logic."""

from typing import Dict, List, Any, Optional
from time import perf_counter
from langchain_core.messages import HumanMessage
from utils.logger import logger
from core.factory import WorkflowFactory
import json


class DeepFund:
    """Core deep fund execution logic."""

    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        portfolio: Dict[str, Any],
        show_reasoning: bool = False,
        selected_analysts: Optional[List[str]] = None,
        model_name: str = "gpt-4o",
        model_provider: str = "OpenAI",
    ):
        """Initialize the deep fund.
        
        Args:
            tickers: List of stock ticker symbols.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            portfolio: Portfolio configuration.
            show_reasoning: Whether to show reasoning from each agent.
            selected_analysts: List of selected analysts. If None, all analysts will be used.
            model_name: Name of the LLM model to use.
            model_provider: Provider of the LLM model.
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.portfolio = portfolio
        self.show_reasoning = show_reasoning
        self.selected_analysts = selected_analysts
        self.model_name = model_name
        self.model_provider = model_provider
        
        # Create workflow
        logger.info("Creating workflow")
        self.workflow = WorkflowFactory.create_workflow(selected_analysts)
        self.agent = self.workflow.compile()
        logger.info("Workflow compiled successfully")

    def run(self):
        """Run the deep fund and return the results."""
        logger.info(f"Starting deep fund run with tickers: {', '.join(self.tickers)}")
        logger.info(f"Date range: {self.start_date} to {self.end_date}")
        
        start_time = perf_counter()
        
        try:
            logger.info("Invoking agent workflow")
            final_state = self.agent.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content="Make trading decisions based on the provided data.",
                        )
                    ],
                    "data": {
                        "tickers": self.tickers,
                        "portfolio": self.portfolio,
                        "start_date": self.start_date,
                        "end_date": self.end_date,
                        "analyst_signals": {},
                    },
                    "metadata": {
                        "show_reasoning": self.show_reasoning,
                        "model_name": self.model_name,
                        "model_provider": self.model_provider,
                    },
                },
            )
            
            logger.info("Agent workflow completed successfully")
            
            # Parse the response
            decisions = self._parse_deep_fund_response(final_state["messages"][-1].content)
            
            result = {
                "decisions": decisions,
                "analyst_signals": final_state["data"]["analyst_signals"],
            }
            
            # Log execution time
            execution_time = perf_counter() - start_time
            logger.info(f"Total execution time: {execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running deep fund: {str(e)}")
            raise

    def _parse_deep_fund_response(self, response):
        """Parse the deep fund response."""
        try:
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parsing response: {response}")
            logger.error(f"Error details: {str(e)}")
            return None 