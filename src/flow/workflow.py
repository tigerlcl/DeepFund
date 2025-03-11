from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from util.logger import logger
from typing import List, Optional
from flow.schema import FundState
from agent.registry import AgentRegistry, AgentKey


class AgentWorkflow:
    """Trading Decision Workflow."""

    def __init__(self, config):
        self.workflow_config = config['workflow']
        self.selected_analysts = self._verify_analysts(self.workflow_config['analysts'])
        self.tickers = config['trading']['tickers'] # to control the iteration

    def build(self, state: FundState) -> StateGraph:
        """Build the workflow"""
        
        logger.info("Building workflow")

        # Create the workflow
        workflow = StateGraph(state)
        
        # create node for portfolio manager
        agent_cfg = AgentRegistry.get_agent_by_key(AgentKey.PORTFOLIO)
        workflow.add_node(AgentKey.PORTFOLIO, agent_cfg["agent_func"])

        # create functional nodes
        workflow.add_node("ticker_iterator", self.ticker_iterator)

        # Add edges to connect nodes (Logically critical)
        workflow.add_edge(START, "ticker_iterator")
        
        # LangGraph auto-converts boolean to yes/no
        workflow.add_conditional_edges(
            "ticker_iterator",
            self.should_continue,
            {
                "yes": "analyst_selector", 
                "no": AgentKey.PORTFOLIO
            } 
        )

        # Route to selected analysts
        for analyst in self.selected_analysts:
            # create node for each analyst
            agent_cfg = AgentRegistry.get_agent_by_key(analyst)
            workflow.add_node(analyst, agent_cfg["agent_func"])

            # link analyst to portfolio manager
            workflow.add_edge(analyst, AgentKey.PORTFOLIO)
        

        # Route to portfolio manager
        workflow.add_edge(AgentKey.PORTFOLIO, END)

        # compile the workflow
        agent = workflow.compile()

        # show the workflow
        display(Image(workflow.get_graph().draw_mermaid_png(
            output_file_path=self.workflow_config['image_path']
        )))

        logger.info("Workflow compiled successfully")
        
        return agent 
    
    def ticker_iterator(self):
        """Iterate over the tickers. Return will update the FundState."""

        current_ticker = self.tickers.pop(0)
        return {"ticker": current_ticker}
        
        
    def should_continue(self) -> bool:
        return len(self.tickers) > 0    

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