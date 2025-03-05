from typing import Dict, List, Optional, Callable, Any, Union
from typing_extensions import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from agents import technical_analyst_agent, fundamentals_agent, sentiment_agent, valuation_agent
from agents.risk_manager import risk_management_agent
from agents.portfolio_manager import portfolio_management_agent
from util.logger import logger
import json
import operator


def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries."""
    return {**a, **b}


class AgentState(TypedDict):
    """State definition for the agent workflow."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    data: Annotated[Dict[str, Any], merge_dicts]
    metadata: Annotated[Dict[str, Any], merge_dicts]


class AgentReasoningLogger:
    """Class to handle agent reasoning logging."""
    
    @staticmethod
    def log_reasoning(output: Any, agent_name: str) -> None:
        """
        Log agent reasoning to the logger.
        
        Args:
            output: The output to log
            agent_name: The name of the agent
        """
        logger.info(f"Agent reasoning from {agent_name}")
        
        serializable_output = AgentReasoningLogger._convert_to_serializable(output)
        
        if isinstance(serializable_output, (dict, list)):
            logger.debug(json.dumps(serializable_output, indent=2))
        else:
            try:
                # Parse the string as JSON and pretty print it
                parsed_output = json.loads(serializable_output)
                logger.debug(json.dumps(parsed_output, indent=2))
            except (json.JSONDecodeError, TypeError):
                # Fallback to original string if not valid JSON
                logger.debug(serializable_output)
    
    @staticmethod
    def _convert_to_serializable(obj: Any) -> Any:
        """Convert an object to a JSON-serializable format."""
        if hasattr(obj, "to_dict"):  # Handle Pandas Series/DataFrame
            return obj.to_dict()
        elif hasattr(obj, "__dict__"):  # Handle custom objects
            return obj.__dict__
        elif isinstance(obj, (int, float, bool, str)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [AgentReasoningLogger._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: AgentReasoningLogger._convert_to_serializable(value) for key, value in obj.items()}
        else:
            return str(obj)  # Fallback to string representation


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
    def get_analyst_node_mapping(cls) -> Dict[str, tuple]:
        """Get the mapping of analyst keys to their (node_name, agent_func) tuples."""
        return {
            key: (f"{key}_agent", config["agent_func"])
            for key, config in cls.ANALYST_CONFIG.items()
        }
    
    @classmethod
    def register_analyst(cls, key: str, display_name: str, agent_func: Callable, order: int) -> None:
        """Register a new analyst."""
        cls.ANALYST_CONFIG[key] = {
            "display_name": display_name,
            "agent_func": agent_func,
            "order": order,
        }


class WorkflowManager:
    """Manager for creating and handling agent workflows."""
    
    # @staticmethod
    # def _start_node(state: AgentState) -> AgentState:
    #     """Initialize the workflow with the input message."""
    #     return state
    
    @classmethod
    def create_workflow(cls, selected_analysts: Optional[List[str]] = None) -> StateGraph:
        """
        Create a workflow with the orchestrator-worker architecture.
        
        Args:
            selected_analysts: List of analyst keys to include in the workflow.
                If None, all analysts will be included.
                
        Returns:
            A compiled StateGraph workflow.
        """
        # If no analysts are selected, use all available analysts
        if selected_analysts is None:
            selected_analysts = list(AnalystRegistry.get_all_analysts().keys())
        
        # Create the workflow
        workflow = StateGraph(AgentState)
        
        # Add the start node
        workflow.add_node("start_node", START)
        
        # Get analyst nodes from the registry
        analyst_nodes = AnalystRegistry.get_analyst_node_mapping()
        
        # Add worker nodes (analysts)
        for analyst_key in selected_analysts:
            if analyst_key in analyst_nodes:
                node_name, node_func = analyst_nodes[analyst_key]
                workflow.add_node(node_name, node_func)
                workflow.add_edge("start_node", node_name)
        
        # Add orchestrator nodes (risk manager and portfolio manager)
        workflow.add_node("risk_management_agent", risk_management_agent)
        workflow.add_node("portfolio_management_agent", portfolio_management_agent)
        
        # Connect worker nodes to the risk management orchestrator
        for analyst_key in selected_analysts:
            if analyst_key in analyst_nodes:
                node_name = analyst_nodes[analyst_key][0]
                workflow.add_edge(node_name, "risk_management_agent")
        
        # Connect risk management to portfolio management
        workflow.add_edge("risk_management_agent", "portfolio_management_agent")
        
        # Connect portfolio management to the end of the workflow
        workflow.add_edge("portfolio_management_agent", END)
        
        # Set the entry point
        workflow.set_entry_point("start_node")
        
        logger.info("Workflow created successfully")
        return workflow 