"""
Rules management service
Platform-independent business logic for group rules
"""

import logging
from typing import Optional

from ..database import get_session
from ..db_models import Rules

logger = logging.getLogger(__name__)


def get_rules(chat_id: str) -> Optional[str]:
    """
    Get rules for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Rules text or None
    """
    session = get_session()
    try:
        rules = session.query(Rules).filter_by(chat_id=chat_id).first()
        return rules.rules if rules else None
    finally:
        session.close()


def set_rules(chat_id: str, rules_text: str) -> None:
    """
    Set rules for a chat
    
    Args:
        chat_id: Chat identifier
        rules_text: Rules content
    """
    session = get_session()
    try:
        rules = session.query(Rules).filter_by(chat_id=chat_id).first()
        if rules:
            rules.rules = rules_text
        else:
            rules = Rules(chat_id=chat_id, rules=rules_text)
            session.add(rules)
        session.commit()
        
        logger.info(f"✅ Rules updated for {chat_id}")
    finally:
        session.close()


def clear_rules(chat_id: str) -> bool:
    """
    Clear rules for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        True if rules existed and were cleared
    """
    session = get_session()
    try:
        count = session.query(Rules).filter_by(chat_id=chat_id).delete()
        session.commit()
        
        if count > 0:
            logger.info(f"✅ Rules cleared for {chat_id}")
            return True
        return False
    finally:
        session.close()
