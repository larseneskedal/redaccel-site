"""
Website Analyzer - Extracts product information from websites.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Optional
import requests
from urllib.parse import urlparse
import re

load_dotenv()


class WebsiteAnalyzer:
    """Analyzes websites to extract product information."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
    
    def fetch_website_content(self, url: str) -> str:
        """
        Fetch and extract text content from a website.
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Extracted text content from the website
        """
        try:
            # Add headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract text from HTML (simple approach)
            # Remove script and style tags
            content = response.text
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Extract text from HTML tags
            text = re.sub(r'<[^>]+>', ' ', content)
            text = re.sub(r'\s+', ' ', text)
            
            # Limit content length
            return text[:10000]  # First 10k characters
            
        except Exception as e:
            raise Exception(f"Error fetching website: {str(e)}")
    
    def analyze_website(self, url: str) -> Dict:
        """
        Analyze a website and extract product information using AI.
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Dictionary containing extracted product information
        """
        try:
            # Fetch website content
            website_content = self.fetch_website_content(url)
            
            # Use AI to extract product information
            prompt = f"""Analyze this website content and extract key product information.

Website URL: {url}
Website Content (first 10k chars):
{website_content[:10000]}

Extract and provide the following information in JSON format:
{{
    "product_name": "Name of the product/service",
    "product_description": "Clear description of what the product does and its value proposition",
    "product_features": ["feature1", "feature2", "feature3"],
    "pricing": "Pricing information if available (e.g., $29/month, Free, Contact for pricing)",
    "target_audience": "Who this product is for",
    "key_benefits": ["benefit1", "benefit2"],
    "product_type": "Type of product (SaaS, Mobile App, Website, etc.)"
}}

Be thorough and extract as much information as possible. If information is not available, use "Not specified" or empty arrays/lists."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing websites and extracting product information. You provide accurate, structured information in JSON format."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            product_info = response.choices[0].message.content
            import json
            product_data = json.loads(product_info)
            
            # Add the URL
            product_data["source_url"] = url
            
            return product_data
            
        except Exception as e:
            raise Exception(f"Error analyzing website: {str(e)}")
