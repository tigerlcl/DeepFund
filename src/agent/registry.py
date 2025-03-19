from typing import Dict, Callable, List

from agent.technical import technical_agent
from agent.sentiment import sentiment_agent
from agent.fundamental import fundamental_agent
from agent.portfolio_manager import portfolio_agent

# Agent Key Identifiers
class AgentKey:
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    PORTFOLIO = "portfolio"


class AgentRegistry:
    """Registry for all agents."""
    
    # Define analyst configuration - signal source of truth
    AGENT_CONFIG = Dict[str, Callable]

    # Analyst KEYs
    ANALYST_KEYS = [
        AgentKey.TECHNICAL, 
        AgentKey.FUNDAMENTAL, 
        AgentKey.SENTIMENT, 
    ]

    @classmethod
    def get_agent_func_by_key(cls, key: str) -> Callable:
        """Get agent function by key."""
        return cls.AGENT_CONFIG.get(key)

    @classmethod
    def get_all_analyst_keys(cls) -> List[str]:
        """Get all analyst keys."""
        return cls.ANALYST_KEYS
    
    @classmethod
    def check_agent_key(cls, key: str) -> bool:
        """Check if an agent key is valid."""
        return key in cls.ANALYST_KEYS

    @classmethod
    def register_agent(cls, key: str, agent_func: Callable) -> None:
        """
        Register a new agent.
        
        Args:
            key: Unique identifier for the agent
            agent_func: Function that implements the agent's logic
        """
        cls.AGENT_CONFIG[key] = agent_func

    @classmethod
    def run_registry(cls):
        """Run the registry."""

        cls.register_agent(
            key=AgentKey.PORTFOLIO,
            agent_func=portfolio_agent
        )


        cls.register_agent(
            key=AgentKey.FUNDAMENTAL,
            agent_func=fundamental_agent
            )

        cls.register_agent(
            key=AgentKey.SENTIMENT,
            agent_func=sentiment_agent
        )
                
        cls.register_agent(
            key=AgentKey.TECHNICAL,
            agent_func=technical_agent
        )
        