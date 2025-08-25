#!/usr/bin/env python3
"""
Comprehensive demo script showing all AI Personal Email Assistant capabilities.
This demonstrates how the system would work with real email data.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def demo_email_processing_workflow():
    """Demonstrate the complete email processing workflow."""
    print("📧 Email Processing Workflow Demo")
    print("=" * 50)
    
    # Simulate incoming emails
    sample_emails = [
        {
            'id': 'msg001',
            'sender': 'sarah.chen@techcorp.com',
            'subject': 'URGENT: Project deadline moved up',
            'body': '''Hi team,
            
I just received word from the client that they need the project delivered 
by Friday instead of next Monday. Can we schedule an emergency meeting 
tomorrow at 2 PM to discuss how to accelerate the timeline?

Please confirm your availability ASAP.

Best regards,
Sarah Chen
Project Manager''',
            'timestamp': datetime.now() - timedelta(minutes=5),
            'priority': 'high'
        },
        {
            'id': 'msg002', 
            'sender': 'alex.kumar@startup.io',
            'subject': 'Question about API rate limits',
            'body': '''Hello,

I'm integrating with your API and running into rate limiting issues. 
The documentation mentions 1000 requests per hour, but I'm getting 
429 errors after just 100 requests. 

Could you clarify the actual limits and suggest best practices for 
handling rate limits in production?

Thanks,
Alex Kumar''',
            'timestamp': datetime.now() - timedelta(minutes=15),
            'priority': 'medium'
        },
        {
            'id': 'msg003',
            'sender': 'marketing@newsletter.com', 
            'subject': 'Weekly Newsletter - Latest Industry Trends',
            'body': '''Check out this week's top stories:
            
- AI adoption reaches new highs
- Remote work trends for 2024
- New productivity tools launched

Click here to read more...''',
            'timestamp': datetime.now() - timedelta(hours=1),
            'priority': 'low'
        }
    ]
    
    print(f"📥 Processing {len(sample_emails)} incoming emails...\n")
    
    for i, email in enumerate(sample_emails, 1):
        print(f"📧 Email {i}: {email['subject']}")
        print(f"   From: {email['sender']}")
        print(f"   Received: {email['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Simulate AI analysis
        if 'urgent' in email['subject'].lower() or 'meeting' in email['body'].lower():
            analysis = {
                'intent': 'meeting_request',
                'priority': 'high',
                'requires_action': True,
                'key_points': ['Emergency meeting', 'Project deadline', 'Tomorrow 2 PM'],
                'suggested_actions': ['slack_notify', 'calendar_check', 'auto_reply']
            }
        elif '?' in email['body'] or 'question' in email['subject'].lower():
            analysis = {
                'intent': 'technical_question', 
                'priority': 'medium',
                'requires_action': True,
                'key_points': ['API rate limits', 'Documentation clarification', '429 errors'],
                'suggested_actions': ['web_search', 'auto_reply']
            }
        else:
            analysis = {
                'intent': 'newsletter',
                'priority': 'low', 
                'requires_action': False,
                'key_points': ['Marketing content', 'Industry news'],
                'suggested_actions': []
            }
        
        print(f"   🧠 AI Analysis:")
        print(f"      Intent: {analysis['intent']}")
        print(f"      Priority: {analysis['priority']}")
        print(f"      Key Points: {', '.join(analysis['key_points'])}")
        
        # Simulate actions taken
        if analysis['suggested_actions']:
            print(f"   ⚡ Actions Taken:")
            for action in analysis['suggested_actions']:
                if action == 'slack_notify':
                    print(f"      ✅ Sent Slack notification to #project-team")
                elif action == 'calendar_check':
                    print(f"      ✅ Checked calendar availability for tomorrow 2 PM")
                elif action == 'web_search':
                    print(f"      ✅ Searched for 'API rate limiting best practices'")
                elif action == 'auto_reply':
                    print(f"      ✅ Generated and sent automated reply")
        
        print()

def demo_slack_integration():
    """Demonstrate Slack integration capabilities."""
    print("\n🔔 Slack Integration Demo")
    print("=" * 50)
    
    scenarios = [
        {
            'trigger': 'High priority email received',
            'email_subject': 'URGENT: Server outage in production',
            'slack_message': '''🚨 High Priority Email Alert

📧 From: devops@company.com
📝 Subject: URGENT: Server outage in production
⏰ Received: Just now

Action Required: Immediate attention needed'''
        },
        {
            'trigger': 'Meeting request detected',
            'email_subject': 'Team sync tomorrow at 3 PM?',
            'slack_message': '''📅 Meeting Request Detected

🤝 Meeting: Team sync
⏰ Proposed time: Tomorrow at 3 PM
👥 Organizer: sarah@company.com

Calendar integration: Checking availability...'''
        },
        {
            'trigger': 'Daily summary report',
            'email_subject': 'Daily Email Processing Summary',
            'slack_message': '''📊 Email Assistant Daily Summary

✅ Processed: 23 emails
🤖 Auto-replied: 8 emails  
📅 Scheduled: 3 meetings
🔍 Web searches: 5 queries

All systems operational'''
        }
    ]
    
    for scenario in scenarios:
        print(f"🎬 Scenario: {scenario['trigger']}")
        print(f"📧 Email: {scenario['email_subject']}")
        print(f"💬 Slack Message:")
        print("   " + "\n   ".join(scenario['slack_message'].split('\n')))
        print()

def demo_calendar_integration():
    """Demonstrate calendar integration capabilities."""
    print("\n📅 Calendar Integration Demo") 
    print("=" * 50)
    
    # Simulate calendar availability check
    print("🔍 Checking calendar availability...")
    
    current_time = datetime.now()
    available_slots = [
        current_time.replace(hour=10, minute=0) + timedelta(days=1),
        current_time.replace(hour=14, minute=0) + timedelta(days=1), 
        current_time.replace(hour=16, minute=30) + timedelta(days=1),
    ]
    
    print("   Available time slots found:")
    for slot in available_slots:
        print(f"      • {slot.strftime('%A, %B %d at %I:%M %p')}")
    
    # Simulate meeting scheduling
    print("\n📝 Scheduling meeting based on email request...")
    meeting_details = {
        'title': 'Project Timeline Discussion',
        'organizer': 'sarah.chen@techcorp.com',
        'duration': '1 hour',
        'location': 'Conference Room A / Zoom',
        'attendees': ['team@company.com'],
        'agenda': 'Discuss accelerated project timeline and resource allocation'
    }
    
    print(f"   📅 Meeting Created:")
    print(f"      Title: {meeting_details['title']}")
    print(f"      Time: {available_slots[1].strftime('%A, %B %d at %I:%M %p')}")
    print(f"      Duration: {meeting_details['duration']}")
    print(f"      Location: {meeting_details['location']}")
    print(f"      Attendees: {', '.join(meeting_details['attendees'])}")
    
    # Simulate calendar invite
    print(f"\n✉️  Calendar invite sent to all attendees")
    print(f"🔔 Reminder set for 15 minutes before meeting")

def demo_web_search_integration():
    """Demonstrate web search integration."""
    print("\n🔍 Web Search Integration Demo")
    print("=" * 50)
    
    search_scenarios = [
        {
            'query': 'API rate limiting best practices 2024',
            'context': 'Technical question about API limits',
            'results': [
                {
                    'title': 'API Rate Limiting Best Practices - Developer Guide',
                    'url': 'https://example.com/api-rate-limits',
                    'snippet': 'Implement exponential backoff, use token bucket algorithms, and provide clear error messages for rate limit responses...'
                },
                {
                    'title': 'Handling Rate Limits in Production APIs',
                    'url': 'https://techblog.com/rate-limits', 
                    'snippet': 'Best practices include caching responses, implementing circuit breakers, and monitoring usage patterns...'
                }
            ]
        },
        {
            'query': 'project management acceleration techniques',
            'context': 'Meeting request about accelerated timeline',
            'results': [
                {
                    'title': 'How to Accelerate Project Timelines Effectively',
                    'url': 'https://pmguide.com/acceleration',
                    'snippet': 'Focus on critical path optimization, resource reallocation, and scope prioritization...'
                }
            ]
        }
    ]
    
    for scenario in search_scenarios:
        print(f"🎯 Search Context: {scenario['context']}")
        print(f"🔍 Query: {scenario['query']}")
        print(f"📊 Results found: {len(scenario['results'])}")
        
        for i, result in enumerate(scenario['results'], 1):
            print(f"   {i}. {result['title']}")
            print(f"      {result['snippet']}")
            print(f"      Source: {result['url']}")
        print()

def demo_auto_reply_generation():
    """Demonstrate automated reply generation."""
    print("\n🤖 Auto-Reply Generation Demo")
    print("=" * 50)
    
    reply_scenarios = [
        {
            'original_email': {
                'from': 'alex.kumar@startup.io',
                'subject': 'Question about API rate limits',
                'body': 'I\'m getting 429 errors after 100 requests. What are the actual limits?'
            },
            'generated_reply': '''Hello Alex,

Thank you for reaching out about the API rate limits. 

Based on our current documentation and system configuration:
- Standard tier: 1,000 requests per hour per API key
- If you're hitting limits at 100 requests, this might indicate:
  1. Multiple concurrent connections from the same key
  2. Cached rate limit counters (resets hourly)
  3. Possible burst limit restrictions

I recommend implementing exponential backoff and monitoring your request patterns. I've also found some helpful resources about API rate limiting best practices that I'll include below.

Would you like to schedule a quick call to discuss your specific use case?

Best regards,
AI Email Assistant''',
            'confidence': 'high'
        },
        {
            'original_email': {
                'from': 'sarah.chen@techcorp.com', 
                'subject': 'Emergency meeting tomorrow 2 PM',
                'body': 'Can we meet tomorrow at 2 PM to discuss the accelerated timeline?'
            },
            'generated_reply': '''Hi Sarah,

I've checked my calendar and I'm available tomorrow at 2 PM for the emergency meeting about the project timeline.

I've also done some preliminary research on project acceleration techniques that might be helpful for our discussion. I'll prepare a brief overview of options for resource reallocation and critical path optimization.

Should we set up a Zoom room or meet in Conference Room A?

Looking forward to working through this challenge together.

Best regards,
AI Email Assistant''',
            'confidence': 'high'
        }
    ]
    
    for i, scenario in enumerate(reply_scenarios, 1):
        orig = scenario['original_email']
        print(f"📧 Original Email {i}:")
        print(f"   From: {orig['from']}")
        print(f"   Subject: {orig['subject']}")
        print(f"   Body: {orig['body']}")
        
        print(f"\n🤖 Generated Reply (Confidence: {scenario['confidence']}):")
        print("   " + "\n   ".join(scenario['generated_reply'].split('\n')))
        print()

def demo_database_insights():
    """Demonstrate database and analytics capabilities."""
    print("\n📊 Database & Analytics Demo")
    print("=" * 50)
    
    # Simulate database statistics
    stats = {
        'total_emails': 1247,
        'emails_this_week': 89,
        'auto_replies_sent': 23,
        'meetings_scheduled': 7,
        'slack_notifications': 15,
        'web_searches': 31,
        'average_response_time': '2.3 minutes',
        'top_senders': [
            ('sarah.chen@techcorp.com', 18),
            ('support@client.com', 12),
            ('alex.kumar@startup.io', 8)
        ],
        'intent_breakdown': {
            'questions': 35,
            'meeting_requests': 12, 
            'information': 28,
            'urgent': 8,
            'other': 6
        }
    }
    
    print("📈 Email Processing Statistics (Last 7 days):")
    print(f"   Total Emails: {stats['total_emails']}")
    print(f"   This Week: {stats['emails_this_week']}")
    print(f"   Auto-replies: {stats['auto_replies_sent']}")
    print(f"   Meetings Scheduled: {stats['meetings_scheduled']}")
    print(f"   Avg Response Time: {stats['average_response_time']}")
    
    print(f"\n👥 Top Email Senders:")
    for sender, count in stats['top_senders']:
        print(f"   {sender}: {count} emails")
    
    print(f"\n🎯 Email Intent Analysis:")
    for intent, count in stats['intent_breakdown'].items():
        print(f"   {intent.title()}: {count} emails")
    
    print(f"\n⚡ Action Summary:")
    print(f"   Slack Notifications: {stats['slack_notifications']}")
    print(f"   Web Searches: {stats['web_searches']}")
    print(f"   Calendar Events: {stats['meetings_scheduled']}")

def main():
    """Run the comprehensive demo."""
    print("🎯 AI Personal Email Assistant - Comprehensive Demo")
    print("=" * 70)
    print("\nThis demo showcases all the capabilities of the AI Email Assistant")
    print("with realistic scenarios and data.\n")
    
    try:
        demo_email_processing_workflow()
        demo_slack_integration()
        demo_calendar_integration()
        demo_web_search_integration()
        demo_auto_reply_generation()
        demo_database_insights()
        
        print("\n🎉 Comprehensive Demo Completed!")
        print("\n" + "=" * 70)
        print("🚀 Ready to Process Real Emails!")
        print("\nNext Steps:")
        print("1. Set up API credentials (.env configuration)")
        print("2. Run: python main.py --once (process current emails)")
        print("3. Run: python main.py --continuous (monitor continuously)")
        print("4. Check logs and database for processing results")
        print("\nFor setup help: python main.py --setup")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo error: {e}")

if __name__ == "__main__":
    main()