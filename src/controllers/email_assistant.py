"""
Main email assistant controller that orchestrates all components.
"""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..models.database import (
    Email, EmailReply, EmailAction, ConversationThread,
    get_session_maker
)
from ..services.gmail_service import GmailService
from ..services.openai_service import OpenAIService
from ..tools.web_search import WebSearchTool
from ..tools.slack_tool import SlackTool
from ..tools.calendar_tool import CalendarTool
from ..utils.logger import get_logger
from ..utils.email_parser import (
    clean_email_body, parse_email_date, detect_meeting_keywords
)

logger = get_logger(__name__)


class EmailAssistant:
    """Main email assistant controller."""
    
    def __init__(self):
        """Initialize the email assistant with all services and tools."""
        logger.info("Initializing Email Assistant...")
        
        # Initialize database
        self.session_maker = get_session_maker(settings.database_url)
        
        # Initialize services
        self.gmail_service = GmailService(
            settings.gmail_credentials_file,
            settings.gmail_token_file
        )
        self.openai_service = OpenAIService(settings.openai_api_key)
        
        # Initialize tools
        self.web_search = WebSearchTool(
            settings.google_search_api_key,
            settings.google_search_engine_id
        )
        self.slack_tool = SlackTool(
            settings.slack_bot_token,
            settings.slack_channel
        )
        self.calendar_tool = CalendarTool(
            settings.calendar_credentials_file,
            settings.calendar_token_file
        )
        
        logger.info("Email Assistant initialized successfully")
    
    def process_emails(self, max_emails: int = None) -> Dict:
        """
        Main method to process emails from inbox.
        
        Args:
            max_emails: Maximum number of emails to process
            
        Returns:
            Processing summary dictionary
        """
        max_emails = max_emails or settings.max_emails_fetch
        logger.info(f"Starting email processing (max: {max_emails})")
        
        # Fetch emails from Gmail
        emails = self.gmail_service.get_messages(
            query='is:unread',
            max_results=max_emails
        )
        
        if not emails:
            logger.info("No unread emails found")
            return {'processed': 0, 'actions': 0, 'errors': 0}
        
        processed_count = 0
        actions_count = 0
        errors_count = 0
        
        with self.session_maker() as session:
            for email_data in emails:
                try:
                    # Process individual email
                    result = self._process_single_email(email_data, session)
                    
                    if result['success']:
                        processed_count += 1
                        actions_count += len(result.get('actions', []))
                    else:
                        errors_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing email {email_data.get('id', 'unknown')}: {e}")
                    errors_count += 1
        
        summary = {
            'processed': processed_count,
            'actions': actions_count,
            'errors': errors_count,
            'total_emails': len(emails)
        }
        
        logger.info(f"Email processing completed: {summary}")
        return summary
    
    def _process_single_email(self, email_data: Dict, session: Session) -> Dict:
        """
        Process a single email through the full pipeline.
        
        Args:
            email_data: Email data dictionary
            session: Database session
            
        Returns:
            Processing result dictionary
        """
        email_id = email_data.get('id', 'unknown')
        logger.info(f"Processing email: {email_id}")
        
        try:
            # Check if email already exists in database
            existing_email = session.query(Email).filter(
                Email.message_id == email_data.get('message_id', '')
            ).first()
            
            if existing_email:
                logger.info(f"Email already processed: {email_id}")
                return {'success': True, 'actions': []}
            
            # Clean and parse email content
            clean_body = clean_email_body(
                email_data.get('body', ''),
                email_data.get('html_body', '')
            )
            
            # Store email in database
            email_record = self._store_email(email_data, clean_body, session)
            
            # Analyze email with AI
            analysis = self.openai_service.analyze_email({
                **email_data,
                'body': clean_body
            })
            
            # Update email record with analysis
            email_record.intent = analysis.get('intent', 'unknown')
            email_record.priority = analysis.get('priority', 'medium')
            email_record.requires_action = analysis.get('requires_action', False)
            email_record.ai_summary = analysis.get('summary', '')
            
            # Perform actions based on analysis
            actions = self._perform_actions(email_record, analysis, session)
            
            # Mark email as read if processed successfully
            self.gmail_service.mark_as_read(email_id)
            
            session.commit()
            
            return {
                'success': True,
                'email_id': email_record.id,
                'actions': actions
            }
            
        except Exception as e:
            logger.error(f"Error processing email {email_id}: {e}")
            session.rollback()
            return {'success': False, 'error': str(e)}
    
    def _store_email(self, email_data: Dict, clean_body: str, session: Session) -> Email:
        """Store email in database."""
        email_record = Email(
            message_id=email_data.get('message_id', ''),
            thread_id=email_data.get('thread_id', ''),
            sender=email_data.get('sender', ''),
            recipient=email_data.get('recipient', ''),
            subject=email_data.get('subject', ''),
            body=clean_body,
            html_body=email_data.get('html_body', ''),
            timestamp=datetime.utcnow(),
            received_date=email_data.get('timestamp'),
            has_attachments=email_data.get('has_attachments', False)
        )
        
        session.add(email_record)
        session.flush()  # Get the ID
        
        return email_record
    
    def _perform_actions(self, email: Email, analysis: Dict, session: Session) -> List[Dict]:
        """
        Perform actions based on email analysis.
        
        Args:
            email: Email database record
            analysis: AI analysis results
            session: Database session
            
        Returns:
            List of actions performed
        """
        actions = []
        
        # Check if high priority email needs Slack notification
        if analysis.get('priority') == 'high':
            action = self._send_slack_notification(email, session)
            if action:
                actions.append(action)
        
        # Check for meeting requests
        meeting_keywords = detect_meeting_keywords(email.body)
        if meeting_keywords or analysis.get('intent') == 'meeting':
            action = self._handle_meeting_request(email, session)
            if action:
                actions.append(action)
        
        # Perform web search if needed for questions
        if analysis.get('intent') == 'question':
            action = self._perform_web_search(email, session)
            if action:
                actions.append(action)
        
        # Generate reply if auto-reply is enabled and email requires action
        if (settings.auto_reply_enabled and 
            analysis.get('requires_action') and
            analysis.get('intent') in ['question', 'request']):
            action = self._generate_auto_reply(email, analysis, session)
            if action:
                actions.append(action)
        
        return actions
    
    def _send_slack_notification(self, email: Email, session: Session) -> Optional[Dict]:
        """Send Slack notification for important email."""
        try:
            email_data = {
                'sender': email.sender,
                'subject': email.subject,
                'snippet': email.body[:200]
            }
            
            success = self.slack_tool.send_email_notification(email_data)
            
            action = EmailAction(
                email_id=email.id,
                action_type='slack_notify',
                action_data={'notification_type': 'high_priority'},
                status='completed' if success else 'failed'
            )
            
            if not success:
                action.error_message = 'Failed to send Slack notification'
            
            session.add(action)
            
            return {
                'type': 'slack_notify',
                'status': 'completed' if success else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return None
    
    def _handle_meeting_request(self, email: Email, session: Session) -> Optional[Dict]:
        """Handle meeting request from email."""
        try:
            # Extract meeting details using AI
            meeting_details = self.openai_service.extract_meeting_details(email.body)
            
            if meeting_details.get('has_meeting_request'):
                # Send Slack notification about meeting
                self.slack_tool.send_meeting_notification(meeting_details)
                
                # Try to schedule if possible
                event_id = None
                if meeting_details.get('proposed_dates'):
                    event_id = self.calendar_tool.schedule_from_email_request(meeting_details)
                
                action = EmailAction(
                    email_id=email.id,
                    action_type='calendar_create',
                    action_data=meeting_details,
                    status='completed' if event_id else 'pending'
                )
                
                if event_id:
                    action.action_data['event_id'] = event_id
                
                session.add(action)
                
                return {
                    'type': 'calendar_create',
                    'status': 'completed' if event_id else 'pending',
                    'event_id': event_id
                }
            
        except Exception as e:
            logger.error(f"Error handling meeting request: {e}")
            return None
    
    def _perform_web_search(self, email: Email, session: Session) -> Optional[Dict]:
        """Perform web search for email questions."""
        try:
            search_results = self.web_search.search_for_email_context(
                email.subject, email.body
            )
            
            action = EmailAction(
                email_id=email.id,
                action_type='web_search',
                action_data={'query': f"{email.subject} {email.body[:100]}"},
                status='completed' if search_results else 'failed'
            )
            
            if search_results:
                action.action_data['results'] = search_results
            else:
                action.error_message = 'No search results found'
            
            session.add(action)
            
            return {
                'type': 'web_search',
                'status': 'completed' if search_results else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return None
    
    def _generate_auto_reply(self, email: Email, analysis: Dict, 
                           session: Session) -> Optional[Dict]:
        """Generate and optionally send auto-reply."""
        try:
            # Get web search context if available
            search_action = session.query(EmailAction).filter(
                EmailAction.email_id == email.id,
                EmailAction.action_type == 'web_search',
                EmailAction.status == 'completed'
            ).first()
            
            context = {}
            if search_action and search_action.action_data.get('results'):
                context['search_results'] = search_action.action_data['results']
            
            # Generate reply
            reply_content = self.openai_service.generate_reply(
                {
                    'sender': email.sender,
                    'subject': email.subject,
                    'body': email.body
                },
                context
            )
            
            # Store reply in database
            reply_record = EmailReply(
                original_email_id=email.id,
                reply_content=reply_content,
                reply_type='auto' if settings.auto_reply_enabled else 'draft',
                confidence_score=analysis.get('confidence', 'medium')
            )
            
            session.add(reply_record)
            
            # Send reply if auto-reply is enabled and confidence is high
            sent = False
            if (settings.auto_reply_enabled and 
                analysis.get('confidence') == 'high'):
                sent = self.gmail_service.send_reply(
                    email.message_id, 
                    reply_content
                )
                
                if sent:
                    reply_record.reply_type = 'sent'
                    reply_record.sent_at = datetime.utcnow()
                    email.is_replied = True
            
            return {
                'type': 'auto_reply',
                'status': 'sent' if sent else 'drafted',
                'reply_id': reply_record.id
            }
            
        except Exception as e:
            logger.error(f"Error generating auto-reply: {e}")
            return None
    
    def get_processing_summary(self, days: int = 7) -> Dict:
        """Get summary of email processing activity."""
        with self.session_maker() as session:
            # Count emails processed in last N days
            since_date = datetime.utcnow() - timedelta(days=days)
            
            emails_count = session.query(Email).filter(
                Email.timestamp >= since_date
            ).count()
            
            actions_count = session.query(EmailAction).join(Email).filter(
                Email.timestamp >= since_date
            ).count()
            
            replies_count = session.query(EmailReply).join(Email).filter(
                Email.timestamp >= since_date
            ).count()
            
            return {
                'emails_processed': emails_count,
                'actions_performed': actions_count,
                'replies_generated': replies_count,
                'period_days': days
            }