"""
Web search tool integration using Google Custom Search API.
"""
import requests
from typing import List, Dict, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class WebSearchTool:
    """Tool for performing web searches to gather information."""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        logger.info("Web search tool initialized")
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Perform a web search and return results.
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 10)
            
        Returns:
            List of search result dictionaries
        """
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', '')
                }
                results.append(result)
            
            logger.info(f"Web search completed: {len(results)} results for '{query}'")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Web search API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in web search: {e}")
            return []
    
    def search_for_email_context(self, email_subject: str, email_body: str) -> Optional[str]:
        """
        Search for information relevant to an email's content.
        
        Args:
            email_subject: Email subject line
            email_body: Email body content
            
        Returns:
            Formatted search results or None
        """
        # Extract key terms for search
        search_terms = self._extract_search_terms(email_subject, email_body)
        
        if not search_terms:
            return None
        
        query = " ".join(search_terms[:5])  # Use top 5 search terms
        results = self.search(query, num_results=3)
        
        if not results:
            return None
        
        # Format results for LLM consumption
        formatted_results = "Web search results:\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result['title']}\n"
            formatted_results += f"   {result['snippet']}\n"
            formatted_results += f"   Source: {result['display_link']}\n\n"
        
        return formatted_results
    
    def _extract_search_terms(self, subject: str, body: str) -> List[str]:
        """
        Extract relevant search terms from email content.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            List of search terms
        """
        import re
        
        # Combine subject and body
        text = f"{subject} {body}".lower()
        
        # Remove common email words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'email', 'message', 'sent', 'received', 'thanks', 'regards',
            'please', 'hi', 'hello', 'dear', 'sincerely', 'best'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z0-9]+\b', text)
        
        # Filter out stop words and short words
        search_terms = [
            word for word in words 
            if len(word) > 2 and word.lower() not in stop_words
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in search_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms[:10]  # Return top 10 terms