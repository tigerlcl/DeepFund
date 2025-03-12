# agent helper function

from typing import Any, Dict, List, Optional
from util.logger import logger
from util.llm_model import get_model
from .schema import Decision

def make_decision(
    prompt: Any,
    llm_config: Dict[str, Any],
    agent_name: str,
    ticker: str,
    max_retries: int = 3
) -> Decision:
    """
    Makes an LLM call with retry logic.
    
    Args:
        prompt: The prompt to send to the LLM
        llm_config: Configuration for the LLM
        agent_name: The name of the agent for logging
        ticker: The ticker of the stock for logging
        max_retries: Maximum number of retries (default: 3)
        
    Returns:
        An instance of the Decision with defaults if error occurs
    """
        
    # Get the model
    llm = get_model(llm_config)
    llm = llm.with_structured_output(Decision)
    
    # Call the LLM with retries
    for attempt in range(max_retries):
        try:
            # Log the attempt
            logger.log_agent_status(agent_name, ticker, f"Calling LLM (attempt {attempt + 1}/{max_retries})")
            result = llm.invoke(prompt)

            return Decision(agent_name=agent_name, ticker=ticker, action=result.action, confidence=result.confidence, justification=result.justification)
        
        except Exception as e:
            logger.log_agent_status(agent_name, ticker, f"Error - retry {attempt + 1}/{max_retries}")
            if attempt == max_retries - 1:
                logger.error(f"Error in LLM call after {max_retries} attempts: {e}")
                # Use model's default values when error occurs
                return Decision(agent_name=agent_name, ticker=ticker)
            
def search_decision(decisions: List[Decision], agent_name: str, ticker: str) -> Optional[Decision]:
    """Find a decision by agent name and ticker."""
    return next(
        (d for d in decisions 
        if d.agent_name == agent_name and d.ticker == ticker),
        None
    )