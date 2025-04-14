import os
import tweepy
import yaml
from .api_model import SocialMediaPost

class TwitterAPI:
    """Twitter API wrapper for fetching tweets and analysis."""

    def __init__(self):
        """Initialize Twitter API client with configuration."""
        self.api_key = os.environ.get("TWITTER_API_KEY")
        
        # Load config
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'dev.yaml')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get_twitter_posts(self, ticker: str, limit: int = 100, start_time: str = None, end_time: str = None) -> list[SocialMediaPost]:
        """
        Get tweets related to a ticker.
        
        Args:
            ticker: The stock ticker symbol
            limit: Maximum number of tweets to retrieve
            start_time: Start time for tweet search (ISO 8601 format)
            end_time: End time for tweet search (ISO 8601 format)
            
        Returns:
            List of SocialMediaPost
        """
        if not self.api_key:
            print("Twitter API key not configured.")
            return []
        
        try:
            client = tweepy.Client(
                bearer_token=self.api_key,
                consumer_key=self.api_key,
                wait_on_rate_limit=True
            )
            
            # Search query with language filter
            query = f"#{ticker} OR {ticker} stock OR {ticker} shares lang:en"   # lang:en only English post
            
            params = {
                "query": query,
                "max_results": max(10, min(limit, 100)),    #Each request can fetch a maximum of 100 tweets. Implement pagination to get more tweets.
                "tweet_fields": ["created_at", "public_metrics", "author_id", "text", "lang"],
                "expansions": ["author_id"],
                "user_fields": ["username"],
            }
            
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
            
            # Get tweets
            response = client.search_recent_tweets(**params)
            
            if not response.data:
                return []
            
            posts = []
            for tweet in response.data:            
                posts.append(SocialMediaPost(
                    platform="twitter",
                    content=tweet.text, # only English content
                ))
            
            return posts
            
        except Exception as e:
            print(f"Error fetching Twitter posts: {str(e)}")
            return []