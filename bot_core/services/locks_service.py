"""
Locks management service
Platform-independent business logic for content locks
"""

import logging
import re
from typing import Dict

from ..database import get_session
from ..db_models import Lock as Locks

logger = logging.getLogger(__name__)

# Supported lock types
LOCK_TYPES = ['links', 'stickers', 'media', 'all', 'url', 'sticker']

_LOCK_TYPE_ALIASES = {
    'url': 'links',
    'link': 'links',
    'sticker': 'stickers'
}


def set_lock(chat_id: str, lock_type: str, enabled: bool) -> bool:
    """
    Set a lock for a chat
    
    Args:
        chat_id: Chat identifier
        lock_type: Type of lock (links, stickers, media)
        enabled: Lock enabled state
    """
    lock_type = _LOCK_TYPE_ALIASES.get(lock_type, lock_type)
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
        else:
            return False
        
        session.commit()
        
        status = "enabled" if enabled else "disabled"
        logger.info(f"🔒 Lock '{lock_type}' {status} in {chat_id}")
        return True
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
                'all': False,
                'url': False,
                'sticker': False
            }

        return {
            'links': locks.lock_links,
            'stickers': locks.lock_stickers,
            'media': locks.lock_media,
            'all': locks.lock_all,
            'url': locks.lock_links,
            'sticker': locks.lock_stickers
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
    lock_type = _LOCK_TYPE_ALIASES.get(lock_type, lock_type)
    locks = get_locks(chat_id)
    return locks.get(lock_type, False) or locks.get('all', False)


def check_message_locks(chat_id: str, message_text: str = None, has_links: bool = False,
                       has_sticker: bool = False, has_stickers: bool = False, has_media: bool = False):
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
    sticker_present = has_sticker or has_stickers

    if isinstance(message_text, str):
        if not message_text.strip():
            message_text = None
        else:
            url_patterns = [
                r'https?://\S+',
                r'www\.\S+',
                r'\b\S+\.\S{2,}\b'
            ]
            if any(re.search(pattern, message_text, re.IGNORECASE) for pattern in url_patterns):
                has_links = True
    elif message_text is None:
        pass
    else:
        message_text = None
    
    if locks.get('all', False):
        logger.info(f"🔒 All content locked in {chat_id}")
        return True
    
    if has_links and locks.get('links', False):
        logger.info(f"🔒 Links locked in {chat_id}")
        return 'url'
    
    if sticker_present and locks.get('stickers', False):
        logger.info(f"🔒 Stickers locked in {chat_id}")
        return 'sticker'
    
    if has_media and locks.get('media', False):
        logger.info(f"🔒 Media locked in {chat_id}")
        return 'media'
    
    return False


def check_lock_violations(chat_id: str, message) -> bool:
    """Compatibility wrapper for lock checks against a message object."""
    text = getattr(message, 'text', None)
    has_media = any([
        getattr(message, 'photo', None),
        getattr(message, 'document', None),
        getattr(message, 'video', None),
        getattr(message, 'audio', None),
        getattr(message, 'sticker', None)
    ])
    has_sticker = bool(getattr(message, 'sticker', None))
    return check_message_locks(chat_id, text, has_sticker=has_sticker, has_media=has_media)


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
