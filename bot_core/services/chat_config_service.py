"""
Chat configuration service
Platform-independent business logic for chat settings
"""

import logging
from typing import Optional

from ..database import get_session
from ..db_models import ChatConfig

logger = logging.getLogger(__name__)


def should_delete_commands(chat_id: str) -> bool:
    """
    Check if commands should be auto-deleted in this chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        True if commands should be deleted
    """
    session = get_session()
    try:
        config = session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        return config.delete_commands if config else False
    finally:
        session.close()


def set_delete_commands(chat_id: str, enabled: bool) -> None:
    """
    Set whether to auto-delete command messages
    
    Args:
        chat_id: Chat identifier
        enabled: Whether to enable command deletion
    """
    session = get_session()
    try:
        config = session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        if config:
            config.delete_commands = enabled
        else:
            config = ChatConfig(chat_id=chat_id, delete_commands=enabled)
            session.add(config)
        session.commit()
        
        status = "enabled" if enabled else "disabled"
        logger.info(f"🗑️ Command deletion {status} in {chat_id}")
    finally:
        session.close()
