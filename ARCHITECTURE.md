# Architecture Documentation

## Overview

The AI Personal Email Assistant is designed with a modular architecture that separates concerns and allows for easy extension and maintenance.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Email Assistant                         │
│                       Controller                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Orchestration Layer                    │   │
│  │  • Email Processing Pipeline                        │   │
│  │  • Decision Making                                  │   │
│  │  • Action Coordination                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Services  │     │    Tools    │     │  Database   │
│             │     │             │     │             │
│ • Gmail     │     │ • Slack     │     │ • Emails    │
│ • OpenAI    │     │ • Calendar  │     │ • Replies   │
│             │     │ • Search    │     │ • Actions   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Core Components

### 1. Controllers Layer (`src/controllers/`)

**EmailAssistant** - Main orchestrator that coordinates all components
- Manages the email processing pipeline
- Makes decisions based on AI analysis
- Coordinates actions across tools and services
- Handles error recovery and logging

### 2. Services Layer (`src/services/`)

**GmailService** - Handles email operations
- OAuth2 authentication with Gmail API
- Fetches emails from inbox
- Sends replies and updates
- Parses email content and metadata

**OpenAIService** - AI-powered analysis and generation
- Email content analysis and intent detection
- Automated reply generation
- Meeting detail extraction
- Conversation summarization

### 3. Tools Layer (`src/tools/`)

**SlackTool** - Slack integration
- Sends notifications for important emails
- Posts meeting requests and updates
- Provides action summaries

**CalendarTool** - Google Calendar integration
- Schedules meetings based on email requests
- Finds available time slots
- Manages calendar events

**WebSearchTool** - Google Custom Search integration
- Searches for information to answer questions
- Provides context for email replies
- Filters and formats search results

### 4. Models Layer (`src/models/`)

**Database Models** - SQLAlchemy ORM models
- Email storage and metadata
- Conversation threading
- Action tracking and history
- Reply management

### 5. Utils Layer (`src/utils/`)

**EmailParser** - Email content processing
- Cleans and normalizes email text
- Extracts contact information
- Removes signatures and quoted text

**Logger** - Structured logging
- JSON-formatted logs
- Multiple log levels
- Performance monitoring

### 6. Config Layer (`src/config/`)

**Settings** - Configuration management
- Environment variable validation
- API key management
- Application parameters

## Data Flow

### Email Processing Pipeline

```
1. Fetch Emails (Gmail API)
         │
         ▼
2. Parse Content (EmailParser)
         │
         ▼
3. Store in Database (SQLAlchemy)
         │
         ▼
4. AI Analysis (OpenAI API)
         │
         ▼
5. Decision Making (Controller)
         │
         ▼
6. Action Execution (Tools)
         │
         ▼
7. Update Records (Database)
```

### Decision Tree

```
Email Received
    │
    ├─ High Priority? ────→ Send Slack Notification
    │
    ├─ Meeting Request? ──→ Extract Details → Schedule Calendar
    │
    ├─ Question? ─────────→ Web Search → Generate Reply
    │
    └─ General ───────────→ Store → Mark Read
```

## Database Schema

### Core Tables

```sql
-- Email storage with AI analysis
emails (
    id, message_id, thread_id,
    sender, recipient, subject, body,
    intent, priority, requires_action,
    ai_summary, timestamp
)

-- AI-generated replies
email_replies (
    id, original_email_id, reply_content,
    reply_type, confidence_score,
    created_at, sent_at
)

-- Action tracking
email_actions (
    id, email_id, action_type,
    action_data, status,
    created_at, completed_at
)

-- Conversation threading
conversation_threads (
    id, thread_id, subject,
    participants, message_count,
    first_message_date, last_message_date
)
```

## API Integration Patterns

### OAuth2 Flow
```python
# Gmail and Calendar APIs
1. Check for existing token
2. Refresh if expired
3. Re-authenticate if needed
4. Store new token securely
```

### Error Handling
```python
# Graceful degradation
try:
    perform_action()
except APIError:
    log_error()
    fallback_action()
except RateLimit:
    queue_for_retry()
```

### Rate Limiting
```python
# Respect API limits
- Gmail: 250 quota units/user/second
- OpenAI: Based on tier limits
- Custom Search: 100 queries/day (free)
```

## Security Considerations

### Data Protection
- Credentials stored outside repository
- Environment variable validation
- Secure token storage
- Local database only

### API Security
- Minimal OAuth scopes
- Token refresh handling
- Rate limit compliance
- Error message sanitization

### Privacy
- No email content sent to unnecessary services
- Local processing where possible
- User consent for auto-actions
- Audit trail maintenance

## Scalability Considerations

### Current Limitations
- Single user design
- Local SQLite database
- Synchronous processing
- No horizontal scaling

### Future Enhancements
- Multi-user support
- PostgreSQL for production
- Async processing with queues
- Microservices architecture
- Redis for caching
- Web interface

## Configuration Management

### Environment-Based Config
```python
# Development
DATABASE_URL=sqlite:///dev.db
AUTO_REPLY_ENABLED=false
LOG_LEVEL=DEBUG

# Production  
DATABASE_URL=postgresql://...
AUTO_REPLY_ENABLED=true
LOG_LEVEL=INFO
```

### Feature Flags
```python
# Gradual rollout
ENABLE_AUTO_REPLY=false
ENABLE_SLACK_NOTIFICATIONS=true
ENABLE_CALENDAR_INTEGRATION=true
```

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock external API calls
- Database operation testing
- Configuration validation

### Integration Tests
- End-to-end email processing
- API integration testing
- Database migration testing
- Error scenario testing

### Performance Tests
- Email processing throughput
- Memory usage monitoring
- API response time tracking
- Database query optimization

## Monitoring and Observability

### Logging
- Structured JSON logs
- Multiple log levels
- Performance metrics
- Error tracking

### Metrics
- Emails processed per hour
- Action success rates
- API response times
- Error frequencies

### Alerts
- Failed authentications
- API rate limit hits
- Database connection issues
- High error rates

This architecture provides a solid foundation for the AI Personal Email Assistant while allowing for future enhancements and scaling.