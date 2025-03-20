from typing import List, Dict, Any
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from graph.schema import FundState
from graph.constants import AgentKey
from agents.registry import AgentRegistry
from util.logger import logger
from time import perf_counter


class AgentWorkflow:
    """Trading Decision Workflow."""

    def __init__(
            self, 
            config: Dict[str, Any], 
            portfolio: dict, 
            tickers: list
            ):
        self.workflow_config = config['workflow']
        self.trading_config = config['trading']
        self.llm_config = config['llm']
        self.tickers = tickers
        self.init_portfolio = portfolio


    def build(self, state: FundState, connected_analysts: List[str]) -> StateGraph:
        """Build the workflow"""
        
        logger.info("Building workflow")

        # Create the workflow
        workflow = StateGraph(state)
        
        # create node for portfolio manager
        portfolio_agent = AgentRegistry.get_agent_func_by_key(AgentKey.PORTFOLIO)
        workflow.add_node(AgentKey.PORTFOLIO, portfolio_agent)

        # create functional nodes
        workflow.add_node("analyst_router", self.analyst_router)
        workflow.add_edge(START, "analyst_router")
        
        # create node for each analyst and add edge
        for analyst in connected_analysts:
            agent_func = AgentRegistry.get_agent_func_by_key(analyst)
            workflow.add_node(analyst, agent_func)

            # route to analyst
            workflow.add_edge("analyst_router", analyst)

            # route to portfolio manager
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

        
    def analyst_router(self, state: FundState):
        """Routing node."""
        return state
        

    def _load_analysts(
            self, 
            ticker: str,
            ) -> List[str]:
        """Load the analysts."""
        
        # pre-defined analysts
        analysts = self.workflow_config['analysts']
        for analyst in analysts:
            if not AgentRegistry.check_agent_key(analyst):
                logger.warning(f"Invalid analyst key: {analyst}, Removed for analysis.")
                analysts.remove(analyst)

        # Otherwise, use planner agent
        if not analysts:
            logger.warning("No analysts provided, using planner agent to select.")
            planner_agent = AgentRegistry.get_agent_func_by_key(AgentKey.PLANNER)
            analysts = planner_agent(ticker)

        return analysts
    

    def run(self):
        """Run the workflow."""

        start_time = perf_counter()

        # will be updated by workflow
        portfolio = self.init_portfolio 

        for ticker in self.tickers:
            connected_analysts = self._load_analysts(ticker)

            # init FundState
            state = FundState(
                ticker = ticker,
                portfolio = portfolio,
                start_date =  self.trading_config['start_date'],
                end_date =  self.trading_config['end_date'],
                llm_config = self.llm_config,
            )

            # build the workflow
            workflow = self.build(state, connected_analysts)

            try:
                logger.info("Invoking agent workflow")
                final_fund_state = workflow.invoke(state)
                logger.info("Agent workflow completed successfully")

            except Exception as e:
                logger.error(f"Error running deep fund: {str(e)}")
                raise

            # log porfolio agent decisions
            for d in final_fund_state["final_decisions"]:
                logger.info(f"Decision for {d.ticker}: {d.action} | {d.confidence:.1f}%\nReason: {d.justification}")


        end_time = perf_counter()
        logger.info(f"Workflow completed in {end_time - start_time:.2f} seconds")

        return final_fund_state

