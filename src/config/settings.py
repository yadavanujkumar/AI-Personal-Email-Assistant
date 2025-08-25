"""
Configuration management for the AI Personal Email Assistant.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Gmail API Configuration
    gmail_credentials_file: str = Field(
        "credentials/gmail_credentials.json", 
        env="GMAIL_CREDENTIALS_FILE"
    )
    gmail_token_file: str = Field(
        "credentials/gmail_token.json", 
        env="GMAIL_TOKEN_FILE"
    )
    
    # Google Search API Configuration
    google_search_api_key: Optional[str] = Field(None, env="GOOGLE_SEARCH_API_KEY")
    google_search_engine_id: Optional[str] = Field(None, env="GOOGLE_SEARCH_ENGINE_ID")
    
    # Slack Configuration
    slack_bot_token: Optional[str] = Field(None, env="SLACK_BOT_TOKEN")
    slack_channel: str = Field("#general", env="SLACK_CHANNEL")
    
    # Google Calendar Configuration
    calendar_credentials_file: str = Field(
        "credentials/calendar_credentials.json",
        env="CALENDAR_CREDENTIALS_FILE"
    )
    calendar_token_file: str = Field(
        "credentials/calendar_token.json",
        env="CALENDAR_TOKEN_FILE"
    )
    
    # Database Configuration
    database_url: str = Field("sqlite:///email_assistant.db", env="DATABASE_URL")
    
    # Application Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    auto_reply_enabled: bool = Field(False, env="AUTO_REPLY_ENABLED")
    max_emails_fetch: int = Field(50, env="MAX_EMAILS_FETCH")
    email_check_interval: int = Field(300, env="EMAIL_CHECK_INTERVAL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()