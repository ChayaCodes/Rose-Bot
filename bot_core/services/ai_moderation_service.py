"""
AI Moderation service
Platform-independent business logic for AI content moderation
"""

import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..database import get_session
from ..db_models import AIModeration as AIModerationSettings, AIModerationThreshold
from .ai_backends import (
    PerspectiveBackend,
    AzureBackend,
    OpenAIBackend,
    DetoxifyBackend
)

logger = logging.getLogger(__name__)

# Supported backends (removed 'rules' - use blacklist for word filtering)
SUPPORTED_BACKENDS = ['detoxify', 'perspective', 'openai', 'azure']

# Environment controls
AI_DEFAULT_BACKEND = os.getenv('AI_DEFAULT_BACKEND', 'openai').lower()
AI_FORCE_BACKEND = os.getenv('AI_FORCE_BACKEND', '').lower().strip()

def _resolve_backend(preferred: Optional[str]) -> str:
    if AI_FORCE_BACKEND in SUPPORTED_BACKENDS:
        return AI_FORCE_BACKEND
    if preferred in SUPPORTED_BACKENDS:
        return preferred
    if AI_DEFAULT_BACKEND in SUPPORTED_BACKENDS:
        return AI_DEFAULT_BACKEND
    return 'openai'

# Backend registry
_BACKEND_REGISTRY = {
    'detoxify': DetoxifyBackend,
    'perspective': PerspectiveBackend,
    'azure': AzureBackend,
    'openai': OpenAIBackend
}


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
            backend = _resolve_backend(None)
            api_key = None
            if backend == 'openai' and os.getenv('OPENAI_API_KEY'):
                api_key = os.getenv('OPENAI_API_KEY')
            return {
                'enabled': False,
                'backend': backend,
                'api_key': api_key,
                'threshold': 70,
                'thresholds': {},
                'action': 'delete'
            }
        threshold = settings.threshold
        if threshold is None:
            threshold = 70
        elif isinstance(threshold, float) and threshold <= 1:
            threshold = int(round(threshold * 100))
        elif isinstance(threshold, int) and threshold <= 1:
            threshold = int(round(threshold * 100))

        backend = _resolve_backend(settings.backend or None)
        api_key = settings.api_key
        if backend == 'openai' and os.getenv('OPENAI_API_KEY'):
            api_key = os.getenv('OPENAI_API_KEY')

        return {
            'enabled': settings.enabled,
            'backend': backend,
            'api_key': api_key,
            'threshold': threshold,
            'thresholds': get_ai_category_thresholds(chat_id),
            'action': settings.action
        }
    except Exception as e:
        # If database doesn't exist yet or any error, return defaults
        backend = _resolve_backend(None)
        api_key = None
        if backend == 'openai' and os.getenv('OPENAI_API_KEY'):
            api_key = os.getenv('OPENAI_API_KEY')
        return {
            'enabled': False,
            'backend': backend,
            'api_key': api_key,
            'threshold': 70,
            'thresholds': {},
            'action': 'delete'
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
                backend='detoxify',
                threshold=70,
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
                threshold=70,
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
                backend='detoxify',
                api_key=api_key,
                threshold=70,
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
        threshold: Detection threshold (0-100)
    """
    session = get_session()
    try:
        if isinstance(threshold, float) and threshold <= 1:
            threshold = int(round(threshold * 100))
        settings = session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            settings = AIModerationSettings(
                chat_id=chat_id,
                enabled=False,
                backend='detoxify',
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


def get_ai_category_thresholds(chat_id: str) -> Dict[str, float]:
    """Get per-category thresholds as 0-1 floats."""
    session = get_session()
    try:
        rows = session.query(AIModerationThreshold).filter_by(chat_id=chat_id).all()
        thresholds: Dict[str, float] = {}
        for row in rows:
            value = row.threshold
            if isinstance(value, float) and value <= 1:
                value = int(round(value * 100))
            thresholds[row.category] = float(value) / 100.0
        return thresholds
    except Exception:
        return {}
    finally:
        session.close()


def set_ai_category_thresholds(chat_id: str, categories: List[str], threshold: float) -> None:
    """Set per-category thresholds (0-100)."""
    session = get_session()
    try:
        if isinstance(threshold, float) and threshold <= 1:
            threshold = int(round(threshold * 100))
        threshold = int(threshold)
        for category in categories:
            row = session.query(AIModerationThreshold).filter_by(chat_id=chat_id, category=category).first()
            if not row:
                row = AIModerationThreshold(chat_id=chat_id, category=category, threshold=threshold)
                session.add(row)
            else:
                row.threshold = threshold
        session.commit()
        logger.info(f"🎯 AI category thresholds set to {threshold} for {chat_id}: {', '.join(categories)}")
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
                backend='detoxify',
                threshold=70,
                action=action
            )
            session.add(settings)
        else:
            settings.action = action
        
        session.commit()
        logger.info(f"⚡ AI action set to '{action}' for {chat_id}")
    finally:
        session.close()


def check_content_toxicity(text: str, backend: str = 'detoxify', 
                          api_key: Optional[str] = None, 
                          threshold: float = 0.7) -> Dict[str, Any]:
    """
    Check content for toxicity using AI backends
    
    Args:
        text: Text to check
        backend: AI backend (detoxify, perspective, openai, azure)
        api_key: API key if required by backend
        threshold: Detection threshold (0.0-1.0)
    
    Returns:
        Dictionary with is_toxic flag, score, and backend info
    """
    if not text or not text.strip():
        return {'is_toxic': False, 'score': 0.0, 'backend': backend}
    
    # Get backend class from registry
    backend_class = _BACKEND_REGISTRY.get(backend)
    
    if not backend_class:
        logger.warning(f"⚠️ Unknown backend '{backend}', falling back to detoxify")
        backend_class = DetoxifyBackend
    
    # Initialize backend
    try:
        backend_instance = backend_class(api_key=api_key)
        
        # Check if API key is required but not provided
        if backend_instance.requires_api_key and not api_key:
            logger.warning(f"⚠️ Backend '{backend}' requires API key, falling back to detoxify")
            backend_instance = DetoxifyBackend()
        
        # Perform check
        result = backend_instance.check_toxicity(text, threshold)
        return result
        
    except Exception as e:
        logger.error(f"❌ Error with backend '{backend}': {e}")
        # Fallback to detoxify (no API key needed)
        try:
            fallback = DetoxifyBackend()
            return fallback.check_toxicity(text, threshold)
        except Exception as fallback_error:
            logger.error(f"❌ Detoxify fallback also failed: {fallback_error}")
            # Return non-toxic if all fails
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': 'error',
                'error': f'All backends failed: {str(e)}'
            }
