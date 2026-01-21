"""
Blacklist management service
Platform-independent business logic for word blacklisting
"""

import logging
from typing import List
import re

from ..database import get_session
from ..db_models import BlacklistWord as Blacklist

logger = logging.getLogger(__name__)


def add_blacklist_word(chat_id: str, word: str) -> bool:
    """
    Add a word to blacklist
    
    Args:
        chat_id: Chat identifier
        word: Word to blacklist
    """
    session = get_session()
    try:
        existing_words = session.query(Blacklist).filter_by(chat_id=chat_id).all()
        if any(w.word.lower() == word.lower() for w in existing_words):
            return True

        if word:
            blacklist = Blacklist(chat_id=chat_id, word=word)
            session.add(blacklist)
            session.commit()
            logger.info(f"✅ Added '{word}' to blacklist in {chat_id}")
        return True
    finally:
        session.close()


def remove_blacklist_word(chat_id: str, word: str) -> bool:
    """
    Remove a word from blacklist
    
    Args:
        chat_id: Chat identifier
        word: Word to remove
    
    Returns:
        True if word existed and was removed
    """
    session = get_session()
    try:
        words = session.query(Blacklist).filter_by(chat_id=chat_id).all()
        to_delete = [w for w in words if w.word.lower() == word.lower()]
        count = 0
        for entry in to_delete:
            session.delete(entry)
            count += 1
        session.commit()

        if count > 0:
            logger.info(f"✅ Removed '{word}' from blacklist in {chat_id}")
            return True
        return False
    finally:
        session.close()


def get_blacklist_words(chat_id: str) -> List[str]:
    """
    Get all blacklisted words for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        List of blacklisted words
    """
    session = get_session()
    try:
        words = session.query(Blacklist).filter_by(chat_id=chat_id).all()
        return [w.word for w in words]
    finally:
        session.close()


def check_blacklist(chat_id: str, text: str) -> str:
    """
    Check if text contains blacklisted words
    
    Args:
        chat_id: Chat identifier
        text: Text to check
    
    Returns:
        The blacklisted word found, or None
    """
    words = get_blacklist_words(chat_id)
    if not words:
        return None
    
    text_lower = text.lower()
    for word in words:
        if word in text_lower:
            logger.info(f"🚫 Blacklist triggered: '{word}' found in {chat_id}")
            return word
    
    return None


def clear_blacklist(chat_id: str) -> bool:
    """
    Clear all blacklisted words for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Number of words removed
    """
    session = get_session()
    try:
        count = session.query(Blacklist).filter_by(chat_id=chat_id).delete()
        session.commit()
        
        logger.info(f"✅ Cleared {count} blacklist words in {chat_id}")
        return count > 0
    finally:
        session.close()


def get_blacklist(chat_id: str) -> List[str]:
    """Compatibility alias for get_blacklist_words."""
    return get_blacklist_words(chat_id)


def get_blacklist_action(chat_id: str) -> str:
    """Return blacklist action (default: delete)."""
    return 'delete'
