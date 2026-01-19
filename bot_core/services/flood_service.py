"""
Flood control service
Platform-independent business logic for anti-flood protection
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

from ..database import get_session
from ..db_models import FloodControl

logger = logging.getLogger(__name__)


def check_flood(chat_id: str, user_id: str, max_messages: int = 5, 
                time_window: int = 10) -> bool:
    """
    Check if user is flooding
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
        max_messages: Maximum messages allowed
        time_window: Time window in seconds
    
    Returns:
        True if user is flooding
    """
    session = get_session()
    try:
        now = datetime.now()
        cutoff = now - timedelta(seconds=time_window)
        
        # Get recent messages
        recent_count = session.query(FloodControl).filter(
            FloodControl.chat_id == chat_id,
            FloodControl.user_id == user_id,
            FloodControl.timestamp > cutoff
        ).count()
        
        # Add current message
        flood = FloodControl(
            chat_id=chat_id,
            user_id=user_id,
            timestamp=now
        )
        session.add(flood)
        session.commit()
        
        if recent_count >= max_messages:
            logger.warning(f"🌊 Flood detected: {user_id} in {chat_id} ({recent_count} msgs)")
            return True
        
        return False
    finally:
        session.close()


def clear_old_flood_records(days: int = 7) -> int:
    """
    Clear old flood control records
    
    Args:
        days: Number of days to keep
    
    Returns:
        Number of records deleted
    """
    session = get_session()
    try:
        cutoff = datetime.now() - timedelta(days=days)
        count = session.query(FloodControl).filter(
            FloodControl.timestamp < cutoff
        ).delete()
        session.commit()
        
        logger.info(f"🧹 Cleared {count} old flood records")
        return count
    finally:
        session.close()


def reset_user_flood(chat_id: str, user_id: str) -> int:
    """
    Reset flood records for a user
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
    
    Returns:
        Number of records deleted
    """
    session = get_session()
    try:
        count = session.query(FloodControl).filter_by(
            chat_id=chat_id,
            user_id=user_id
        ).delete()
        session.commit()
        
        logger.info(f"✅ Reset flood records for {user_id} in {chat_id}")
        return count
    finally:
        session.close()
