from typing import Dict, List, Optional, Any
from typing_extensions import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from agents.registry import AnalystRegistry
from util.logger import logger
import operator


def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries."""
    return {**a, **b}


class AgentState(TypedDict):
    """State definition for the agent workflow."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    data: Annotated[Dict[str, Any], merge_dicts]
    metadata: Annotated[Dict[str, Any], merge_dicts]


class AgentWorkflow:
    """Workflow for creating and handling communication among agents."""

    def __init__(self, config):
        # TODO
        self.config = config
    

    def orchestrator(self, state: AgentState) -> AgentState:
        """Orchestrator that orchestrates the workflow."""
        return state
    
    
    def compile(self, selected_analysts: Optional[List[str]] = None) -> StateGraph:
        """Create a workflow with the orchestrator-worker architecture."""
        
        logger.info("Creating workflow")
        # Create the workflow
        workflow = StateGraph(AgentState)
        
        # # Add the start node
        # workflow.add_node("orchestrator", cls.orchestrator)
        
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

        agent = workflow.compile()
        
        logger.info("Workflow compiled successfully")
        

        return agent 