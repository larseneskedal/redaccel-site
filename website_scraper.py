"""
Website scraper module for extracting information about what's being promoted.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Optional
import re


class WebsiteScraper:
    def __init__(self):
        """Initialize website scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_website(self, url: str) -> Dict[str, str]:
        """
        Scrape a website to understand what it's about.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary with website information
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract information
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            keywords = self._extract_keywords(soup)
            main_content = self._extract_main_content(soup)
            
            # Get domain name
            domain = urlparse(url).netloc.replace('www.', '')
            
            return {
                'url': url,
                'domain': domain,
                'title': title,
                'description': description,
                'keywords': keywords,
                'main_content': main_content[:1000],  # First 1000 chars
                'summary': self._generate_summary(title, description, main_content)
            }
        except Exception as e:
            # Return basic info if scraping fails
            domain = urlparse(url if url.startswith(('http://', 'https://')) else 'https://' + url).netloc.replace('www.', '')
            return {
                'url': url,
                'domain': domain,
                'title': domain,
                'description': f'Website at {domain}',
                'keywords': '',
                'main_content': '',
                'summary': f'Website: {domain}',
                'error': str(e)
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try multiple methods
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '').strip()
            if desc:
                return desc
        
        # Try Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            desc = og_desc.get('content', '').strip()
            if desc:
                return desc
        
        # Try first paragraph
        p = soup.find('p')
        if p:
            text = p.get_text().strip()
            if len(text) > 50:
                return text[:200]
        
        return ''
    
    def _extract_keywords(self, soup: BeautifulSoup) -> str:
        """Extract meta keywords."""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            return meta_keywords.get('content', '').strip()
        return ''
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content area
        main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article', re.I))
        
        if main:
            text = main.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        return text
    
    def _generate_summary(self, title: str, description: str, content: str) -> str:
        """Generate a summary of the website."""
        parts = []
        
        if title:
            parts.append(f"Title: {title}")
        if description:
            parts.append(f"Description: {description}")
        if content:
            # Get first sentence or first 200 chars
            first_sentence = content.split('.')[0] if '.' in content else content[:200]
            parts.append(f"Content: {first_sentence}")
        
        return ' | '.join(parts) if parts else 'Website information'

