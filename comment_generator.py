"""
Comment generator module for creating human-like, subtly promotional comments.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Optional

load_dotenv()


class CommentGenerator:
    def __init__(self):
        """Initialize OpenAI client for comment generation."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.promotion_target = os.getenv("PROMOTION_TARGET", "")
        self.promotion_context = os.getenv("PROMOTION_CONTEXT", "")
    
    def generate_comment(
        self, 
        post_title: str, 
        post_content: str, 
        subreddit: str,
        promotion_target: Optional[str] = None,
        promotion_context: Optional[str] = None,
        website_info: Optional[Dict] = None,
        short: bool = False,
    ) -> str:
        """
        Generate a human-like comment that subtly promotes a business/website.
        
        Args:
            post_title: Title of the Reddit post
            post_content: Content/body of the Reddit post
            subreddit: Name of the subreddit
            promotion_target: What to promote (overrides env var)
            promotion_context: Context about what's being promoted (overrides env var)
            
        Returns:
            Generated comment text
        """
        target = promotion_target or self.promotion_target
        context = promotion_context or self.promotion_context
        
        # Build context from website info if available
        if website_info:
            if not target:
                target = website_info.get('domain', '') or website_info.get('title', '')
            if not context:
                context = website_info.get('summary', '') or website_info.get('description', '')
        
        # Build the prompt
        website_context = ""
        if website_info:
            website_context = f"""
Website Information:
- Domain: {website_info.get('domain', 'N/A')}
- Title: {website_info.get('title', 'N/A')}
- Description: {website_info.get('description', 'N/A')}
- Summary: {website_info.get('summary', 'N/A')}
"""
        
        length_instruction = (
            "Write exactly 1 short, simple sentence that feels like a natural reply, not marketing. "
            "Keep it casual and under 25 words."
            if short
            else "Write a natural, conversational comment of 2-4 sentences."
        )

        prompt = f"""You are a helpful Reddit user writing a comment on r/{subreddit}. 

Post Title: {post_title}
Post Content: {post_content[:1000]}
{website_context}
{length_instruction}

The comment must:
1. Provide at least a bit of value or context related to the post
2. Sound like a real person wrote it (casual, authentic tone)
3. Subtly mention or reference "{target}" in a helpful, non-salesy way
4. Feel organic and not like an advertisement

Context about what you're promoting: {context if context else "General promotion"}

Important: The comment should NOT sound like marketing. It should feel like a genuine recommendation or helpful tip from a fellow Reddit user. Do NOT use phrases like "check out", "visit our website", or "I recommend". Instead, naturally weave it into the conversation.

Write only the comment text, nothing else:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes natural, authentic Reddit comments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher temperature for more natural variation
                max_tokens=200
            )
            
            comment = response.choices[0].message.content.strip()
            return comment
            
        except Exception as e:
            raise Exception(f"Error generating comment: {str(e)}")
    
    def generate_multiple_comments(
        self, 
        posts: list, 
        count: int = 1,
        promotion_target: Optional[str] = None,
        promotion_context: Optional[str] = None,
        website_info: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate comments for multiple posts.
        
        Args:
            posts: List of post dictionaries
            count: Number of comment variations to generate per post
            promotion_target: What to promote
            promotion_context: Context about promotion
            
        Returns:
            Dictionary mapping post URLs to lists of generated comments
        """
        results = {}
        
        for post in posts:
            comments = []
            for i in range(count):
                try:
                    # Make ~50% of comments shorter/simpler
                    short = (i % 2 == 1)
                    comment = self.generate_comment(
                        post["title"],
                        post.get("selftext", ""),
                        post["subreddit"],
                        promotion_target,
                        promotion_context,
                        website_info,
                        short=short,
                    )
                    comments.append(comment)
                except Exception as e:
                    print(f"Error generating comment for {post['url']}: {e}")
                    continue
            
            if comments:
                results[post["url"]] = comments
        
        return results

