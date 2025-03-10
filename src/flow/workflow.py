from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from util.logger import logger
from util.models import get_model

from flow.schema import FundState
from agent.registry import AgentRegistry, AgentKey


class AgentWorkflow:
    """Trading Decision Workflow."""

    def __init__(self, config):

        self.config = config
        self.llm = get_model(self.config['llm'])
        
        # self.memory = None

    def build(self, state: FundState) -> StateGraph:
        """Build the workflow"""
        
        logger.info("Building workflow")

        # Create the workflow
        workflow = StateGraph(state)
        
        # create nodes for agents (including analyst and manager)
        for node_key, node_value in AgentRegistry.AGENT_CONFIG.items():
            workflow.add_node(node_key, node_value["agent_func"])

        # create functional nodes
        workflow.add_node("ticker_iterator", self.ticker_iterator)
        workflow.add_node("analyst_router", self.analyst_router)

        # Add edges to connect nodes (Logically critical)
        workflow.add_edge(START, "ticker_iterator")
        
        workflow.add_conditional_edges(
            "ticker_iterator",
            self.should_continue,
            {"yes": "analyst_router", "no": END} # LangGraph auto-converts boolean to yes/no
        )

        # Route to selected analysts based on analyst_router output
        workflow.add_conditional_edges(
            "analyst_router",
            lambda x: {"selected": x.analyst_in_the_loop},
            {analyst_key: analyst_key for analyst_key in AgentRegistry.get_all_analyst_keys()}
        )

        # bind analyst to manager
        for analyst_key in AgentRegistry.get_all_analyst_keys():
            workflow.add_edge(analyst_key, AgentKey.PORTFOLIO)
        
        workflow.add_edge(AgentKey.PORTFOLIO, END)

        # compile the workflow
        agent = workflow.compile()

        # show the workflow
        display(Image(workflow.get_graph().draw_mermaid_png(
            output_file_path=self.config['workflow']['image_path']
        )))

        logger.info("Workflow compiled successfully")
        
        return agent 
    
    def ticker_iterator(self, state: FundState):
        """Iterate over the tickers. Return will update the FundState."""

        current_ticker = state.tickers.pop(0)
        return {"ticker": current_ticker}
        
        
    def should_continue(self, state: FundState) -> bool:
        return len(state.tickers) > 0    
    

    def analyst_router(self):
        """Choose analyst agents to analyze the ticker. Return will update the FundState."""

        # If analysts are pre-configured
        selected_analysts = self.config['workflow']['analysts']

        # Check if all pre-configured keys are valid
        for analyst_key in selected_analysts:
            if not AgentRegistry.check_agent_key(analyst_key):
                logger.warning(f"Invalid analyst key: {analyst_key}, Removed for analysis.")
                selected_analysts.remove(analyst_key)

        # Otherwise, use all as default
        # TODO optimization, choose analysts based on ticker and context
        if selected_analysts is None:
            selected_analysts = AgentRegistry.get_all_analyst_keys()

        return {"analyst_in_the_loop": selected_analysts}
