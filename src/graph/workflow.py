from typing import List, Dict, Any
from langgraph.graph import StateGraph, START, END
from graph.schema import FundState, Action
from graph.constants import AgentKey
from agents.registry import AgentRegistry
from agents.planner import planner_agent
from util.logger import logger
from time import perf_counter


class AgentWorkflow:
    """Trading Decision Workflow."""

    def __init__(self, config: Dict[str, Any], portfolio: dict, tickers: list):
        self.trading_config = config['trading']
        self.llm_config = config['llm']
        self.tickers = tickers
        self.init_portfolio = portfolio
        
        if config.get('workflow_analysts'):
            self.workflow_analysts = config['workflow_analysts']
        else:
            self.workflow_analysts = None
            self.planner_mode = True

    def build(self) -> StateGraph:
        """Build the workflow"""
        # logger.info("Building workflow")

        # Create the workflow
        graph = StateGraph(FundState)
        
        # create node for portfolio manager
        portfolio_agent = AgentRegistry.get_agent_func_by_key(AgentKey.PORTFOLIO)
        graph.add_node(AgentKey.PORTFOLIO, portfolio_agent)

        # create functional nodes
        graph.add_node("analyst_router", self.analyst_router)
        graph.add_edge(START, "analyst_router")
        
        # create node for each analyst and add edge
        for analyst in self.workflow_analysts:
            agent_func = AgentRegistry.get_agent_func_by_key(analyst)
            graph.add_node(analyst, agent_func)
            graph.add_edge("analyst_router", analyst) # route to analyst
            graph.add_edge(analyst, AgentKey.PORTFOLIO)
        
        # Route portfolio manager to end
        graph.add_edge(AgentKey.PORTFOLIO, END)

        # compile the workflow
        workflow = graph.compile()        
        return workflow 
        
    def analyst_router(self, state: FundState):
        """Routing node."""
        return state

    def load_analysts(self, ticker: str):
        """
        Load the analysts. It can:
        - verify and remove invalid analysts.
        - call planner agent to select analysts.
        """
        
        # pre-defined analysts
        if self.workflow_analysts:
            for analyst in self.workflow_analysts:
                if not AgentRegistry.check_agent_key(analyst):
                    logger.warning(f"Invalid analyst key: {analyst}, Removed for analysis.")
                    self.workflow_analysts.remove(analyst)

        # Otherwise, use planner agent
        else:
            logger.warning("No analysts provided, using planner agent to select.")
            analysts = planner_agent(ticker, self.llm_config)
            self.workflow_analysts = analysts
            logger.info(f"Planner agent selected {len(analysts)} analysts: {analysts}")
    
    def run(self):
        """Run the workflow."""
        start_time = perf_counter()

        # will be updated by the output of workflow
        portfolio = self.init_portfolio 
        for ticker in self.tickers:
            self.load_analysts(ticker)
            state = FundState(
                ticker = ticker,
                portfolio = portfolio,
                start_date = self.trading_config['start_date'],
                end_date = self.trading_config['end_date'],
                llm_config = self.llm_config
            ) # init FundState

            # build the workflow
            workflow = self.build()
            logger.info(f"{ticker} workflow compiled successfully")
            try:
                final_state = workflow.invoke(state)
            except Exception as e:
                logger.error(f"Error running deep fund: {str(e)}")
                raise

            # update portfolio
            action = final_state["decision"].action
            shares = final_state["decision"].shares
            trading_price = final_state["trading_price"]
            portfolio = self.update_portfolio(portfolio, ticker, action, shares, trading_price)

            # clean analysts
            if self.planner_mode:
                self.workflow_analysts = None

        end_time = perf_counter()
        logger.info(f"Workflow completed in {end_time - start_time:.2f} seconds")

        return portfolio


    def update_portfolio(self, portfolio, ticker: str, action: Action, shares: int, trading_price: float):
        """Update the portfolio."""
        if action == Action.BUY:
            portfolio.positions[ticker].shares += shares
            portfolio.positions[ticker].value = trading_price * shares
            portfolio.cashflow -= trading_price * shares
        elif action == Action.SELL:
            portfolio.positions[ticker].shares -= shares
            portfolio.positions[ticker].value = trading_price * shares
            portfolio.cashflow += trading_price * shares
        return portfolio
