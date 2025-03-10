from typing import Dict, Callable, Union, List

from .technical import technical_agent
from .fundamental import fundamental_agent
# from .sentiment import sentiment_agent
# from .valuation import valuation_agent
from .portfolio import portfolio_agent

# Agent Key Identifiers
class AgentKey:
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    VALUATION = "valuation"
    PORTFOLIO = "portfolio"


class AgentRegistry:
    """Registry for all agents."""
    
    # Define analyst configuration - signal source of truth
    AGENT_CONFIG = {}

    # Analyst KEYs
    ANALYST_KEYS = [
        AgentKey.TECHNICAL, 
        AgentKey.FUNDAMENTAL, 
        AgentKey.SENTIMENT, 
        AgentKey.VALUATION,
    ]

    @classmethod
    def get_agent_by_key(cls, key: str) -> Dict[str, Union[str, str, Callable]]:
        """Get agent configuration by key."""
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
    def register_agent(cls, key: str, display_name: str, agent_func: Callable) -> None:
        """
        Register a new agent.
        
        Args:
            key: Unique identifier for the agent
            display_name: Human-readable name for the agent
            agent_func: Function that implements the agent's logic
        """
        cls.AGENT_CONFIG[key] = {
            "display_name": display_name,
            "agent_func": agent_func,
        }

    @classmethod
    def run_registry(cls):
        """Run the registry."""

        cls.register_agent(
            key=AgentKey.PORTFOLIO,
            display_name="Portfolio Manager",

            agent_func=portfolio_agent
        )

        cls.register_agent(
            key=AgentKey.FUNDAMENTAL,
            display_name="Fundamental Analyst",
            agent_func=fundamental_agent
            )

        # cls.register_agent(
        #     key=AgentKey.SENTIMENT,
        #     display_name="Sentiment Analyst",
        #     agent_func=sentiment_agent
        # )
        
        # cls.register_agent(
        #     key=AgentKey.VALUATION,
        #     display_name="Valuation Analyst",
        #     agent_func=valuation_agent
        # )
        
        cls.register_agent(
            key=AgentKey.TECHNICAL,
            display_name="Technical Analyst",
            agent_func=technical_agent
        )
        