#!/usr/bin/env python3
"""
Demo script for the AI Personal Email Assistant.
This script demonstrates the capabilities without requiring full setup.
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def demo_email_analysis():
    """Demo the email analysis capabilities."""
    print("🤖 AI Email Analysis Demo")
    print("=" * 40)
    
    # Mock email data
    sample_emails = [
        {
            'sender': 'john.doe@company.com',
            'subject': 'Urgent: Meeting tomorrow at 2 PM',
            'body': 'Hi, we need to schedule a meeting tomorrow at 2 PM to discuss the project timeline. Can you confirm your availability? Let me know if this time works for you.',
            'timestamp': '2024-01-15 10:30:00'
        },
        {
            'sender': 'support@service.com',
            'subject': 'How to integrate API with Python?',
            'body': 'I am trying to integrate your API with my Python application but getting authentication errors. Can you provide documentation or examples?',
            'timestamp': '2024-01-15 14:22:00'
        },
        {
            'sender': 'marketing@company.com',
            'subject': 'Newsletter: Latest Updates',
            'body': 'Check out our latest product updates and features in this month\'s newsletter. We have exciting new features and improvements.',
            'timestamp': '2024-01-15 09:15:00'
        }
    ]
    
    # Demo analysis without actually calling OpenAI
    for i, email in enumerate(sample_emails, 1):
        print(f"\n📧 Email {i}:")
        print(f"   From: {email['sender']}")
        print(f"   Subject: {email['subject']}")
        print(f"   Body: {email['body'][:80]}...")
        
        # Mock AI analysis based on content
        if 'meeting' in email['subject'].lower() or 'meeting' in email['body'].lower():
            analysis = {
                'intent': 'meeting',
                'priority': 'high',
                'requires_action': True,
                'summary': 'Meeting request for tomorrow at 2 PM',
                'suggested_actions': ['calendar_create', 'slack_notify']
            }
        elif '?' in email['body'] or 'how' in email['body'].lower():
            analysis = {
                'intent': 'question',
                'priority': 'medium', 
                'requires_action': True,
                'summary': 'Technical support question about API integration',
                'suggested_actions': ['web_search', 'auto_reply']
            }
        else:
            analysis = {
                'intent': 'information',
                'priority': 'low',
                'requires_action': False,
                'summary': 'Newsletter or informational email',
                'suggested_actions': []
            }
        
        print(f"   🧠 AI Analysis:")
        print(f"      Intent: {analysis['intent']}")
        print(f"      Priority: {analysis['priority']}")
        print(f"      Requires Action: {analysis['requires_action']}")
        print(f"      Summary: {analysis['summary']}")
        if analysis['suggested_actions']:
            print(f"      Suggested Actions: {', '.join(analysis['suggested_actions'])}")


def demo_tool_integrations():
    """Demo the tool integration capabilities."""
    print("\n\n🔧 Tool Integration Demo")
    print("=" * 40)
    
    tools = [
        {
            'name': 'Slack Notification',
            'description': 'Sends alerts for high-priority emails',
            'example': 'Meeting request → Slack notification to #team-channel'
        },
        {
            'name': 'Calendar Scheduling',
            'description': 'Automatically schedules meetings from email requests',
            'example': 'Meeting request → Google Calendar event created'
        },
        {
            'name': 'Web Search',
            'description': 'Searches for information to answer questions',
            'example': 'API question → Google search for documentation'
        },
        {
            'name': 'Auto Reply',
            'description': 'Generates and sends intelligent responses',
            'example': 'Question email → AI-generated helpful reply'
        }
    ]
    
    for tool in tools:
        print(f"\n🛠️  {tool['name']}:")
        print(f"    Description: {tool['description']}")
        print(f"    Example: {tool['example']}")


def demo_workflow():
    """Demo the complete workflow."""
    print("\n\n🔄 Complete Workflow Demo")
    print("=" * 40)
    
    workflow_steps = [
        "📥 Email arrives in Gmail inbox",
        "🔍 Assistant fetches email via Gmail API",
        "🧠 AI analyzes email content and intent",
        "⚡ Actions performed based on analysis:",
        "   • High priority → Slack notification",
        "   • Meeting request → Calendar event",
        "   • Question → Web search + Reply",
        "💾 Email and actions stored in database",
        "✅ Email marked as read in Gmail"
    ]
    
    for step in workflow_steps:
        print(f"  {step}")


def demo_database_schema():
    """Demo the database structure."""
    print("\n\n🗄️  Database Schema Demo")
    print("=" * 40)
    
    tables = {
        'emails': ['id', 'message_id', 'sender', 'subject', 'body', 'intent', 'priority'],
        'email_replies': ['id', 'original_email_id', 'reply_content', 'confidence_score'],
        'email_actions': ['id', 'email_id', 'action_type', 'status', 'action_data'],
        'conversation_threads': ['id', 'thread_id', 'subject', 'participants', 'message_count']
    }
    
    for table, columns in tables.items():
        print(f"\n📋 Table: {table}")
        for col in columns:
            print(f"    • {col}")


def main():
    """Run the complete demo."""
    print("🎯 AI Personal Email Assistant - Demo Mode")
    print("=" * 60)
    print()
    print("This demo shows the capabilities of the AI Email Assistant")
    print("without requiring full API setup.")
    print()
    
    try:
        demo_email_analysis()
        demo_tool_integrations()
        demo_workflow()
        demo_database_schema()
        
        print("\n\n🎉 Demo completed successfully!")
        print("\nTo run the full assistant:")
        print("1. Set up API credentials (.env file)")
        print("2. Run: python main.py --once")
        print("\nFor continuous monitoring:")
        print("   python main.py --continuous")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo error: {e}")


if __name__ == "__main__":
    main()