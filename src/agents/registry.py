from typing import Dict, Callable, List

from agents.technical import technical_agent
from agents.sentiment import sentiment_agent
from agents.fundamental import fundamental_agent
from agents.portfolio_manager import portfolio_agent
from agents.planner import planner_agent

# Agent Key Identifiers
class AgentKey:
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    PORTFOLIO = "portfolio"
    PLANNER = "planner"


class AgentRegistry:
    """Registry for all agents."""
    
    # Define analyst configuration - signal source of truth
    agent_func_mapping = Dict[str, Callable]
    agent_doc_mapping = Dict[str, str]

    # Analyst KEYs
    ANALYST_KEYS = [
        AgentKey.TECHNICAL, 
        AgentKey.FUNDAMENTAL, 
        AgentKey.SENTIMENT, 
    ]

    @classmethod
    def get_agent_func_by_key(cls, key: str) -> Callable:
        """Get agent function by key."""
        return cls.agent_func_mapping.get(key)

    @classmethod
    def get_all_analyst_keys(cls) -> List[str]:
        """Get all analyst keys."""
        return cls.ANALYST_KEYS
    
    @classmethod
    def check_agent_key(cls, key: str) -> bool:
        """Check if an agent key is valid."""
        return key in cls.ANALYST_KEYS

    @classmethod
    def register_agent(cls, key: str, agent_func: Callable, agent_doc: str) -> None:
        """
        Register a new agent.
        
        Args:
            key: Unique identifier for the agent
            agent_func: Function that implements the agent logic
            agent_doc: short description of the agent
        """
        cls.agent_func_mapping[key] = agent_func
        cls.agent_doc_mapping[key] = agent_doc

    @classmethod
    def run_registry(cls):
        """Run the registry."""

        cls.register_agent(
            key=AgentKey.PORTFOLIO,
            agent_func=portfolio_agent,
            agent_doc="Portfolio manager making final trading decisions based on the signals from the analysts."
        )

        cls.register_agent(
            key=AgentKey.PLANNER,
            agent_func=planner_agent,
            agent_doc="Planner agent that decides which analysts to use based on self-knowledge."
        )

        cls.register_agent(
            key=AgentKey.FUNDAMENTAL,
            agent_func=fundamental_agent,
            agent_doc="Fundamental analysis specialist focusing on company financial health and valuation."
            )

        cls.register_agent(
            key=AgentKey.SENTIMENT,
            agent_func=sentiment_agent,
            agent_doc="Market sentiment specialist analyzing insider activity and news sentiment."
        )
                
        cls.register_agent(
            key=AgentKey.TECHNICAL,
            agent_func=technical_agent,
            agent_doc="Technical analysis specialist using multiple technical analysis strategies."
        )

    @classmethod
    def get_analyst_info(cls) -> str:
        """Get analyst info."""
        return "\n".join([f"{key}: {cls.agent_doc_mapping[key]}" for key in cls.ANALYST_KEYS])