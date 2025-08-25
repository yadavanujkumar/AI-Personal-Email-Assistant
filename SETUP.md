# API Setup Guide

This guide walks you through setting up all the required API credentials for the AI Personal Email Assistant.

## Required APIs

1. **OpenAI API** - For email analysis and reply generation
2. **Gmail API** - For reading and sending emails  
3. **Google Custom Search API** - For web search functionality
4. **Slack API** - For notifications (optional)
5. **Google Calendar API** - For meeting scheduling

## 1. OpenAI API Setup

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to "API Keys" 
4. Click "Create new secret key"
5. Copy the key and add to your `.env` file:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

## 2. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application" 
   - Download the JSON file
   - Save as `credentials/gmail_credentials.json`

**Required OAuth Scopes:**
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.modify`

## 3. Google Custom Search API Setup

1. In Google Cloud Console, enable "Custom Search API"
2. Create an API key:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the key
3. Set up Custom Search Engine:
   - Go to [Google Custom Search](https://cse.google.com/)
   - Click "Add" to create a new search engine
   - Enter `*` as the site to search (for entire web)
   - Get the Search Engine ID from the control panel
4. Add to `.env`:
   ```
   GOOGLE_SEARCH_API_KEY=your-api-key
   GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
   ```

## 4. Slack API Setup (Optional)

1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App" > "From scratch"
3. Choose app name and workspace
4. Add Bot Token Scopes:
   - Go to "OAuth & Permissions"
   - Add scopes: `chat:write`, `channels:read`
5. Install app to workspace
6. Copy "Bot User OAuth Token"
7. Add to `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_CHANNEL=#general
   ```

## 5. Google Calendar API Setup

1. In Google Cloud Console, enable "Google Calendar API"
2. Use the same OAuth 2.0 credentials from Gmail setup
3. Save credentials as `credentials/calendar_credentials.json`
4. Update `.env`:
   ```
   CALENDAR_CREDENTIALS_FILE=credentials/calendar_credentials.json
   CALENDAR_TOKEN_FILE=credentials/calendar_token.json
   ```

**Required OAuth Scopes:**
- `https://www.googleapis.com/auth/calendar`

## Environment Variables

Your final `.env` file should look like:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key

# Gmail API Configuration  
GMAIL_CREDENTIALS_FILE=credentials/gmail_credentials.json
GMAIL_TOKEN_FILE=credentials/gmail_token.json

# Google Search API Configuration
GOOGLE_SEARCH_API_KEY=your-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Slack Configuration (optional)
SLACK_BOT_TOKEN=xoxb-your-slack-token
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

## Testing Your Setup

1. Run setup mode: `python main.py --setup`
2. Copy credentials to the `credentials/` directory
3. Test with demo: `python main.py --demo`
4. Try processing emails: `python main.py --once`

## Troubleshooting

**Authentication Errors:**
- Make sure credential files are in the correct location
- Check that APIs are enabled in Google Cloud Console
- Verify OAuth scopes match requirements

**Quota Limits:**
- Check API usage in Google Cloud Console
- Gmail API: 1 billion quota units/day
- Custom Search: 100 queries/day (free tier)
- OpenAI: Based on your account limits

**Permission Issues:**
- Ensure OAuth consent screen is configured
- Add your email as a test user during development
- Publish the app for production use

## Security Notes

- Never commit credential files to version control
- Use environment variables for all sensitive data
- Regularly rotate API keys
- Set up proper OAuth scopes (minimal required permissions)
- Monitor API usage and costs