"""Factory for creating workflow graphs."""

from typing import List, Dict, Any, Callable, Tuple
from core.state import AgentState
from langgraph.graph import StateGraph, END
from agents import get_analyst_nodes
from agents.risk_manager import risk_management_agent
from agents.portfolio_manager import portfolio_management_agent
from core.logger import logger


class WorkflowFactory:
    """Factory for creating workflow graphs."""

    @staticmethod
    def create_workflow(selected_analysts: List[str] = None) -> StateGraph:
        """Create a workflow with selected analysts.
        
        Args:
            selected_analysts: List of analyst keys to include in the workflow.
                If None, all analysts will be included.
                
        Returns:
            A compiled StateGraph workflow.
        """
        workflow = StateGraph(AgentState)
        workflow.add_node("start_node", WorkflowFactory._start_node)

        # Get analyst nodes from the configuration
        analyst_nodes = get_analyst_nodes()

        # Default to all analysts if none selected
        if selected_analysts is None:
            selected_analysts = list(analyst_nodes.keys())
            
        # Add selected analyst nodes
        for analyst_key in selected_analysts:
            if analyst_key in analyst_nodes:
                node_name, node_func = analyst_nodes[analyst_key]
                workflow.add_node(node_name, node_func)
                workflow.add_edge("start_node", node_name)
                logger.info(f"Added analyst node: {node_name}")
            else:
                logger.warning(f"Analyst not found: {analyst_key}")

        # Always add risk and portfolio management
        workflow.add_node("risk_management_agent", risk_management_agent)
        workflow.add_node("portfolio_management_agent", portfolio_management_agent)

        # Connect selected analysts to risk management
        for analyst_key in selected_analysts:
            if analyst_key in analyst_nodes:
                node_name = analyst_nodes[analyst_key][0]
                workflow.add_edge(node_name, "risk_management_agent")

        workflow.add_edge("risk_management_agent", "portfolio_management_agent")
        workflow.add_edge("portfolio_management_agent", END)

        workflow.set_entry_point("start_node")
        logger.info("Workflow created successfully")
        return workflow

    @staticmethod
    def _start_node(state: AgentState) -> AgentState:
        """Initialize the workflow with the input message."""
        return state 