import os
import requests
import tweepy
from .api_model import SocialMediaPost

class TwitterAPI:
    """Twitter API wrapper for fetching tweets and analysis."""

    def __init__(self):
        """Initialize Twitter API client (Tweepy) with configuration."""
        self.api_key = os.environ.get("TWITTER_API_KEY")
        if not self.api_key:
            raise ValueError("Twitter API key not configured.")
    
    def get_twitter_posts(self, ticker: str, limit: int) -> list[SocialMediaPost]:
        """Get tweets related to a ticker."""

        client  = tweepy.Client(bearer_token=self.api_key)
        # Search query with language filter
        query = f"#{ticker} OR {ticker} stock OR {ticker} shares lang:en"  
        params = {
            "query": query,
            "max_results": limit, # 10 <= x <= 100
            "tweet_fields": ["created_at", "public_metrics", "author_id"], # A comma separated list of Tweet fields
        }
        
        # Get tweets
        response = client.search_recent_tweets(**params)

        posts = []
        for tweet in response.data:            
            posts.append(SocialMediaPost(
                content=tweet.text,
                publish_time=tweet.created_at,
                views=tweet.public_metrics["impression_count"],
                likes=tweet.public_metrics["like_count"],
                repost=tweet.public_metrics["retweet_count"],
            ))
        
        return posts
            