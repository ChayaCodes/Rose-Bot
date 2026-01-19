"""
Ban management service
Platform-independent business logic for user bans
"""

import logging
from typing import List
from datetime import datetime

from ..database import get_session
from ..db_models import Ban

logger = logging.getLogger(__name__)


def add_ban(chat_id: str, user_id: str, user_name: str = None, banned_by: str = None, reason: str = None) -> None:
    """
    Ban a user from a chat
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
        user_name: User display name
        banned_by: Admin who issued the ban
        reason: Ban reason
    """
    session = get_session()
    try:
        # Check if already banned
        existing = session.query(Ban).filter_by(
            chat_id=chat_id,
            user_id=user_id
        ).first()
        
        if not existing:
            ban = Ban(
                chat_id=chat_id,
                user_id=user_id,
                user_name=user_name,
                reason=reason,
                banned_by=banned_by,
                banned_at=datetime.now()
            )
            session.add(ban)
            session.commit()
            logger.info(f"🚫 User {user_name} banned in {chat_id}")
    finally:
        session.close()


def remove_ban(chat_id: str, user_id: str) -> bool:
    """
    Remove a ban for a user
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
    
    Returns:
        True if user was banned and is now unbanned
    """
    session = get_session()
    try:
        count = session.query(Ban).filter_by(
            chat_id=chat_id,
            user_id=user_id
        ).delete()
        session.commit()
        
        if count > 0:
            logger.info(f"✅ User {user_id} unbanned in {chat_id}")
            return True
        return False
    finally:
        session.close()


def is_banned(chat_id: str, user_id: str) -> bool:
    """
    Check if a user is banned in a chat
    
    Args:
        chat_id: Chat identifier
        user_id: User identifier
    
    Returns:
        True if user is banned
    """
    session = get_session()
    try:
        ban = session.query(Ban).filter_by(
            chat_id=chat_id,
            user_id=user_id
        ).first()
        return ban is not None
    finally:
        session.close()


def get_banned_users(chat_id: str) -> List[Ban]:
    """
    Get all banned users in a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        List of Ban objects
    """
    session = get_session()
    try:
        return session.query(Ban).filter_by(chat_id=chat_id).all()
    finally:
        session.close()
