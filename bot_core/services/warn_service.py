"""
Warning management service
Platform-independent business logic for user warnings
"""

import logging
from typing import Optional, Tuple
from datetime import datetime

from ..database import get_session
from ..db_models import Warn, WarnSettings

logger = logging.getLogger(__name__)


def warn_user(chat_id: str, user_id: str, user_name: str, reason: Optional[str] = None) -> Tuple[int, int]:
    """
    Issue a warning to a user
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
        user_name: User display name
        reason: Warning reason
    
    Returns:
        Tuple of (current_warns, warn_limit)
    """
    session = get_session()
    try:
        # Add warning
        warn = Warn(
            chat_id=chat_id,
            user_id=user_id,
            user_name=user_name,
            reason=reason or "No reason provided",
            warned_at=datetime.now()
        )
        session.add(warn)
        session.commit()
        
        # Count warns
        count = session.query(Warn).filter_by(
            chat_id=chat_id,
            user_id=user_id
        ).count()
        
        # Get limit
        settings = session.query(WarnSettings).filter_by(chat_id=chat_id).first()
        limit = settings.warn_limit if settings else 3
        
        logger.info(f"⚠️ User {user_name} warned in {chat_id}: {count}/{limit}")
        return count, limit
    finally:
        session.close()


def add_warn(chat_id: str, user_id: str, user_name: str, reason: Optional[str] = None) -> bool:
    """Compatibility wrapper to add a warning and return success."""
    warn_user(chat_id, user_id, user_name, reason)
    return True


def get_user_warns(chat_id: str, user_id: str) -> Tuple[int, int]:
    """
    Get warning count for a user
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
    
    Returns:
        Tuple of (current_warns, warn_limit)
    """
    session = get_session()
    try:
        count = session.query(Warn).filter_by(
            chat_id=chat_id,
            user_id=user_id
        ).count()
        
        settings = session.query(WarnSettings).filter_by(chat_id=chat_id).first()
        limit = settings.warn_limit if settings else 3
        
        return count, limit
    finally:
        session.close()


def reset_user_warns(chat_id: str, user_id: str) -> int:
    """
    Reset warnings for a user
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
    
    Returns:
        Number of warnings cleared
    """
    session = get_session()
    try:
        count = session.query(Warn).filter_by(
            chat_id=chat_id,
            user_id=user_id
        ).delete()
        session.commit()
        
        logger.info(f"✅ Cleared {count} warns for user {user_id} in {chat_id}")
        return count
    finally:
        session.close()


def reset_warns(chat_id: str, user_id: str) -> bool:
    """Compatibility wrapper to reset warnings and return boolean."""
    return reset_user_warns(chat_id, user_id) > 0


def set_warn_limit(chat_id: str, limit: int) -> None:
    """
    Set warning limit for a chat
    
    Args:
        chat_id: Chat identifier
        limit: Warning limit
    """
    session = get_session()
    try:
        settings = session.query(WarnSettings).filter_by(chat_id=chat_id).first()
        if settings:
            settings.warn_limit = limit
        else:
            settings = WarnSettings(chat_id=chat_id, warn_limit=limit)
            session.add(settings)
        session.commit()
        
        logger.info(f"✅ Warn limit set to {limit} for {chat_id}")
    finally:
        session.close()


def get_warn_settings(chat_id: str) -> Tuple[int, bool]:
    """
    Get warning settings for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Tuple of (warn_limit, soft_warn)
    """
    session = get_session()
    try:
        settings = session.query(WarnSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            settings = WarnSettings(chat_id=chat_id)
            session.add(settings)
            session.commit()
        return settings.warn_limit, settings.soft_warn
    finally:
        session.close()


def get_warn_limit(chat_id: str) -> int:
    """
    Get warning limit for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Warning limit (default: 3)
    """
    session = get_session()
    try:
        settings = session.query(WarnSettings).filter_by(chat_id=chat_id).first()
        return settings.warn_limit if settings else 3
    finally:
        session.close()


def get_warns(chat_id: str, user_id: str):
    """
    Get all warnings for a user in a chat
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
    
    Returns:
        List of Warn objects
    """
    session = get_session()
    try:
        return session.query(Warn).filter_by(chat_id=chat_id, user_id=user_id).all()
    finally:
        session.close()
