# AI Personal Email Assistant

An intelligent email assistant that uses AI to automatically read, analyze, and respond to emails while integrating with external tools like Slack, Google Calendar, and web search.

## 🎯 Features

- **Email Integration**: Full Gmail API integration with OAuth2 authentication
- **AI Analysis**: Uses OpenAI GPT models to understand email content and intent
- **Smart Actions**: Automatically performs actions based on email content:
  - Sends Slack notifications for important emails
  - Schedules meetings when requested
  - Performs web searches to answer questions
  - Generates and sends automated replies
- **Database Storage**: Stores emails and conversation history in SQLite
- **Tool Integration**: Seamlessly integrates with:
  - Gmail API for email operations
  - Slack API for notifications
  - Google Calendar API for scheduling
  - Google Custom Search for web research

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gmail API     │    │   OpenAI API    │    │  External Tools │
│                 │    │                 │    │                 │
│ • Read emails   │    │ • Analyze       │    │ • Slack         │
│ • Send replies  │    │ • Generate      │    │ • Calendar      │
│ • Mark as read  │    │ • Summarize     │    │ • Web Search    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Email Assistant │
                    │   Controller    │
                    │                 │
                    │ • Orchestrates  │
                    │ • Decision      │
                    │ • Actions       │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │                 │
                    │ • Emails        │
                    │ • Threads       │
                    │ • Actions       │
                    │ • Replies       │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Project with APIs enabled
- OpenAI API account
- Slack workspace (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yadavanujkumar/AI-Personal-Email-Assistant.git
   cd AI-Personal-Email-Assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Setup credentials directory**
   ```bash
   python main.py --setup
   ```

### Configuration

#### 1. Environment Variables (.env)

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=credentials/gmail_credentials.json
GMAIL_TOKEN_FILE=credentials/gmail_token.json

# Google Search API Configuration
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_custom_search_engine_id_here

# Slack Configuration (optional)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_CHANNEL=#general

# Google Calendar Configuration
CALENDAR_CREDENTIALS_FILE=credentials/calendar_credentials.json
CALENDAR_TOKEN_FILE=credentials/calendar_token.json

# Application Configuration
DATABASE_URL=sqlite:///email_assistant.db
AUTO_REPLY_ENABLED=false
MAX_EMAILS_FETCH=50
EMAIL_CHECK_INTERVAL=300
```

#### 2. Google API Credentials

**Gmail API Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the JSON file and save as `credentials/gmail_credentials.json`

**Google Calendar API Setup:**
1. In the same Google Cloud project
2. Enable Google Calendar API
3. Use the same OAuth 2.0 credentials or create new ones
4. Save as `credentials/calendar_credentials.json`

**Google Custom Search API:**
1. Enable Custom Search API in Google Cloud Console
2. Create API key
3. Set up a Custom Search Engine at [Google Custom Search](https://cse.google.com/)
4. Get the Search Engine ID

#### 3. Slack Setup (Optional)

1. Create a Slack app at [Slack API](https://api.slack.com/apps)
2. Add Bot Token Scopes: `chat:write`, `channels:read`
3. Install app to workspace
4. Copy Bot User OAuth Token

#### 4. OpenAI Setup

1. Create account at [OpenAI](https://platform.openai.com/)
2. Generate API key
3. Add to environment variables

## 📖 Usage

### Command Line Interface

```bash
# Run once and exit
python main.py --once

# Run continuously (monitors for new emails)
python main.py --continuous

# Run demo mode
python main.py --demo

# Setup mode (creates directories and shows instructions)
python main.py --setup
```

### Example Workflow

1. **Email arrives** in your Gmail inbox
2. **Assistant fetches** the email using Gmail API
3. **AI analyzes** the email content to understand intent
4. **Actions are performed** based on analysis:
   - High priority emails → Slack notification
   - Meeting requests → Calendar scheduling
   - Questions → Web search for answers
   - Actionable emails → Draft/send replies
5. **Database stores** all email data and actions
6. **Email marked** as read in Gmail

## 🔧 Architecture Details

### Project Structure

```
├── src/
│   ├── controllers/
│   │   └── email_assistant.py      # Main orchestrator
│   ├── services/
│   │   ├── gmail_service.py        # Gmail API integration
│   │   └── openai_service.py       # OpenAI API integration
│   ├── tools/
│   │   ├── web_search.py           # Google Search integration
│   │   ├── slack_tool.py           # Slack API integration
│   │   └── calendar_tool.py        # Google Calendar integration
│   ├── models/
│   │   └── database.py             # Database models and schema
│   ├── utils/
│   │   ├── logger.py               # Logging configuration
│   │   └── email_parser.py         # Email parsing utilities
│   └── config/
│       └── settings.py             # Configuration management
├── credentials/                    # API credentials (not in repo)
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

### Database Schema

**Emails Table:**
- Stores email content, metadata, and AI analysis results
- Links to conversation threads

**Email Replies Table:**
- Stores AI-generated replies
- Tracks confidence scores and send status

**Email Actions Table:**
- Records all actions taken (Slack, Calendar, Web Search)
- Stores action results and error messages

**Conversation Threads Table:**
- Groups related emails by thread
- Tracks conversation metadata

### AI Workflow

1. **Email Analysis**: Extract intent, priority, and summary
2. **Context Enhancement**: Web search for additional information
3. **Action Decision**: Determine appropriate actions
4. **Reply Generation**: Create personalized responses
5. **Quality Control**: Confidence scoring and human oversight

## 🔒 Security & Privacy

- **OAuth2 Authentication**: Secure Google API access
- **Local Storage**: Emails stored locally in SQLite
- **API Key Management**: Environment-based configuration
- **Permission Scopes**: Minimal required Gmail/Calendar permissions
- **Data Encryption**: Secure token storage

## 🧪 Testing

The assistant includes several safety features:

- **Dry Run Mode**: Test without sending emails
- **Confidence Thresholds**: Only auto-send high-confidence replies
- **Human Oversight**: Draft mode for review before sending
- **Logging**: Comprehensive logging for debugging

## 🚨 Troubleshooting

### Common Issues

**Authentication Errors:**
- Ensure credentials files are in the correct location
- Check API quotas in Google Cloud Console
- Verify OAuth scopes are correctly configured

**Missing Dependencies:**
```bash
pip install -r requirements.txt
```

**Database Issues:**
- Delete `email_assistant.db` to reset database
- Check file permissions in project directory

**API Rate Limits:**
- Reduce `MAX_EMAILS_FETCH` in configuration
- Increase `EMAIL_CHECK_INTERVAL` for continuous mode

## 📊 Monitoring & Analytics

The assistant provides processing summaries:

```python
assistant = EmailAssistant()
summary = assistant.get_processing_summary(days=7)
print(f"Processed {summary['emails_processed']} emails in last 7 days")
```

## 🔮 Future Enhancements

- **Web Interface**: Flask/Django web UI
- **Mobile App**: React Native mobile client
- **Advanced AI**: Fine-tuned models for specific use cases
- **Multi-Account**: Support for multiple email accounts
- **Plugin System**: Extensible tool integration
- **Analytics Dashboard**: Email processing insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Google for Gmail, Calendar, and Search APIs
- Slack for messaging API
- Python community for excellent libraries

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub

---

**Note**: This is a prototype built as a learning exercise. Use caution when enabling auto-reply features in production environments.