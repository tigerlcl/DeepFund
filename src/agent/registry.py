from typing import Dict, Optional, Callable, Union, Tuple


class AgentRegistry:
    """Registry for all agents."""
    
    # Define analyst configuration - single source of truth
    AGENT_CONFIG = {}
    
    
    @classmethod
    def get_agent_by_key(cls, key: str) -> Optional[Dict[str, Union[str, Callable, int]]]:
        """Get agent configuration by key."""
        return cls.AGENT_CONFIG.get(key)

    
    @classmethod
    def get_portfolio_agent(cls) -> Tuple[str, Callable]:
        """Get the portfolio management agent."""
        return cls.AGENT_CONFIG["portfolio"]


    @classmethod
    def register_agent(cls, key: str, node_name: str, display_name: str, agent_func: Callable) -> None:
        """
        Register a new agent.
        
        Args:
            key: Unique identifier for the  
            node_name: Graph node name for the agent
            display_name: Human-readable name for the agent
            agent_func: Function that implements the agent's logic
        """
        cls.AGENT_CONFIG[key] = {
            "node_name": node_name,
            "display_name": display_name,
            "agent_func": agent_func,
        }