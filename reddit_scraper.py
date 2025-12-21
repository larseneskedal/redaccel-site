"""
Reddit scraper module for finding high-traffic threads by keywords.

Primary strategy:
- Use Reddit's public JSON search (no API key required)
- If PRAW + official API credentials are available, use them as a secondary option

Now with Ahrefs integration for search traffic data.
"""
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ahrefs_client import AhrefsClient
import re
import requests

try:
    import praw  # Optional: only used if credentials are present
except ImportError:  # pragma: no cover - optional dependency
    praw = None

load_dotenv()


class RedditScraper:
    def __init__(self):
        """Initialize Reddit clients and Ahrefs client."""
        self.ahrefs = AhrefsClient()
        self.two_weeks_ago = datetime.utcnow() - timedelta(days=14)

        # Optional official Reddit API client (only if real credentials exist)
        self.reddit = None
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "RedditCommentTool/1.0 by demo-user")

        if praw and client_id and client_secret and "your_client_id_here" not in client_id:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                )
            except Exception as e:
                print(f"Warning: Failed to initialize PRAW client, will use web search instead: {e}")

        # Session for public JSON search (no auth)
        self.http = requests.Session()
        self.http.headers.update(
            {
                "User-Agent": user_agent
                or "Mozilla/5.0 (RedditCommentTool; +https://reddit.com)"
            }
        )
    
    def _is_keyword_relevant(self, text: str, keyword: str) -> bool:
        """Check if text is relevant to the keyword."""
        if not text:
            return False
        
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Check for exact match or word boundaries
        if keyword_lower in text_lower:
            return True
        
        # Check for similar keywords (split by spaces)
        keyword_words = keyword_lower.split()
        if len(keyword_words) > 1:
            # If multi-word keyword, check if most words appear
            matches = sum(1 for word in keyword_words if word in text_lower)
            if matches >= len(keyword_words) * 0.7:  # 70% of words match
                return True
        
        return False
    
    def _calculate_engagement_score(self, score: int, comments: int) -> int:
        """Calculate engagement score."""
        return score + (comments * 2)
    
    def _search_via_public_json(self, keyword: str, limit: int = 200) -> List[Dict]:
        """
        Use Reddit's public JSON search endpoint (no API key required).
        This is best-effort and may be rate-limited by Reddit.
        """
        posts: List[Dict] = []
        now = datetime.utcnow()

        try:
            resp = self.http.get(
                "https://www.reddit.com/search.json",
                params={
                    "q": keyword,
                    "sort": "hot",
                    "t": "year",
                    "limit": min(limit, 100),
                    "type": "link",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Public Reddit search failed: {e}")
            return posts

        children = (
            data.get("data", {}).get("children", [])
            if isinstance(data, dict)
            else []
        )

        for child in children:
            try:
                post = child.get("data", {})
                title = post.get("title", "")
                selftext = post.get("selftext", "") or ""
                permalink = post.get("permalink", "")
                subreddit = post.get("subreddit", "unknown")
                score = int(post.get("score", 0))
                num_comments = int(post.get("num_comments", 0))

                created_utc_ts = post.get("created_utc")
                if created_utc_ts:
                    post_created = datetime.fromtimestamp(created_utc_ts)
                else:
                    post_created = now

                age_days = (now - post_created).days
                is_recent = age_days <= 14

                # Keyword relevance
                title_relevant = self._is_keyword_relevant(title, keyword)
                content_relevant = self._is_keyword_relevant(selftext[:500], keyword)
                if not (title_relevant or content_relevant):
                    continue

                engagement_score = self._calculate_engagement_score(score, num_comments)

                # Relaxed engagement filters to surface more threads
                if is_recent and engagement_score < 10:
                    continue
                if not is_recent and engagement_score < 5:
                    continue

                post_data = {
                    "title": title,
                    "url": f"https://reddit.com{permalink}",
                    "subreddit": subreddit,
                    "score": score,
                    "comments": num_comments,
                    "engagement_score": engagement_score,
                    "created_utc": post_created,
                    "age_days": age_days,
                    "is_recent": is_recent,
                    "selftext": selftext[:500],
                    "author": post.get("author", "[unknown]"),
                    "search_traffic": 0,
                }

                posts.append(post_data)
            except Exception as e:
                print(f"Error processing public post: {e}")
                continue

        return posts

    def search_subreddits(
        self,
        keyword: str,
        limit: int = 200,
        prioritize_traffic: bool = True,
    ) -> List[Dict]:
        """
        Search for posts across Reddit containing the keyword.
        Tries official API (if configured), otherwise falls back to public JSON.
        """
        # Try public JSON search first (no keys needed)
        posts = self._search_via_public_json(keyword, limit=limit)

        # Enrich with Ahrefs keyword metrics (same keyword for all posts)
        if posts and prioritize_traffic:
            try:
                traffic_data = self.ahrefs.get_reddit_post_traffic(
                    reddit_url="", keyword=keyword
                )
            except Exception as e:
                print(f"Ahrefs enrichment failed: {e}")
                traffic_data = None

            if traffic_data:
                for post in posts:
                    post["search_traffic"] = traffic_data.get("estimated_traffic", 0)
                    post["search_volume"] = traffic_data.get("search_volume", 0)
                    post["keyword_difficulty"] = traffic_data.get(
                        "keyword_difficulty", 0
                    )

        if posts:
            return posts

        # Fallback: if public search fails but we have PRAW + keys, use that
        if self.reddit:
            print("Public search empty, falling back to official Reddit API (PRAW).")
            posts: List[Dict] = []
            now = datetime.utcnow()

            for submission in self.reddit.subreddit("all").search(
                keyword, limit=limit, sort="hot"
            ):
                try:
                    post_created = datetime.fromtimestamp(submission.created_utc)
                    age_days = (now - post_created).days
                    is_recent = age_days <= 14

                    title_relevant = self._is_keyword_relevant(
                        submission.title, keyword
                    )
                    content_relevant = self._is_keyword_relevant(
                        submission.selftext[:500] if submission.selftext else "",
                        keyword,
                    )
                    if not (title_relevant or content_relevant):
                        continue

                    engagement_score = self._calculate_engagement_score(
                        submission.score, submission.num_comments
                    )

                    if is_recent and engagement_score < 20:
                        continue
                    if not is_recent and engagement_score < 10:
                        continue

                    post_data = {
                        "title": submission.title,
                        "url": f"https://reddit.com{submission.permalink}",
                        "subreddit": submission.subreddit.display_name,
                        "score": submission.score,
                        "comments": submission.num_comments,
                        "engagement_score": engagement_score,
                        "created_utc": post_created,
                        "age_days": age_days,
                        "is_recent": is_recent,
                        "selftext": submission.selftext[:500]
                        if submission.selftext
                        else "",
                        "author": str(submission.author)
                        if submission.author
                        else "[deleted]",
                        "search_traffic": 0,
                    }

                    if prioritize_traffic and not is_recent:
                        traffic_data = self.ahrefs.get_reddit_post_traffic(
                            post_data["url"], keyword
                        )
                        if traffic_data:
                            post_data["search_traffic"] = traffic_data.get(
                                "estimated_traffic", 0
                            )
                            post_data["search_volume"] = traffic_data.get(
                                "search_volume", 0
                            )
                            post_data["keyword_difficulty"] = traffic_data.get(
                                "keyword_difficulty", 0
                            )

                    posts.append(post_data)
                except Exception as e:
                    print(f"Error processing post via PRAW: {e}")
                    continue

            return posts

        # If everything fails, return empty list (UI will show \"no posts\" or demo mode will kick in)
        return []
    
    def get_top_posts(
        self, 
        keyword: str, 
        top_n: int = 10,
        prioritize_traffic: bool = True
    ) -> List[Dict]:
        """
        Get top N posts for a keyword, prioritizing by search traffic or engagement.
        
        Args:
            keyword: Search term
            top_n: Number of top posts to return
            prioritize_traffic: If True, prioritize by search traffic; if False, by engagement
            
        Returns:
            List of top post dictionaries, sorted by:
            - For older posts: search traffic (if available) or engagement
            - For recent posts (< 2 weeks): engagement score
        """
        # Fetch a generous pool so we can filter/sort and still have many results
        fetch_limit = max(top_n * 10, 400)
        all_posts = self.search_subreddits(
            keyword, limit=fetch_limit, prioritize_traffic=prioritize_traffic
        )
        
        if not all_posts:
            return []

        # Single combined ranking:
        # - High Ahrefs traffic strongly favored
        # - Recent posts get a small bonus
        # - Engagement always matters
        def combined_score(post):
            traffic = post.get("search_traffic", 0) or 0
            engagement = post.get("engagement_score", 0) or 0
            is_recent = post.get("is_recent", False)
            recent_bonus = 1.2 if is_recent else 1.0
            return traffic * 3.0 + engagement * recent_bonus

        all_posts.sort(key=combined_score, reverse=True)

        # Ensure we return at least top_n if that many exist
        return all_posts[: min(top_n, len(all_posts))]
    
    def get_post_details(self, post_url: str) -> Dict:
        """
        Get detailed information about a specific post.

        For now this is a best-effort helper and will use PRAW only if available.
        The main UI does not rely on this.
        """
        if not self.reddit:
            return {
                "title": "",
                "url": post_url,
                "subreddit": "",
                "score": 0,
                "comments": 0,
                "selftext": "",
                "created_utc": datetime.utcnow(),
                "author": "[unknown]",
            }

        submission = self.reddit.submission(url=post_url)

        return {
            "title": submission.title,
            "url": f"https://reddit.com{submission.permalink}",
            "subreddit": submission.subreddit.display_name,
            "score": submission.score,
            "comments": submission.num_comments,
            "selftext": submission.selftext,
            "created_utc": datetime.fromtimestamp(submission.created_utc),
            "author": str(submission.author) if submission.author else "[deleted]",
        }
