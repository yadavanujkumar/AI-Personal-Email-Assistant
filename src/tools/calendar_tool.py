"""
Google Calendar integration tool for scheduling and managing events.
"""
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarTool:
    """Tool for Google Calendar integration."""
    
    def __init__(self, credentials_file: str, token_file: str):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API."""
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
                    logger.error(f"Calendar credentials file not found: {self.credentials_file}")
                    raise FileNotFoundError(
                        f"Calendar credentials file not found: {self.credentials_file}"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Calendar API")
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime,
                    description: str = None, attendees: List[str] = None,
                    location: str = None) -> Optional[str]:
        """
        Create a calendar event.
        
        Args:
            title: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description (optional)
            attendees: List of attendee email addresses (optional)
            location: Event location (optional)
            
        Returns:
            Event ID if created successfully, None otherwise
        """
        try:
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if description:
                event['description'] = description
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            result = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            event_id = result.get('id')
            logger.info(f"Calendar event created: {event_id}")
            return event_id
            
        except HttpError as error:
            logger.error(f"Failed to create calendar event: {error}")
            return None
    
    def find_free_time(self, duration_minutes: int = 60, 
                      days_ahead: int = 7) -> List[Dict]:
        """
        Find available time slots in the calendar.
        
        Args:
            duration_minutes: Required duration in minutes
            days_ahead: Number of days to look ahead
            
        Returns:
            List of available time slot dictionaries
        """
        try:
            # Get current time and future time boundary
            now = datetime.utcnow()
            time_max = now + timedelta(days=days_ahead)
            
            # Get busy times
            freebusy_query = {
                'timeMin': now.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'items': [{'id': 'primary'}]
            }
            
            freebusy_result = self.service.freebusy().query(
                body=freebusy_query
            ).execute()
            
            busy_times = freebusy_result['calendars']['primary']['busy']
            
            # Generate potential time slots (business hours: 9 AM - 5 PM)
            free_slots = []
            current_day = now.replace(hour=9, minute=0, second=0, microsecond=0)
            
            for day in range(days_ahead):
                day_start = current_day + timedelta(days=day)
                day_end = day_start.replace(hour=17)  # 5 PM
                
                # Skip weekends
                if day_start.weekday() >= 5:
                    continue
                
                # Check each hour slot
                slot_start = day_start
                while slot_start + timedelta(minutes=duration_minutes) <= day_end:
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    # Check if slot conflicts with busy times
                    if not self._is_time_busy(slot_start, slot_end, busy_times):
                        free_slots.append({
                            'start': slot_start,
                            'end': slot_end,
                            'duration_minutes': duration_minutes
                        })
                    
                    slot_start += timedelta(hours=1)
            
            logger.info(f"Found {len(free_slots)} available time slots")
            return free_slots
            
        except HttpError as error:
            logger.error(f"Error finding free time: {error}")
            return []
    
    def _is_time_busy(self, start: datetime, end: datetime, 
                     busy_times: List[Dict]) -> bool:
        """Check if a time slot conflicts with busy times."""
        for busy_period in busy_times:
            busy_start = datetime.fromisoformat(
                busy_period['start'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
            busy_end = datetime.fromisoformat(
                busy_period['end'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
            
            # Check for overlap
            if start < busy_end and end > busy_start:
                return True
        
        return False
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict]:
        """
        Get upcoming calendar events.
        
        Args:
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'No title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'attendees': [
                        attendee.get('email') 
                        for attendee in event.get('attendees', [])
                    ]
                })
            
            logger.info(f"Retrieved {len(formatted_events)} upcoming events")
            return formatted_events
            
        except HttpError as error:
            logger.error(f"Error getting upcoming events: {error}")
            return []
    
    def suggest_meeting_times(self, attendee_emails: List[str], 
                            duration_minutes: int = 60,
                            days_ahead: int = 7) -> List[str]:
        """
        Suggest meeting times based on availability.
        
        Args:
            attendee_emails: List of attendee email addresses
            duration_minutes: Meeting duration in minutes
            days_ahead: Number of days to look ahead
            
        Returns:
            List of suggested meeting time strings
        """
        free_slots = self.find_free_time(duration_minutes, days_ahead)
        
        if not free_slots:
            return ["No available time slots found"]
        
        # Format top 3 suggestions
        suggestions = []
        for slot in free_slots[:3]:
            start_time = slot['start']
            formatted_time = start_time.strftime("%A, %B %d at %I:%M %p")
            suggestions.append(formatted_time)
        
        return suggestions
    
    def schedule_from_email_request(self, meeting_data: Dict) -> Optional[str]:
        """
        Schedule a meeting based on extracted email data.
        
        Args:
            meeting_data: Dictionary containing meeting information
            
        Returns:
            Event ID if scheduled successfully, None otherwise
        """
        title = meeting_data.get('meeting_title', 'Meeting')
        attendees = meeting_data.get('attendees', [])
        
        # Try to parse proposed dates/times
        proposed_dates = meeting_data.get('proposed_dates', [])
        proposed_times = meeting_data.get('proposed_times', [])
        
        # If no specific time proposed, suggest next available slot
        if not proposed_dates or not proposed_times:
            free_slots = self.find_free_time(60, 7)  # 1 hour, 7 days ahead
            if free_slots:
                slot = free_slots[0]
                return self.create_event(
                    title=title,
                    start_time=slot['start'],
                    end_time=slot['end'],
                    attendees=attendees,
                    description="Meeting scheduled by AI Email Assistant"
                )
        
        # TODO: Parse specific dates/times from proposed_dates and proposed_times
        # This would require more sophisticated date/time parsing
        
        return None