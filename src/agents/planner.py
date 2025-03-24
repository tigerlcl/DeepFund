from agents.registry import AgentRegistry
from graph.constants import AgentKey
from graph.prompt import PLANNER_PROMPT
from graph.state import agent_call
from util.logger import logger
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PlannerOutput(BaseModel):
    """Pydantic model for planner agent output."""
    analysts: List[str] = Field(
        description="List of selected analysts",
        default=AgentRegistry.get_all_analyst_keys()
    )
    justification: str = Field(
        description="Explanation for the analyst selection",
        default="No justification provided due to error"
    )

def planner_agent(ticker: str, llm_config: Dict[str, Any]) -> List[str]:
    """
    Planner agent that decides which analysts to use based on self-knowledge.
    It functions as a pre-requisite for the agentic workflow.
    """
    
    logger.log_agent_status(AgentKey.PLANNER, ticker, "Planning")
    analyst_info = AgentRegistry.get_analyst_info()

    prompt = PLANNER_PROMPT.format(
        ticker=ticker,
        analysts=analyst_info
    )

    result = agent_call(
        agent_name=AgentKey.PLANNER,
        ticker=ticker,
        prompt=prompt,
        llm_config=llm_config,
        pydantic_model=PlannerOutput
    )

    return result.analyst