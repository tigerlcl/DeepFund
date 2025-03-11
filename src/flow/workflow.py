from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from util.logger import logger

from flow.schema import FundState
from agent.registry import AgentRegistry, AgentKey


class AgentWorkflow:
    """Trading Decision Workflow."""

    def __init__(self, config):
        self.config = config
        self.selected_analysts = self._analyst_selector()

    def build(self, state: FundState) -> StateGraph:
        """Build the workflow"""
        
        logger.info("Building workflow")

        # Add LLM config to state
        state["llm_config"] = self.config['llm']

        # Create the workflow
        workflow = StateGraph(state)
        
        # create node for manager
        for manager_key in AgentRegistry.get_all_manager_keys():
            agent_cfg = AgentRegistry.get_agent_by_key(manager_key)
            workflow.add_node(manager_key, agent_cfg["agent_func"])

        # create functional nodes
        workflow.add_node("ticker_iterator", self.ticker_iterator)
        workflow.add_node("analyst_selector") # no action

        # Add edges to connect nodes (Logically critical)
        workflow.add_edge(START, "ticker_iterator")
        
        workflow.add_conditional_edges(
            "ticker_iterator",
            self.should_continue,
            {"yes": "analyst_selector", "no": END} # LangGraph auto-converts boolean to yes/no
        )

        # Route to selected analysts based on analyst_router output
        for analyst in self.selected_analysts:
            # create node for each analyst
            agent_cfg = AgentRegistry.get_agent_by_key(analyst)
            workflow.add_node(analyst, agent_cfg["agent_func"])
            
            workflow.add_edge("analyst_selector", analyst)
            workflow.add_edge(analyst, AgentKey.RISK) # analyst signals to risk manager   
        
        # risk manager to portfolio manager
        workflow.add_edge(AgentKey.RISK, AgentKey.PORTFOLIO)
        
        # portfolio manager to end
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
    

    def _analyst_selector(self):
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

        self.selected_analysts = selected_analysts
