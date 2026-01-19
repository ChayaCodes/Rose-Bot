"""
AI Moderation service
Platform-independent business logic for AI content moderation
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..database import get_session
from ..db_models import AIModeration as AIModerationSettings

logger = logging.getLogger(__name__)

# Supported backends
SUPPORTED_BACKENDS = ['rules', 'perspective', 'azure', 'openai', 'detoxify']


def get_ai_settings(chat_id: str) -> Dict[str, Any]:
    """
    Get AI moderation settings for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Dictionary with AI settings
    """
    session = get_session()
    try:
        settings = session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            return {
                'enabled': False,
                'backend': 'rules',
                'api_key': None,
                'threshold': 0.7,
                'action': 'delete'
            }
        
        return {
            'enabled': settings.enabled,
            'backend': settings.backend or 'rules',
            'api_key': settings.api_key,
            'threshold': settings.threshold,
            'action': settings.action
        }
    finally:
        session.close()


def set_ai_enabled(chat_id: str, enabled: bool) -> None:
    """
    Enable or disable AI moderation
    
    Args:
        chat_id: Chat identifier
        enabled: Enable state
    """
    session = get_session()
    try:
        settings = session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            settings = AIModerationSettings(
                chat_id=chat_id,
                enabled=enabled,
                backend='rules',
                threshold=0.7,
                action='delete'
            )
            session.add(settings)
        else:
            settings.enabled = enabled
        
        session.commit()
        
        status = "enabled" if enabled else "disabled"
        logger.info(f"🤖 AI moderation {status} for {chat_id}")
    finally:
        session.close()


def set_ai_backend(chat_id: str, backend: str) -> bool:
    """
    Set AI moderation backend
    
    Args:
        chat_id: Chat identifier
        backend: Backend name
    
    Returns:
        True if backend is valid and was set
    """
    if backend not in SUPPORTED_BACKENDS:
        return False
    
    session = get_session()
    try:
        settings = session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            settings = AIModerationSettings(
                chat_id=chat_id,
                enabled=False,
                backend=backend,
                threshold=0.7,
                action='delete'
            )
            session.add(settings)
        else:
            settings.backend = backend
        
        session.commit()
        logger.info(f"🤖 AI backend set to '{backend}' for {chat_id}")
        return True
    finally:
        session.close()


def set_ai_api_key(chat_id: str, api_key: str) -> None:
    """
    Set API key for AI backend
    
    Args:
        chat_id: Chat identifier
        api_key: API key
    """
    session = get_session()
    try:
        settings = session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            settings = AIModerationSettings(
                chat_id=chat_id,
                enabled=False,
                backend='rules',
                api_key=api_key,
                threshold=0.7,
                action='delete'
            )
            session.add(settings)
        else:
            settings.api_key = api_key
        
        session.commit()
        logger.info(f"🔑 AI API key set for {chat_id}")
    finally:
        session.close()


def set_ai_threshold(chat_id: str, threshold: float) -> None:
    """
    Set AI detection threshold
    
    Args:
        chat_id: Chat identifier
        threshold: Detection threshold (0.0-1.0)
    """
    session = get_session()
    try:
        settings = session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            settings = AIModerationSettings(
                chat_id=chat_id,
                enabled=False,
                backend='rules',
                threshold=threshold,
                action='delete'
            )
            session.add(settings)
        else:
            settings.threshold = threshold
        
        session.commit()
        logger.info(f"🎯 AI threshold set to {threshold} for {chat_id}")
    finally:
        session.close()


def set_ai_action(chat_id: str, action: str) -> None:
    """
    Set action for detected content
    
    Args:
        chat_id: Chat identifier
        action: Action type (delete, warn, kick, ban)
    """
    session = get_session()
    try:
        settings = session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            settings = AIModerationSettings(
                chat_id=chat_id,
                enabled=False,
                backend='rules',
                threshold=0.7,
                action=action
            )
            session.add(settings)
        else:
            settings.action = action
        
        session.commit()
        logger.info(f"⚡ AI action set to '{action}' for {chat_id}")
    finally:
        session.close()


def check_content_toxicity(text: str, backend: str = 'rules', 
                          api_key: Optional[str] = None, 
                          threshold: float = 0.7) -> Dict[str, Any]:
    """
    Check content for toxicity using specified backend
    
    Args:
        text: Text to check
        backend: AI backend to use
        api_key: API key if required
        threshold: Detection threshold
    
    Returns:
        Dictionary with is_toxic flag and score
    """
    # Rule-based detection (no API needed)
    if backend == 'rules':
        toxic_patterns = [
            # Hebrew toxic patterns
            r'\b(דפוק|מניאק|זין|כוס|חרא|לעזאזל)\b',
            # English toxic patterns
            r'\b(fuck|shit|damn|bitch|asshole|idiot|stupid)\b',
            # Spam patterns
            r'(http|https|www\.)\S+',
            r'(\d{10,})',  # Long numbers (phone/spam)
        ]
        
        import re
        text_lower = text.lower()
        
        for pattern in toxic_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"🚫 Toxic content detected (rules): {pattern}")
                return {
                    'is_toxic': True,
                    'score': 0.9,
                    'backend': 'rules'
                }
        
        return {
            'is_toxic': False,
            'score': 0.0,
            'backend': 'rules'
        }
    
    # Other backends would be implemented here
    # perspective, azure, openai, detoxify
    logger.warning(f"⚠️ Backend '{backend}' not fully implemented yet")
    
    return {
        'is_toxic': False,
        'score': 0.0,
        'backend': backend,
        'error': 'Backend not implemented'
    }
