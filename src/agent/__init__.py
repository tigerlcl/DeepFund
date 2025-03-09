"""
Agent package initialization.
This module initializes the AgentRegistry and exports the necessary components. This happens when the package is imported
"""

# Import all agent implementations
from agent.registry import AgentRegistry
from agent.technical import technical_agent
from agent.fundamental import fundamental_agent
from agent.sentiment import sentiment_agent
from agent.valuation import valuation_agent
from agent.portfolio import portfolio_agent


# Register all standard analysts
AgentRegistry.register_analyst(
    key="technical",
    node_name="technical_agent",
    display_name="Technical Analyst",
    agent_func=technical_agent
)

AgentRegistry.register_analyst(
    key="fundamental",
    node_name="fundamental_agent",
    display_name="Fundamental Analyst",
    agent_func= fundamental_agent
)

AgentRegistry.register_analyst(
    key="sentiment",
    node_name="sentiment_agent",
    display_name="Sentiment Analyst",
    agent_func=sentiment_agent
)

AgentRegistry.register_analyst(
    key="valuation",
    node_name="valuation_agent",
    display_name="Valuation Analyst",
    agent_func=valuation_agent
)

AgentRegistry.register_agent(
    key="portfolio",
    node_name="portfolio_agent",
    display_name="Portfolio Management Agent",
    agent_func=portfolio_agent
)

