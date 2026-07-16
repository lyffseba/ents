"""
web/models.py - SQLAlchemy models for Ents Academy (users, progress, agent decisions, revenue).
Critical for persistence of AI agent actions + revenue evidence.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .deps import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    is_pro = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    progress = relationship("Progress", back_populates="user")

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phase = Column(String)
    pillars_completed = Column(String)  # JSON or comma list
    updated_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="progress")

class AgentDecision(Base):
    __tablename__ = "agent_decisions"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String)
    decision = Column(Text)
    gemini_prompt_summary = Column(Text)
    gemini_output = Column(Text)
    action_taken = Column(String)
    # For XPRIZE evidence: export these as "agent execution logs"

class RevenueEvent(Base):
    __tablename__ = "revenue_events"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow)
    amount_usd = Column(Float)
    month = Column(String)  # '2026-06'
    source = Column(String)  # 'stripe'
    is_related_party = Column(Boolean, default=False)
    user_email = Column(String)
    # Used by scripts/export_revenue.py for exact submission artifacts

class ChatLog(Base):
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role = Column(String)
    content = Column(Text)
    ts = Column(DateTime, default=datetime.utcnow)
