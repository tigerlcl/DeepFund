from pydantic import BaseModel
from typing import Optional

class SocialMediaPost(BaseModel):
    """Social media post model for sentiment analysis."""
    content: str
    publish_time: str
    views: Optional[int] = None
    likes: Optional[int] = None   
    repost: Optional[int] = None 
