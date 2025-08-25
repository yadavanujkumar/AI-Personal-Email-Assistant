"""
Email parsing utilities.
"""
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from email.utils import parsedate_to_datetime
import dateutil.parser
from bs4 import BeautifulSoup

from .logger import get_logger

logger = get_logger(__name__)


def clean_email_body(body: str, html_body: str = None) -> str:
    """
    Clean and normalize email body content.
    
    Args:
        body: Plain text email body
        html_body: HTML email body (optional)
        
    Returns:
        Cleaned email body text
    """
    if html_body:
        # Convert HTML to text
        soup = BeautifulSoup(html_body, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
    else:
        text = body or ""
    
    # Clean up whitespace and line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
    text = text.strip()
    
    # Remove email signatures and quoted text
    text = remove_signature(text)
    text = remove_quoted_text(text)
    
    return text


def remove_signature(text: str) -> str:
    """Remove email signature from text."""
    # Common signature patterns
    signature_patterns = [
        r'\n--\s*\n.*',  # Standard signature delimiter
        r'\nBest regards,.*',
        r'\nSincerely,.*',
        r'\nThanks,.*',
        r'\nCheers,.*',
        r'\nSent from my.*',
        r'\n________________________________.*',  # Outlook separator
    ]
    
    for pattern in signature_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    return text.strip()


def remove_quoted_text(text: str) -> str:
    """Remove quoted text from replies."""
    # Remove text after "On ... wrote:" pattern
    quote_pattern = r'\n\s*On .+ wrote:\s*\n.*'
    text = re.sub(quote_pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove lines starting with > (common quote marker)
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        if not line.strip().startswith('>'):
            clean_lines.append(line)
    
    return '\n'.join(clean_lines).strip()


def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Remove duplicates


def parse_email_date(date_str: str) -> Optional[datetime]:
    """
    Parse email date string to datetime object.
    
    Args:
        date_str: Date string from email header
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        # Try email.utils.parsedate_to_datetime first
        return parsedate_to_datetime(date_str)
    except (ValueError, TypeError):
        try:
            # Fallback to dateutil.parser
            return dateutil.parser.parse(date_str)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse date: {date_str}")
            return None


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls


def detect_meeting_keywords(text: str) -> List[str]:
    """
    Detect meeting-related keywords in text.
    
    Args:
        text: Email body text
        
    Returns:
        List of detected meeting keywords
    """
    meeting_keywords = [
        'meeting', 'call', 'conference', 'appointment', 'schedule',
        'discuss', 'catch up', 'sync', 'standup', 'review',
        'demo', 'presentation', 'interview', 'zoom', 'teams',
        'calendar', 'available', 'free time', 'availability'
    ]
    
    detected = []
    text_lower = text.lower()
    
    for keyword in meeting_keywords:
        if keyword in text_lower:
            detected.append(keyword)
    
    return detected


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
        r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',  # (123) 456-7890
        r'\b\+\d{1,3}[-.\s]?\d{1,14}\b',  # International
    ]
    
    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, text))
    
    return phones


def get_email_thread_id(message_id: str, in_reply_to: str = None, 
                       references: str = None) -> str:
    """
    Generate a consistent thread ID for email threading.
    
    Args:
        message_id: Current message ID
        in_reply_to: In-Reply-To header value
        references: References header value
        
    Returns:
        Thread ID string
    """
    if in_reply_to:
        return in_reply_to.strip('<>')
    
    if references:
        # Use the first message ID in references
        refs = references.split()
        if refs:
            return refs[0].strip('<>')
    
    # If no threading headers, use the message ID itself
    return message_id.strip('<>')


def parse_contact_info(text: str) -> Dict[str, List[str]]:
    """
    Extract contact information from email text.
    
    Args:
        text: Email body text
        
    Returns:
        Dictionary with contact information
    """
    return {
        'emails': extract_email_addresses(text),
        'phones': extract_phone_numbers(text),
        'urls': extract_urls(text)
    }