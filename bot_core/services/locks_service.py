"""
Locks management service
Platform-independent business logic for content locks
"""

import logging
from typing import Dict

from ..database import get_session
from ..db_models import Lock as Locks

logger = logging.getLogger(__name__)

# Supported lock types
LOCK_TYPES = ['links', 'stickers', 'media', 'all']


def set_lock(chat_id: str, lock_type: str, enabled: bool) -> None:
    """
    Set a lock for a chat
    
    Args:
        chat_id: Chat identifier
        lock_type: Type of lock (links, stickers, media)
        enabled: Lock enabled state
    """
    session = get_session()
    try:
        locks = session.query(Locks).filter_by(chat_id=chat_id).first()
        if not locks:
            locks = Locks(chat_id=chat_id)
            session.add(locks)
        
        if lock_type == 'links':
            locks.lock_links = enabled
        elif lock_type == 'stickers':
            locks.lock_stickers = enabled
        elif lock_type == 'media':
            locks.lock_media = enabled
        elif lock_type == 'all':
            locks.lock_all = enabled
        
        session.commit()
        
        status = "enabled" if enabled else "disabled"
        logger.info(f"🔒 Lock '{lock_type}' {status} in {chat_id}")
    finally:
        session.close()


def get_locks(chat_id: str) -> Dict[str, bool]:
    """
    Get all locks for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Dictionary of lock types and their states
    """
    session = get_session()
    try:
        locks = session.query(Locks).filter_by(chat_id=chat_id).first()
        if not locks:
            return {
                'links': False,
                'stickers': False,
                'media': False,
                'all': False
            }
        
        return {
            'links': locks.lock_links,
            'stickers': locks.lock_stickers,
            'media': locks.lock_media,
            'all': locks.lock_all
        }
    finally:
        session.close()


def is_locked(chat_id: str, lock_type: str) -> bool:
    """
    Check if a specific lock is enabled
    
    Args:
        chat_id: Chat identifier
        lock_type: Type of lock to check
    
    Returns:
        True if lock is enabled
    """
    locks = get_locks(chat_id)
    return locks.get(lock_type, False) or locks.get('all', False)


def check_message_locks(chat_id: str, has_links: bool = False, 
                       has_stickers: bool = False, has_media: bool = False) -> bool:
    """
    Check if a message violates any locks
    
    Args:
        chat_id: Chat identifier
        has_links: Message contains links
        has_stickers: Message contains stickers
        has_media: Message contains media
    
    Returns:
        True if message violates locks
    """
    locks = get_locks(chat_id)
    
    if locks.get('all', False):
        logger.info(f"🔒 All content locked in {chat_id}")
        return True
    
    if has_links and locks.get('links', False):
        logger.info(f"🔒 Links locked in {chat_id}")
        return True
    
    if has_stickers and locks.get('stickers', False):
        logger.info(f"🔒 Stickers locked in {chat_id}")
        return True
    
    if has_media and locks.get('media', False):
        logger.info(f"🔒 Media locked in {chat_id}")
        return True
    
    return False


def clear_locks(chat_id: str) -> bool:
    """
    Clear all locks for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        True if locks existed and were cleared
    """
    session = get_session()
    try:
        count = session.query(Locks).filter_by(chat_id=chat_id).delete()
        session.commit()
        
        if count > 0:
            logger.info(f"✅ Locks cleared for {chat_id}")
            return True
        return False
    finally:
        session.close()
