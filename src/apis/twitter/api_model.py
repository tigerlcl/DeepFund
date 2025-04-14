from pydantic import BaseModel
from typing import Optional, List

class SocialMediaPost(BaseModel):
    """Social media post model for retail investor sentiment analysis."""
    platform: str  # 'twitter' or others
    post_id: str = None
    author: str = None
    content: str = None
    publish_time: str = None
    comments: Optional[int] = None 
    likes: Optional[int] = None   
    repost: Optional[int] = None 

class SocialMediaSentiment(BaseModel):
    """Model for storing Reddit and Twitter retail investor sentiment data."""
    ticker: str
    total_posts: int
    posts: List[SocialMediaPost]
    reddit_sentiment: Optional[float] = None
    twitter_sentiment: Optional[float] = None

