"""
Database Models - Platform Independent
All database models used by the bot
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Warn(Base):
    """User warnings"""
    __tablename__ = 'warns'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    chat_id = Column(String(100), nullable=False)
    reason = Column(Text)
    warned_by = Column(String(100))
    date = Column(DateTime, default=datetime.utcnow)


class WarnSettings(Base):
    """Warning configuration per chat"""
    __tablename__ = 'warn_settings'
    chat_id = Column(String(100), primary_key=True)
    warn_limit = Column(Integer, default=3)
    soft_warn = Column(Boolean, default=False)  # True=kick, False=ban


class Ban(Base):
    """Banned users"""
    __tablename__ = 'bans'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    chat_id = Column(String(100), nullable=False)
    reason = Column(Text)
    banned_by = Column(String(100))
    date = Column(DateTime, default=datetime.utcnow)


class Rules(Base):
    """Chat rules"""
    __tablename__ = 'rules'
    chat_id = Column(String(100), primary_key=True)
    rules = Column(Text)


class Welcome(Base):
    """Welcome messages"""
    __tablename__ = 'welcome'
    chat_id = Column(String(100), primary_key=True)
    message = Column(Text)
    enabled = Column(Boolean, default=True)


class BlacklistWord(Base):
    """Blacklisted words per chat"""
    __tablename__ = 'blacklist'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(100), nullable=False)
    word = Column(String(255), nullable=False)


class Lock(Base):
    """Content locks per chat"""
    __tablename__ = 'locks'
    chat_id = Column(String(100), primary_key=True)
    lock_links = Column(Boolean, default=False)
    lock_stickers = Column(Boolean, default=False)
    lock_media = Column(Boolean, default=False)


class FloodControl(Base):
    """Anti-flood settings"""
    __tablename__ = 'flood_control'
    chat_id = Column(String(100), primary_key=True)
    limit = Column(Integer, default=5)  # messages
    timeframe = Column(Integer, default=10)  # seconds


class AIModeration(Base):
    """AI moderation configuration"""
    __tablename__ = 'ai_moderation'
    chat_id = Column(String(100), primary_key=True)
    enabled = Column(Boolean, default=False)
    backend = Column(String(20), default='rules')  # perspective, azure, openai, detoxify, rules
    api_key = Column(String(255), nullable=True)  # Group's own API key
    toxicity_threshold = Column(Integer, default=70)  # 0-100
    spam_threshold = Column(Integer, default=70)
    sexual_threshold = Column(Integer, default=70)
    threat_threshold = Column(Integer, default=60)
    auto_delete = Column(Boolean, default=True)
    auto_warn = Column(Boolean, default=False)


class ChatLanguage(Base):
    """Language preference per chat"""
    __tablename__ = 'language'
    chat_id = Column(String(100), primary_key=True)
    lang_code = Column(String(10), default='he')  # he, en, etc.
