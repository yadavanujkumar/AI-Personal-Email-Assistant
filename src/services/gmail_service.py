"""
Gmail service for fetching and sending emails using Gmail API.
"""
import os
import pickle
import base64
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailService:
    """Service for interacting with Gmail API."""
    
    def __init__(self, credentials_file: str, token_file: str):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    raise FileNotFoundError(
                        f"Gmail credentials file not found: {self.credentials_file}. "
                        "Please download from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")
    
    def get_messages(self, query: str = '', max_results: int = 50) -> List[Dict]:
        """
        Fetch messages from Gmail inbox.
        
        Args:
            query: Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')
            max_results: Maximum number of messages to fetch
            
        Returns:
            List of message dictionaries
        """
        try:
            # Get list of message IDs
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No messages found")
                return []
            
            # Fetch full message details
            full_messages = []
            for message in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                parsed_msg = self._parse_message(msg_detail)
                if parsed_msg:
                    full_messages.append(parsed_msg)
            
            logger.info(f"Fetched {len(full_messages)} messages")
            return full_messages
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []
    
    def _parse_message(self, message: Dict) -> Optional[Dict]:
        """Parse Gmail message into structured format."""
        try:
            headers = message['payload'].get('headers', [])
            header_dict = {h['name'].lower(): h['value'] for h in headers}
            
            # Extract message body
            body = self._extract_body(message['payload'])
            
            parsed = {
                'id': message['id'],
                'thread_id': message['threadId'],
                'message_id': header_dict.get('message-id', ''),
                'sender': header_dict.get('from', ''),
                'recipient': header_dict.get('to', ''),
                'subject': header_dict.get('subject', ''),
                'date': header_dict.get('date', ''),
                'body': body.get('text', ''),
                'html_body': body.get('html', ''),
                'snippet': message.get('snippet', ''),
                'has_attachments': self._has_attachments(message['payload']),
                'labels': message.get('labelIds', []),
                'timestamp': datetime.fromtimestamp(int(message['internalDate']) / 1000)
            }
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    def _extract_body(self, payload: Dict) -> Dict[str, str]:
        """Extract text and HTML body from message payload."""
        body = {'text': '', 'html': ''}
        
        def extract_part(part):
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    body['text'] = base64.urlsafe_b64decode(data).decode('utf-8')
            
            elif part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    body['html'] = base64.urlsafe_b64decode(data).decode('utf-8')
            
            # Handle multipart messages
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_part(subpart)
        
        extract_part(payload)
        return body
    
    def _has_attachments(self, payload: Dict) -> bool:
        """Check if message has attachments."""
        def check_part(part):
            if part.get('filename'):
                return True
            if 'parts' in part:
                return any(check_part(subpart) for subpart in part['parts'])
            return False
        
        return check_part(payload)
    
    def send_reply(self, original_message_id: str, reply_content: str, 
                  subject: str = None) -> bool:
        """
        Send a reply to an email.
        
        Args:
            original_message_id: ID of the original message
            reply_content: Content of the reply
            subject: Subject line (optional)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Get original message details
            original = self.service.users().messages().get(
                userId='me', 
                id=original_message_id
            ).execute()
            
            headers = original['payload'].get('headers', [])
            header_dict = {h['name'].lower(): h['value'] for h in headers}
            
            # Create reply message
            reply_msg = MIMEText(reply_content)
            reply_msg['To'] = header_dict.get('from', '')
            reply_msg['Subject'] = subject or f"Re: {header_dict.get('subject', '')}"
            reply_msg['In-Reply-To'] = header_dict.get('message-id', '')
            reply_msg['References'] = header_dict.get('message-id', '')
            
            # Send the message
            raw_message = base64.urlsafe_b64encode(
                reply_msg.as_bytes()
            ).decode('utf-8')
            
            send_message = {
                'raw': raw_message,
                'threadId': original['threadId']
            }
            
            result = self.service.users().messages().send(
                userId='me', 
                body=send_message
            ).execute()
            
            logger.info(f"Reply sent successfully: {result['id']}")
            return True
            
        except HttpError as error:
            logger.error(f"Failed to send reply: {error}")
            return False
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            logger.error(f"Failed to mark message as read: {error}")
            return False