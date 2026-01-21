"""
Welcome message service
Platform-independent business logic for welcome messages
"""

import logging
from typing import Optional

from ..database import get_session
from ..db_models import Welcome

logger = logging.getLogger(__name__)


def get_welcome_message(chat_id: str) -> Optional[str]:
    """
    Get welcome message for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Welcome message or None
    """
    session = get_session()
    try:
        welcome = session.query(Welcome).filter_by(chat_id=chat_id).first()
        return welcome.message if welcome and welcome.enabled else None
    finally:
        session.close()


def set_welcome_message(chat_id: str, message: str) -> bool:
    """
    Set welcome message for a chat
    
    Args:
        chat_id: Chat identifier
        message: Welcome message content
    """
    session = get_session()
    try:
        welcome = session.query(Welcome).filter_by(chat_id=chat_id).first()
        if welcome:
            welcome.message = message
        else:
            welcome = Welcome(chat_id=chat_id, message=message)
            session.add(welcome)
        session.commit()
        
        logger.info(f"✅ Welcome message updated for {chat_id}")
        return True
    finally:
        session.close()


def clear_welcome_message(chat_id: str) -> bool:
    """
    Clear welcome message for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        True if welcome existed and was cleared
    """
    session = get_session()
    try:
        count = session.query(Welcome).filter_by(chat_id=chat_id).delete()
        session.commit()
        
        if count > 0:
            logger.info(f"✅ Welcome message cleared for {chat_id}")
            return True
        return False
    finally:
        session.close()


def format_welcome_message(message: str, user_name: str, mention: Optional[str] = None, chat_name: Optional[str] = None, user_id: Optional[str] = None) -> str:
    """
    Format welcome message with user placeholders
    
    Args:
        message: Welcome message template
        user_name: User display name
        mention: Platform-specific mention string
    
    Returns:
        Formatted message
    """
    mention_value = mention or user_name
    formatted = message.replace('{mention}', mention_value).replace('{user}', user_name).replace('{name}', user_name)
    if chat_name:
        formatted = formatted.replace('{chat}', chat_name).replace('{group}', chat_name)
    if user_id:
        formatted = formatted.replace('{id}', user_id)
    return formatted


def get_welcome(chat_id: str) -> Optional[str]:
    """Compatibility alias."""
    return get_welcome_message(chat_id)


def set_welcome(chat_id: str, message: str) -> bool:
    """Compatibility alias."""
    return set_welcome_message(chat_id, message)
