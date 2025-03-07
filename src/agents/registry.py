from typing import Dict, Optional, Callable, Union, List, Tuple
from agents import technical_analyst_agent, fundamentals_agent, sentiment_agent, valuation_agent


class AnalystRegistry:
    """Registry for analyst agents."""
    
    # Define analyst configuration - single source of truth
    ANALYST_CONFIG = {
        "technical_analyst": {
            "display_name": "Technical Analyst",
            "agent_func": technical_analyst_agent,
            "order": 0,
        },
        "fundamentals_analyst": {
            "display_name": "Fundamentals Analyst",
            "agent_func": fundamentals_agent,
            "order": 1,
        },
        "sentiment_analyst": {
            "display_name": "Sentiment Analyst",
            "agent_func": sentiment_agent,
            "order": 2,
        },
        "valuation_analyst": {
            "display_name": "Valuation Analyst",
            "agent_func": valuation_agent,
            "order": 3,
        },
    }
    
    @classmethod
    def get_all_analysts(cls) -> Dict[str, Dict[str, Union[str, Callable, int]]]:
        """Get all registered analysts."""
        return cls.ANALYST_CONFIG
    
    @classmethod
    def get_analyst_by_key(cls, key: str) -> Optional[Dict[str, Union[str, Callable, int]]]:
        """Get analyst configuration by key."""
        return cls.ANALYST_CONFIG.get(key)
    
    @classmethod
    def get_analyst_node_mapping(cls) -> Dict[str, Tuple[str, Callable]]:
        """Get the mapping of analyst keys to their (node_name, agent_func) tuples."""
        return {
            key: (f"{key}_agent", config["agent_func"])
            for key, config in cls.ANALYST_CONFIG.items()
        }
    
    @classmethod
    def register_analyst(cls, key: str, display_name: str, agent_func: Callable, order: int) -> None:
        """
        Register a new analyst.
        
        Args:
            key: Unique identifier for the analyst
            display_name: Human-readable name for the analyst
            agent_func: Function that implements the analyst's logic
            order: Order in which the analyst should be executed (lower numbers first)
        """
        cls.ANALYST_CONFIG[key] = {
            "display_name": display_name,
            "agent_func": agent_func,
            "order": order,
        }
    
    @classmethod
    def get_sorted_analysts(cls) -> List[Tuple[str, Dict[str, Union[str, Callable, int]]]]:
        """Get all analysts sorted by their order."""
        return sorted(
            cls.ANALYST_CONFIG.items(),
            key=lambda item: item[1]["order"]
        ) 