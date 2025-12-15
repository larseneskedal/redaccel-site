"""
Ahrefs API client for getting search traffic data.
"""
import requests
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime, timedelta

load_dotenv()


class AhrefsClient:
    def __init__(self):
        """Initialize Ahrefs API client."""
        self.api_token = os.getenv("AHREFS_API_TOKEN")
        self.base_url = "https://apiv2.ahrefs.com"
        
        if not self.api_token:
            print("Warning: AHREFS_API_TOKEN not found. Search traffic features will be limited.")
    
    def get_url_metrics(self, url: str) -> Optional[Dict]:
        """
        Get URL metrics from Ahrefs.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with URL metrics or None
        """
        if not self.api_token:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/url-metrics",
                params={
                    'target': url,
                    'token': self.api_token,
                    'output': 'json',
                    'from': 'backlinks',
                    'mode': 'domain'
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ahrefs API error: {e}")
            return None
    
    def get_keyword_metrics(self, keyword: str) -> Optional[Dict]:
        """
        Get keyword metrics from Ahrefs.
        
        Args:
            keyword: Keyword to check
            
        Returns:
            Dictionary with keyword metrics or None
        """
        if not self.api_token:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/keywords-explorer",
                params={
                    'keyword': keyword,
                    'token': self.api_token,
                    'output': 'json',
                    'mode': 'exact'
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ahrefs API error: {e}")
            return None
    
    def get_reddit_post_traffic(self, reddit_url: str, keyword: str) -> Optional[Dict]:
        """
        Estimate search traffic for a Reddit post URL based on keyword.
        
        Args:
            reddit_url: Reddit post URL
            keyword: Related keyword
            
        Returns:
            Dictionary with traffic estimates or None
        """
        # Since Ahrefs doesn't directly track Reddit posts,
        # we'll use keyword metrics to estimate potential traffic
        keyword_data = self.get_keyword_metrics(keyword)

        # The exact shape of Ahrefs' response can vary by plan/version.
        # We try a few common patterns and fall back gracefully.
        if not keyword_data:
            return None

        metrics = {}
        # Pattern 1: top-level "metrics"
        if isinstance(keyword_data, dict) and "metrics" in keyword_data:
            metrics = keyword_data["metrics"]
        # Pattern 2: nested under "keywords" list
        elif isinstance(keyword_data, dict) and "keywords" in keyword_data:
            kws = keyword_data.get("keywords") or []
            if isinstance(kws, list) and kws:
                metrics = kws[0]

        if metrics:
            return {
                "search_volume": metrics.get("search_volume", 0),
                "keyword_difficulty": metrics.get("keyword_difficulty", 0),
                "cpc": metrics.get("cpc", 0),
                "estimated_traffic": self._estimate_traffic(metrics),
            }
        
        return None
    
    def _estimate_traffic(self, metrics: Dict) -> int:
        """Estimate traffic based on keyword metrics."""
        search_volume = metrics.get('search_volume', 0)
        # Rough estimate: 10-20% of search volume might click through to top results
        # Reddit posts ranking in top 10 might get 1-5% of that
        if search_volume > 0:
            return int(search_volume * 0.15 * 0.03)  # Very rough estimate
        return 0

