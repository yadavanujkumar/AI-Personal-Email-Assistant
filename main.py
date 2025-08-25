"""
Main application entry point for the AI Personal Email Assistant.
"""
import os
import sys
import time
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def setup_credentials_directory():
    """Create credentials directory if it doesn't exist."""
    credentials_dir = Path("credentials")
    credentials_dir.mkdir(exist_ok=True)
    
    # Check if credential files exist and provide helpful messages
    gmail_creds = Path("credentials/gmail_credentials.json")
    calendar_creds = Path("credentials/calendar_credentials.json")
    
    if not gmail_creds.exists():
        print(f"⚠️  Gmail credentials file not found: {gmail_creds}")
        print("📝 Please download Gmail API credentials from Google Cloud Console")
        print("   and save as 'credentials/gmail_credentials.json'")
    
    if not calendar_creds.exists():
        print(f"⚠️  Calendar credentials file not found: {calendar_creds}")
        print("📝 Please download Google Calendar API credentials from Google Cloud Console")
        print("   and save as 'credentials/calendar_credentials.json'")


def run_once():
    """Run email processing once."""
    from src.config.settings import settings
    from src.controllers.email_assistant import EmailAssistant
    from src.utils.logger import configure_logging, get_logger
    
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    logger.info("Running email assistant (single run)")
    
    try:
        assistant = EmailAssistant()
        summary = assistant.process_emails()
        
        logger.info("Email processing completed successfully")
        logger.info(f"Summary: {summary}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error running email assistant: {e}")
        return None


def run_continuous():
    """Run email processing continuously."""
    from src.config.settings import settings
    from src.controllers.email_assistant import EmailAssistant
    from src.utils.logger import configure_logging, get_logger
    
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    logger.info(f"Starting continuous email monitoring (interval: {settings.email_check_interval}s)")
    
    try:
        assistant = EmailAssistant()
        
        while True:
            logger.info("Checking for new emails...")
            summary = assistant.process_emails()
            
            if summary['processed'] > 0:
                logger.info(f"Processed {summary['processed']} emails")
            else:
                logger.info("No new emails to process")
            
            logger.info(f"Waiting {settings.email_check_interval} seconds until next check...")
            time.sleep(settings.email_check_interval)
            
    except KeyboardInterrupt:
        logger.info("Email assistant stopped by user")
    except Exception as e:
        logger.error(f"Error in continuous mode: {e}")


def run_demo():
    """Run a demo of the email assistant capabilities."""
    from src.config.settings import settings
    from src.controllers.email_assistant import EmailAssistant
    from src.utils.logger import configure_logging, get_logger
    
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    logger.info("Running email assistant demo")
    
    try:
        assistant = EmailAssistant()
        
        # Get recent summary
        summary = assistant.get_processing_summary(days=30)
        logger.info(f"Recent activity (30 days): {summary}")
        
        # Check for any unread emails
        logger.info("Checking for unread emails...")
        processing_summary = assistant.process_emails(max_emails=5)
        
        logger.info("Demo completed successfully")
        return processing_summary
        
    except Exception as e:
        logger.error(f"Error running demo: {e}")
        return None


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="AI Personal Email Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --once              # Process emails once and exit
  python main.py --continuous        # Run continuously
  python main.py --demo              # Run demo mode
  python main.py --setup             # Setup credentials directory
        """
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run email processing once and exit'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run email processing continuously'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Setup credentials directory and show setup instructions'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set logging level'
    )
    
    args = parser.parse_args()
    
    # Show banner
    print("=" * 60)
    print("          AI Personal Email Assistant")
    print("=" * 60)
    print()
    
    # Setup mode
    if args.setup:
        setup_credentials_directory()
        print("\n🚀 Setup Instructions:")
        print("1. Copy .env.example to .env and fill in your API keys")
        print("2. Download Google API credentials and place in credentials/")
        print("3. Run with --demo to test the setup")
        print()
        return
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠️  .env file not found. Please copy .env.example to .env and configure.")
        print("\n🔧 Quick setup:")
        print("1. cp .env.example .env")
        print("2. Edit .env with your API keys")
        print("3. Run with --setup for credential setup")
        print()
        return
    
    try:
        # Import settings here to avoid issues in setup mode
        from src.config.settings import settings
        from src.utils.logger import configure_logging
        
        # Configure logging
        configure_logging(args.log_level)
        
        # Run based on mode
        if args.demo:
            run_demo()
        elif args.once:
            run_once()
        elif args.continuous:
            run_continuous()
        else:
            # Default: show help and run demo
            parser.print_help()
            print("\nNo mode specified. Running demo...")
            run_demo()
            
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
    except Exception as e:
        print(f"\n\nApplication error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()