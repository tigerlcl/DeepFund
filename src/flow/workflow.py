from agent.registry import AgentRegistry

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from util.logger import logger
from flow.schema import FundState, TickerSignal
from util.models import get_model



class AgentWorkflow:
    """Trading Decision Workflow that orchestrates a set of analyst agents.
    """

    def __init__(self, config):
        self.config = config

        # Get LLM model
        llm = get_model(self.config['llm'])
        self.planner = llm.with_structured_output(TickerSignal)


    def orchestrator(self, state: FundState) -> FundState:
        """Orchestrator that orchestrates the workflow."""

        # Generate queries
        ticker_signal = self.planner.invoke(
            HumanMessage(content="Make trading decisions based on the provided ticker.")
        )

        return {"signals": [ticker_signal]}
    
    def compile(self) -> StateGraph:
        """Create a workflow with the orchestrator-worker architecture."""
        
        logger.info("Building workflow")

        # Create the workflow
        workflow = StateGraph(FundState)
        
        # connect nodes and edges
        workflow.add_node("orchestrator", self.orchestrator)
        workflow.add_edge(START, "orchestrator")
        

        # Add portfolio management node
        pa = AgentRegistry.get_portfolio_agent()
        workflow.add_node(pa["node_name"], pa["agent_func"])
        workflow.add_edge(pa["node_name"], END)
        
        # Add (selected) analysts nodes
        for analyst_key in self.config['analysts']:
            node_name, node_func = AgentRegistry.get_analyst_by_key(analyst_key)
            workflow.add_node(node_name, node_func)
            workflow.add_edge("orchestrator", node_name)
            workflow.add_edge(node_name, pa["node_name"])
        

        agent = workflow.compile()
        
        logger.info("Workflow compiled successfully")
        

        return agent 