"""
Demo mode - generates sample Reddit posts for testing without Reddit API
"""
from typing import List, Dict
from datetime import datetime, timedelta
import random


def generate_demo_posts(keyword: str, count: int = 5) -> List[Dict]:
    """Generate demo Reddit posts for testing."""
    now = datetime.utcnow()
    
    sample_posts = [
        {
            "title": f"Best practices for {keyword} in 2024",
            "subreddit": "technology",
            "score": 1250,
            "comments": 89,
            "engagement_score": 1428,
            "search_traffic": 450,
            "age_days": 3,
            "is_recent": True,
            "selftext": f"Hey everyone! I've been working with {keyword} for the past year and wanted to share some insights..."
        },
        {
            "title": f"Anyone else struggling with {keyword}?",
            "subreddit": "programming",
            "score": 890,
            "comments": 156,
            "engagement_score": 1202,
            "search_traffic": 320,
            "age_days": 5,
            "is_recent": True,
            "selftext": f"I've been trying to implement {keyword} but running into some issues..."
        },
        {
            "title": f"Complete guide to {keyword} - everything you need to know",
            "subreddit": "learnprogramming",
            "score": 2100,
            "comments": 234,
            "engagement_score": 2568,
            "search_traffic": 890,
            "age_days": 12,
            "is_recent": True,
            "selftext": f"After months of research, I've compiled this comprehensive guide on {keyword}..."
        },
        {
            "title": f"{keyword} changed my workflow completely",
            "subreddit": "productivity",
            "score": 567,
            "comments": 45,
            "engagement_score": 657,
            "search_traffic": 180,
            "age_days": 8,
            "is_recent": True,
            "selftext": f"I started using {keyword} last month and it's been a game changer..."
        },
        {
            "title": f"Top 10 {keyword} tools you should know about",
            "subreddit": "webdev",
            "score": 1450,
            "comments": 112,
            "engagement_score": 1674,
            "search_traffic": 670,
            "age_days": 18,
            "is_recent": False,
            "selftext": f"Here's my curated list of the best {keyword} tools available right now..."
        },
        {
            "title": f"AMA: I've been working with {keyword} for 5 years",
            "subreddit": "IAmA",
            "score": 3200,
            "comments": 456,
            "engagement_score": 4112,
            "search_traffic": 1200,
            "age_days": 25,
            "is_recent": False,
            "selftext": f"Ask me anything about {keyword}! I've seen it evolve over the years..."
        },
        {
            "title": f"Quick tip: {keyword} can save you hours",
            "subreddit": "LifeProTips",
            "score": 980,
            "comments": 67,
            "engagement_score": 1114,
            "search_traffic": 420,
            "age_days": 6,
            "is_recent": True,
            "selftext": f"If you're not using {keyword}, you're missing out on a huge time saver..."
        }
    ]
    
    # Generate URLs
    for i, post in enumerate(sample_posts[:count]):
        post["url"] = f"https://reddit.com/r/{post['subreddit']}/demo_post_{i+1}"
        post["created_utc"] = (now - timedelta(days=post["age_days"])).isoformat()
        post["author"] = "demo_user"
    
    return sample_posts[:count]

