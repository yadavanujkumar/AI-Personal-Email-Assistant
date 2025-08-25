"""
OpenAI service for email analysis and reply generation.
"""
import openai
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI GPT models."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI service with model: {model}")
    
    def analyze_email(self, email_data: Dict) -> Dict:
        """
        Analyze email content to extract intent, priority, and summary.
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            Dictionary with analysis results
        """
        prompt = self._create_analysis_prompt(email_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that analyzes emails to extract intent, priority, and create summaries. Always respond in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            analysis = self._parse_analysis_response(content)
            
            logger.info(f"Email analysis completed for subject: {email_data.get('subject', '')[:50]}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing email: {e}")
            return {
                'intent': 'unknown',
                'priority': 'medium',
                'requires_action': False,
                'summary': 'Error analyzing email content',
                'confidence': 'low'
            }
    
    def generate_reply(self, email_data: Dict, context: Dict = None) -> str:
        """
        Generate a reply to an email.
        
        Args:
            email_data: Dictionary containing original email information
            context: Additional context for reply generation
            
        Returns:
            Generated reply content
        """
        prompt = self._create_reply_prompt(email_data, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email assistant. Generate polite, helpful, and concise email replies."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            reply_content = response.choices[0].message.content.strip()
            logger.info(f"Reply generated for email: {email_data.get('subject', '')[:50]}")
            return reply_content
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return "Thank you for your email. I'll get back to you soon."
    
    def extract_meeting_details(self, email_text: str) -> Dict:
        """
        Extract meeting details from email content.
        
        Args:
            email_text: Email body text
            
        Returns:
            Dictionary with extracted meeting details
        """
        prompt = f"""
        Analyze the following email and extract any meeting-related information.
        Look for dates, times, locations, attendees, and meeting topics.
        
        Email content:
        {email_text}
        
        Please respond in JSON format with the following structure:
        {{
            "has_meeting_request": boolean,
            "meeting_title": "string or null",
            "proposed_dates": ["list of date strings"],
            "proposed_times": ["list of time strings"],
            "location": "string or null",
            "attendees": ["list of email addresses"],
            "meeting_type": "in-person/virtual/unknown",
            "urgency": "high/medium/low"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant specialized in extracting meeting information from emails. Always respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            meeting_details = self._parse_json_response(content)
            
            logger.info("Meeting details extracted successfully")
            return meeting_details
            
        except Exception as e:
            logger.error(f"Error extracting meeting details: {e}")
            return {
                'has_meeting_request': False,
                'meeting_title': None,
                'proposed_dates': [],
                'proposed_times': [],
                'location': None,
                'attendees': [],
                'meeting_type': 'unknown',
                'urgency': 'medium'
            }
    
    def summarize_thread(self, emails: List[Dict]) -> str:
        """
        Summarize a conversation thread.
        
        Args:
            emails: List of email dictionaries in chronological order
            
        Returns:
            Thread summary
        """
        if not emails:
            return "No emails in thread."
        
        # Create thread context
        thread_text = ""
        for i, email in enumerate(emails[-5:]):  # Last 5 emails for context
            thread_text += f"\nEmail {i+1} from {email.get('sender', 'Unknown')}:\n"
            thread_text += f"Subject: {email.get('subject', 'No subject')}\n"
            thread_text += f"Content: {email.get('body', '')[:500]}...\n"
        
        prompt = f"""
        Please provide a concise summary of this email conversation thread.
        Focus on the main topics, decisions made, and any pending actions.
        
        Thread content:
        {thread_text}
        
        Summary:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that creates concise summaries of email conversations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info("Thread summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing thread: {e}")
            return "Unable to generate thread summary."
    
    def _create_analysis_prompt(self, email_data: Dict) -> str:
        """Create prompt for email analysis."""
        sender = email_data.get('sender', 'Unknown')
        subject = email_data.get('subject', 'No subject')
        body = email_data.get('body', '')[:1000]  # Limit body length
        
        return f"""
        Analyze the following email and provide structured analysis:
        
        From: {sender}
        Subject: {subject}
        Body: {body}
        
        Please respond in JSON format with:
        {{
            "intent": "meeting|question|request|information|complaint|other",
            "priority": "high|medium|low",
            "requires_action": true|false,
            "summary": "brief summary of the email content",
            "confidence": "high|medium|low",
            "suggested_actions": ["list of suggested actions"]
        }}
        """
    
    def _create_reply_prompt(self, email_data: Dict, context: Dict = None) -> str:
        """Create prompt for reply generation."""
        sender = email_data.get('sender', 'Unknown')
        subject = email_data.get('subject', 'No subject')
        body = email_data.get('body', '')
        
        context_text = ""
        if context:
            if context.get('search_results'):
                context_text += f"\nWeb search results: {context['search_results']}"
            if context.get('calendar_availability'):
                context_text += f"\nCalendar availability: {context['calendar_availability']}"
        
        return f"""
        Generate a professional email reply to the following message:
        
        Original email from: {sender}
        Subject: {subject}
        Content: {body}
        
        Additional context: {context_text}
        
        Please write a helpful, professional reply that addresses the sender's needs.
        Keep it concise but friendly.
        """
    
    def _parse_analysis_response(self, content: str) -> Dict:
        """Parse JSON response from analysis."""
        try:
            import json
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Failed to parse analysis response as JSON")
            return {
                'intent': 'unknown',
                'priority': 'medium',
                'requires_action': False,
                'summary': content[:200],
                'confidence': 'low',
                'suggested_actions': []
            }
    
    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON response with error handling."""
        try:
            import json
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response")
            return {}