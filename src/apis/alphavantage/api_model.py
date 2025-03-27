from pydantic import BaseModel

class InsiderTrade(BaseModel):
    """insider trade model."""
    transaction_date: str
    ticker: str
    executive: str
    executive_title: str
    security_type: str
    acquisition_or_disposal: str
    shares: float
    share_price: float