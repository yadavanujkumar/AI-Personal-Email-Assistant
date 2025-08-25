"""
Slack integration tool for sending notifications and messages.
"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Optional, Dict, List

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SlackTool:
    """Tool for sending Slack notifications and messages."""
    
    def __init__(self, bot_token: str, default_channel: str = "#general"):
        self.client = WebClient(token=bot_token)
        self.default_channel = default_channel
        self._verify_connection()
        logger.info("Slack tool initialized successfully")
    
    def _verify_connection(self):
        """Verify Slack API connection."""
        try:
            response = self.client.auth_test()
            if response["ok"]:
                logger.info(f"Connected to Slack as: {response['user']}")
            else:
                logger.error("Failed to authenticate with Slack")
        except SlackApiError as e:
            logger.error(f"Slack authentication error: {e}")
            raise
    
    def send_email_notification(self, email_data: Dict, channel: str = None) -> bool:
        """
        Send a notification about an important email.
        
        Args:
            email_data: Dictionary containing email information
            channel: Slack channel to send to (optional)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        channel = channel or self.default_channel
        
        # Create notification message
        sender = email_data.get('sender', 'Unknown')
        subject = email_data.get('subject', 'No subject')
        snippet = email_data.get('snippet', email_data.get('body', ''))[:200]
        
        message_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📧 Important Email Received"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*From:* {sender}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Subject:* {subject}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Preview:* {snippet}..."
                }
            }
        ]
        
        return self._send_message(channel, "Important email received", message_blocks)
    
    def send_meeting_notification(self, meeting_data: Dict, channel: str = None) -> bool:
        """
        Send a notification about a meeting request.
        
        Args:
            meeting_data: Dictionary containing meeting information
            channel: Slack channel to send to (optional)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        channel = channel or self.default_channel
        
        title = meeting_data.get('meeting_title', 'Meeting Request')
        dates = meeting_data.get('proposed_dates', [])
        times = meeting_data.get('proposed_times', [])
        
        message_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📅 Meeting Request Detected"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Meeting:* {title}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Proposed Dates:* {', '.join(dates) if dates else 'TBD'}"
                    }
                ]
            }
        ]
        
        if times:
            message_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Proposed Times:* {', '.join(times)}"
                }
            })
        
        return self._send_message(channel, "Meeting request detected", message_blocks)
    
    def send_action_summary(self, actions: List[Dict], channel: str = None) -> bool:
        """
        Send a summary of actions taken by the email assistant.
        
        Args:
            actions: List of action dictionaries
            channel: Slack channel to send to (optional)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        channel = channel or self.default_channel
        
        if not actions:
            return True
        
        message_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 Email Assistant Actions"
                }
            }
        ]
        
        for action in actions:
            action_type = action.get('action_type', 'Unknown')
            status = action.get('status', 'Unknown')
            
            status_emoji = "✅" if status == "completed" else "⏳" if status == "pending" else "❌"
            
            message_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji} *{action_type.replace('_', ' ').title()}*: {status}"
                }
            })
        
        return self._send_message(channel, "Email assistant actions", message_blocks)
    
    def send_custom_message(self, message: str, channel: str = None) -> bool:
        """
        Send a custom message to Slack.
        
        Args:
            message: Message text to send
            channel: Slack channel to send to (optional)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        channel = channel or self.default_channel
        return self._send_message(channel, message)
    
    def _send_message(self, channel: str, text: str, blocks: List[Dict] = None) -> bool:
        """
        Send a message to Slack.
        
        Args:
            channel: Slack channel
            text: Fallback text
            blocks: Message blocks for rich formatting
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            
            if response["ok"]:
                logger.info(f"Message sent to Slack channel: {channel}")
                return True
            else:
                logger.error(f"Failed to send Slack message: {response}")
                return False
                
        except SlackApiError as e:
            logger.error(f"Slack API error: {e}")
            return False
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Get information about a Slack user.
        
        Args:
            user_id: Slack user ID
            
        Returns:
            User information dictionary or None
        """
        try:
            response = self.client.users_info(user=user_id)
            if response["ok"]:
                return response["user"]
            return None
        except SlackApiError as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def list_channels(self) -> List[Dict]:
        """
        List available Slack channels.
        
        Returns:
            List of channel dictionaries
        """
        try:
            response = self.client.conversations_list()
            if response["ok"]:
                return response["channels"]
            return []
        except SlackApiError as e:
            logger.error(f"Error listing channels: {e}")
            return []