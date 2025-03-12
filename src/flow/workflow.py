from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from typing import List, Optional
from flow.schema import FundState
from agent.registry import AgentRegistry, AgentKey
from util.logger import logger
from util.config import ConfigManager
from time import perf_counter


class AgentWorkflow:
    """Trading Decision Workflow."""

    def __init__(self, config: ConfigManager, portfolio: dict):
        self.workflow_config = config['workflow']
        self.trading_config = config['trading']
        self.llm_config = config['llm']

        # init portfolio
        self.init_portfolio = portfolio

        # init workflow variables
        self.selected_analysts = self._verify_analysts(self.workflow_config['analysts'])
        self.tickers = self.trading_config['tickers'] # to control the iteration

        self.agent_workflow = None

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
        workflow.add_node("analyst_router", self.analyst_router)

        # Add edges to connect nodes (Logically critical)
        workflow.add_edge(START, "ticker_iterator")
        
        # LangGraph auto-converts boolean to yes/no
        workflow.add_conditional_edges(
            "ticker_iterator",
            self.should_continue,
            {
                "yes": "analyst_router", 
                "no": AgentKey.PORTFOLIO
            } 
        )

        # Route to selected analysts
        for analyst in self.selected_analysts:
            # create node for each analyst
            agent_cfg = AgentRegistry.get_agent_by_key(analyst)
            workflow.add_node(analyst, agent_cfg["agent_func"])

            # route to analyst
            workflow.add_edge("analyst_router", analyst)
            # loop analyst back to ticket iterator
            workflow.add_edge(analyst, "ticker_iterator")
        
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
        
    def analyst_router(self, state: FundState):
        """Route the analyst to use."""
        return state
        
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
    

    def run(self):
        """Run the workflow."""

        start_time = perf_counter()

        # init FundState
        state = FundState(
            portfolio=self.init_portfolio,
            start_date =  self.trading_config['start_date'],
            end_date =  self.trading_config['end_date'],
            tickers = self.trading_config['tickers'],
            llm_config = self.llm_config,
        )

        try:
            logger.info("Invoking agent workflow")
            final_fund_state = self.agent_workflow.invoke(state)
            logger.info("Agent workflow completed successfully")

        except Exception as e:
            logger.error(f"Error running deep fund: {str(e)}")
            raise

        # log porfolio agent decisions
        for d in final_fund_state["agent_decisions"]:
            if d.agent_name == AgentKey.PORTFOLIO:
                logger.info(f"Decision for {d.ticker}: {d.action} | {d.confidence:.1f}%\nReason: {d.justification}")


        end_time = perf_counter()
        logger.info(f"Workflow completed in {end_time - start_time:.2f} seconds")

        return final_fund_state

