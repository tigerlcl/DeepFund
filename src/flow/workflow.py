from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from util.logger import logger
from typing import List, Optional
from flow.schema import FundState
from agent.registry import AgentRegistry, AgentKey


class AgentWorkflow:
    """Trading Decision Workflow."""

    def __init__(self, config):
        self.llm_config = config['llm']
        self.workflow_config = config['workflow']
        self.selected_analysts = self._verify_analysts(self.workflow_config['analysts'])

    def build(self, state: FundState) -> StateGraph:
        """Build the workflow"""
        
        logger.info("Building workflow")

        # Create the workflow
        workflow = StateGraph(state)
        
        # create node for manager
        for manager_key in AgentRegistry.get_all_manager_keys():
            agent_cfg = AgentRegistry.get_agent_by_key(manager_key)
            workflow.add_node(manager_key, agent_cfg["agent_func"])

        # create functional nodes
        workflow.add_node("ticker_iterator", self.ticker_iterator)

        # Add edges to connect nodes (Logically critical)
        workflow.add_edge(START, "ticker_iterator")
        
        workflow.add_conditional_edges(
            "ticker_iterator",
            self.should_continue,
            {"yes": "analyst_selector", "no": END} # LangGraph auto-converts boolean to yes/no
        )

        # Route to selected analysts
        for analyst in self.selected_analysts:
            # create node for each analyst
            agent_cfg = AgentRegistry.get_agent_by_key(analyst)
            workflow.add_node(analyst, agent_cfg["agent_func"])
            
            workflow.add_edge("analyst_selector", analyst)
            workflow.add_edge(analyst, AgentKey.RISK) # analyst signals to risk manager   
        
        # risk manager to portfolio manager
        workflow.add_edge(AgentKey.RISK, AgentKey.PORTFOLIO)

        # Add a loop back to ticker_iterator after portfolio manager
        workflow.add_edge(AgentKey.PORTFOLIO, "ticker_iterator")

        # compile the workflow
        agent = workflow.compile()

        # show the workflow
        display(Image(workflow.get_graph().draw_mermaid_png(
            output_file_path=self.workflow_config['image_path']
        )))

        logger.info("Workflow compiled successfully")
        
        return agent 
    
    def ticker_iterator(self, state: FundState):
        """Iterate over the tickers. Return will update the FundState."""

        current_ticker = state.tickers.pop(0)
        return {"ticker": current_ticker}
        
        
    def should_continue(self, state: FundState) -> bool:
        return len(state.tickers) > 0    

    def _verify_analysts(self, analysts: Optional[List[str]] = None) -> List[str]:
        """Verify the analysts are valid."""
        for analyst in analysts:
            if not AgentRegistry.check_agent_key(analyst):
                logger.warning(f"Invalid analyst key: {analyst}, Removed for analysis.")
                analysts.remove(analyst)

        # Otherwise, use all as default
        if analysts is None:
            analysts = AgentRegistry.get_all_analyst_keys()

        return analysts