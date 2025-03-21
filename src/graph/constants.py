from enum import Enum

class AgentKey:
    # analyst keys
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"

    # workflow keys
    PORTFOLIO = "portfolio manager"
    PLANNER = "analyst planner" 

class Signal(str, Enum):
    """Signal type"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

    def __str__(self) -> str:
        return self.value

class Action(str, Enum):
    """Action type"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

    def __str__(self) -> str:
        return self.value 