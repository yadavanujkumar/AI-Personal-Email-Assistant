"""
Database models for storing email data and conversation history.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()


class Email(Base):
    """Email model for storing email data."""
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, index=True)
    thread_id = Column(String(255), index=True)
    sender = Column(String(255), index=True)
    recipient = Column(Text)  # Can contain multiple recipients
    subject = Column(Text)
    body = Column(Text)
    html_body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    received_date = Column(DateTime)
    
    # Email metadata
    has_attachments = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    is_forwarded = Column(Boolean, default=False)
    
    # AI analysis results
    intent = Column(String(100))  # meeting, question, request, etc.
    priority = Column(String(20))  # high, medium, low
    requires_action = Column(Boolean, default=False)
    ai_summary = Column(Text)
    
    # Relationships
    replies = relationship("EmailReply", back_populates="original_email")
    actions = relationship("EmailAction", back_populates="email")
    
    def __repr__(self):
        return f"<Email(id={self.id}, subject='{self.subject[:50]}...')>"


class EmailReply(Base):
    """Model for storing AI-generated replies."""
    __tablename__ = "email_replies"
    
    id = Column(Integer, primary_key=True, index=True)
    original_email_id = Column(Integer, ForeignKey("emails.id"))
    reply_content = Column(Text)
    reply_type = Column(String(50))  # auto, draft, sent
    confidence_score = Column(String(10))  # AI confidence in the reply
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    original_email = relationship("Email", back_populates="replies")
    
    def __repr__(self):
        return f"<EmailReply(id={self.id}, type='{self.reply_type}')>"


class EmailAction(Base):
    """Model for tracking actions taken on emails."""
    __tablename__ = "email_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    action_type = Column(String(50))  # slack_notify, calendar_create, web_search
    action_data = Column(JSON)  # Store action-specific data
    status = Column(String(20))  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    email = relationship("Email", back_populates="actions")
    
    def __repr__(self):
        return f"<EmailAction(id={self.id}, type='{self.action_type}')>"


class ConversationThread(Base):
    """Model for tracking conversation threads."""
    __tablename__ = "conversation_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), unique=True, index=True)
    subject = Column(Text)
    participants = Column(Text)  # JSON string of email addresses
    first_message_date = Column(DateTime)
    last_message_date = Column(DateTime)
    message_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<ConversationThread(id={self.id}, subject='{self.subject[:50]}...')>"


def create_database(database_url: str):
    """Create database and tables."""
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine


def get_session_maker(database_url: str):
    """Get SQLAlchemy session maker."""
    engine = create_database(database_url)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)