import uuid
from typing import  Dict, Any
from langgraph.graph import StateGraph, START, END
from graph.schema import FundState, Portfolio,Decision, Action, Position
from graph.constants import AgentKey
from agents.registry import AgentRegistry
from agents.planner import planner_agent
from util.db_helper import get_db
from util.logger import logger
from time import perf_counter


class AgentWorkflow:
    """Trading Decision Workflow."""

    def __init__(self, config: Dict[str, Any], config_id: str):
        self.llm_config = config['llm']
        self.tickers = config['tickers']
        self.exp_name = config['exp_name']
        self.db = get_db()

        # load latest portfolio
        portfolio = self.db.get_latest_portfolio(config_id)
        if not portfolio:
            portfolio = self.db.create_portfolio(config_id, config['cashflow'])
            if not portfolio:
                raise RuntimeError(f"Failed to create portfolio for config {self.exp_name}")
        
        # copy portfolio with a new id
        new_portfolio = self.db.copy_portfolio(config_id, portfolio)
        self.init_portfolio = Portfolio(**new_portfolio)
        logger.info(f"New portfolio ID: {self.init_portfolio.id}")
        
        # Workflow analysts
        if config.get('workflow_analysts'):
            self.workflow_analysts = config['workflow_analysts']
            self.planner_mode = False
        else:
            self.workflow_analysts = None
            self.planner_mode = True


    def build(self) -> StateGraph:
        """Build the workflow"""
        graph = StateGraph(FundState)
        
        # create node for portfolio manager
        portfolio_agent = AgentRegistry.get_agent_func_by_key(AgentKey.PORTFOLIO)
        graph.add_node(AgentKey.PORTFOLIO, portfolio_agent)
        
        # create node for each analyst and add edge
        for analyst in self.workflow_analysts:
            agent_func = AgentRegistry.get_agent_func_by_key(analyst)
            graph.add_node(analyst, agent_func)
            graph.add_edge(START, analyst)
            graph.add_edge(analyst, AgentKey.PORTFOLIO)
        
        # Route portfolio manager to end
        graph.add_edge(AgentKey.PORTFOLIO, END)
        workflow = graph.compile()

        return workflow 
        

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
    
    def run(self) -> Dict[str, Any]:
        """Run the workflow."""
        start_time = perf_counter()

        # will be updated by the output of workflow
        portfolio = self.init_portfolio 
        for ticker in self.tickers:
            self.load_analysts(ticker)
            
            # init FundState
            state = FundState(
                ticker = ticker,
                exp_name = self.exp_name,
                portfolio = portfolio,
                llm_config = self.llm_config,
            ) 

            # build the workflow
            workflow = self.build()
            logger.info(f"{ticker} workflow compiled successfully")
            try:
                final_state = workflow.invoke(state)
            except Exception as e:
                logger.error(f"Error running deep fund: {str(e)}")
                raise

            # update portfolio
            portfolio = self.update_portfolio_ticker(portfolio, ticker, final_state["decision"])
            logger.log_portfolio(f"{ticker} position update", portfolio)

            # clean analysts
            if self.planner_mode:
                self.workflow_analysts = None

        end_time = perf_counter()
        logger.info(f"Workflow completed in {end_time - start_time:.2f} seconds")

        # Convert Pydantic model to dict
        return portfolio.model_dump()


    def update_portfolio_ticker(self, portfolio: Portfolio, ticker: str, decision: Decision) -> Portfolio:
        """Update the ticker asset in the portfolio."""

        action = decision.action
        shares = decision.shares
        price = decision.price

        if ticker not in portfolio.positions:
            portfolio.positions[ticker] = Position(shares=0, value=0)

        if action == Action.BUY:
            portfolio.positions[ticker].shares += shares
            portfolio.cashflow -= price * shares
        elif action == Action.SELL:
            portfolio.positions[ticker].shares -= shares
            portfolio.cashflow += price * shares

        # Always recalculate position value with latest price
        portfolio.positions[ticker].value = round(price * portfolio.positions[ticker].shares, 2)

        # round cashflow
        portfolio.cashflow = round(portfolio.cashflow, 2)

        return portfolio
