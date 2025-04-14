from pydantic import BaseModel
from typing import Optional, List

class SocialMediaPost(BaseModel):
    """Social media post model for retail investor sentiment analysis."""
    platform: str  
    author: str = None
    content: str = None
    publish_time: str = None
    comments: Optional[int] = None 
    likes: Optional[int] = None   
    repost: Optional[int] = None 
