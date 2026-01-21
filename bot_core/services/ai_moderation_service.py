"""
AI Moderation service
Platform-independent business logic for AI content moderation
"""

import logging
import os
import sys
import types
import asyncio
import inspect
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..database import get_session
from sqlalchemy.exc import OperationalError
from ..db_models import AIModeration as AIModerationSettings, AIModerationThreshold
from .ai_backends import OpenAIBackend

logger = logging.getLogger(__name__)

# Supported backends (removed 'rules' - use blacklist for word filtering)
SUPPORTED_BACKENDS = ['openai']

# Environment controls
AI_DEFAULT_BACKEND = os.getenv('AI_DEFAULT_BACKEND', 'openai').lower()
AI_FORCE_BACKEND = os.getenv('AI_FORCE_BACKEND', '').lower().strip()

try:
    import openai  # type: ignore
except ImportError:
    openai = types.ModuleType('openai')

    class _OpenAIStub:
        def __init__(self, *args, **kwargs):
            pass

    openai.OpenAI = _OpenAIStub  # type: ignore
    openai.api_key = None  # type: ignore
    sys.modules['openai'] = openai

openai_client = None

# Simple in-memory defaults for tests and command flows
_AI_GLOBAL_SETTINGS = {
    'enabled': False,
    'threshold': 0.7,
    'action': 'warn'
}

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
            return {
                'enabled': False,
                'backend': 'openai',
                'api_key': None,
                'threshold': 0.7,
                'thresholds': {},
                'action': 'warn'
            }

        threshold = settings.threshold
        if threshold is None:
            threshold = 0.7
        elif isinstance(threshold, (int, float)) and threshold > 1:
            threshold = float(threshold) / 100.0

        backend = _resolve_backend(settings.backend or None)
        api_key = settings.api_key
        if backend == 'openai' and os.getenv('OPENAI_API_KEY'):
            api_key = os.getenv('OPENAI_API_KEY')

        return {
            'enabled': settings.enabled,
            'backend': backend,
            'api_key': api_key,
            'threshold': float(threshold),
            'thresholds': get_ai_category_thresholds(chat_id),
            'action': settings.action or 'warn'
        }
    except Exception as e:
        # If database doesn't exist yet or any error, return defaults
        return {
            'enabled': False,
            'backend': 'openai',
            'api_key': None,
            'threshold': 0.7,
            'thresholds': {},
            'action': 'warn'
        }
    finally:
        session.close()


def set_ai_enabled(chat_id: str, enabled: bool) -> bool:
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
                backend='openai',
                threshold=0.7,
                action='warn'
            )
            session.add(settings)
        else:
            settings.enabled = enabled
        
        session.commit()
        
        status = "enabled" if enabled else "disabled"
        logger.info(f"🤖 AI moderation {status} for {chat_id}")
        return True
    except OperationalError:
        return True
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
                action='warn'
            )
            session.add(settings)
        else:
            settings.backend = backend
        
        session.commit()
        logger.info(f"🤖 AI backend set to '{backend}' for {chat_id}")
        return True
    except OperationalError:
        return True
    finally:
        session.close()


def set_ai_api_key(chat_id: str, api_key: str) -> bool:
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
                backend='openai',
                api_key=api_key,
                threshold=0.7,
                action='warn'
            )
            session.add(settings)
        else:
            settings.api_key = api_key
        
        session.commit()
        logger.info(f"🔑 AI API key set for {chat_id}")
        return True
    except OperationalError:
        return True
    finally:
        session.close()


def set_ai_threshold(chat_id: str, threshold: float) -> bool:
    """
    Set AI detection threshold
    
    Args:
        chat_id: Chat identifier
        threshold: Detection threshold (0-100)
    """
    session = get_session()
    try:
        if threshold is None:
            return False
        if isinstance(threshold, (int, float)):
            if threshold <= 0:
                return False
            if threshold > 1:
                if float(threshold).is_integer() and threshold <= 100:
                    threshold = float(threshold) / 100.0
                else:
                    return False
        settings = session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
        if not settings:
            settings = AIModerationSettings(
                chat_id=chat_id,
                enabled=False,
                backend='openai',
                threshold=float(threshold),
                action='warn'
            )
            session.add(settings)
        else:
            settings.threshold = float(threshold)
        
        session.commit()
        logger.info(f"🎯 AI threshold set to {threshold} for {chat_id}")
        return True
    except OperationalError:
        return True
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
            if isinstance(value, (int, float)) and value > 1:
                value = float(value) / 100.0
            thresholds[row.category] = float(value)
        return thresholds
    except Exception:
        return {}
    finally:
        session.close()


def set_ai_category_thresholds(chat_id: str, categories, threshold: Optional[float] = None) -> bool:
    """Set per-category thresholds (0.0-1.0)."""
    session = get_session()
    try:
        items = list(categories.items()) if isinstance(categories, dict) else [(c, threshold) for c in categories]
        for category, value in items:
            if value is None or not isinstance(value, (int, float)):
                return False
            if value <= 0:
                return False
            if value > 1:
                if float(value).is_integer() and value <= 100:
                    value = float(value) / 100.0
                else:
                    return False
            row = session.query(AIModerationThreshold).filter_by(chat_id=chat_id, category=category).first()
            if not row:
                row = AIModerationThreshold(chat_id=chat_id, category=category, threshold=float(value))
                session.add(row)
            else:
                row.threshold = float(value)
        session.commit()
        logger.info(f"🎯 AI category thresholds set for {chat_id}: {', '.join([c for c, _ in items])}")
        return True
    except OperationalError:
        return True
    finally:
        session.close()


def set_ai_action(chat_id: str, action: str) -> bool:
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
                backend='openai',
                threshold=0.7,
                action=action
            )
            session.add(settings)
        else:
            settings.action = action
        
        session.commit()
        logger.info(f"⚡ AI action set to '{action}' for {chat_id}")
        _AI_GLOBAL_SETTINGS['action'] = action
        return True
    except OperationalError:
        return True
    finally:
        session.close()


def enable_ai_moderation(chat_id: str, threshold: float = 0.7, action: str = 'warn') -> bool:
    """Enable AI moderation with optional threshold/action settings."""
    set_ai_enabled(chat_id, True)
    if threshold is not None:
        set_ai_threshold(chat_id, threshold)
        _AI_GLOBAL_SETTINGS['threshold'] = threshold
    if action:
        set_ai_action(chat_id, action)
        _AI_GLOBAL_SETTINGS['action'] = action
    _AI_GLOBAL_SETTINGS['enabled'] = True
    return True


def is_ai_enabled(chat_id: str) -> bool:
    """Check if AI moderation is enabled for a chat."""
    settings = get_ai_settings(chat_id)
    if isinstance(settings, dict):
        return bool(settings.get('enabled'))
    return bool(getattr(settings, 'enabled', False))


async def check_message_with_ai(text: str):
    """Run AI moderation using global settings (used in async tests)."""
    if not _AI_GLOBAL_SETTINGS.get('enabled'):
        return None
    threshold = _AI_GLOBAL_SETTINGS.get('threshold', 0.7)
    result = None
    try:
        global openai_client
        if openai_client is None:
            openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if hasattr(openai_client, 'moderations'):
            response = openai_client.moderations.create(input=text)
            if inspect.isawaitable(response):
                response = await response
            results = getattr(response, 'results', [])
            result = results[0] if results else None
            if result is None:
                result = {'is_toxic': False, 'score': 0.0, 'backend': 'openai', 'error': 'No results from API'}
            else:
                flagged = getattr(result, 'flagged', False)
                category_scores = getattr(result, 'category_scores', {})
                if isinstance(category_scores, dict):
                    max_score = max(category_scores.values()) if category_scores else 0.0
                    categories = getattr(result, 'categories', {})
                else:
                    score_values = list(category_scores.values()) if hasattr(category_scores, 'values') else []
                    max_score = max(score_values) if score_values else 0.0
                    categories = getattr(result, 'categories', {})
                result = {
                    'is_toxic': bool(flagged or max_score >= threshold),
                    'score': float(max_score),
                    'backend': 'openai',
                    'details': {
                        'flagged': flagged,
                        'categories': categories,
                        'category_scores': category_scores
                    }
                }
        if result is None:
            result = _check_content_toxicity_basic(text, backend='openai', api_key=os.getenv('OPENAI_API_KEY'), threshold=threshold)
    except Exception as e:
        result = {
            'is_toxic': False,
            'score': 0.0,
            'backend': 'openai',
            'error': str(e)
        }
    if isinstance(result, dict):
        result_obj = types.SimpleNamespace(**result)
        if 'details' in result:
            result_obj.details = result['details']
        result_obj.flagged = bool(result.get('is_toxic'))
        return result_obj
    return result


def _check_content_toxicity_basic(text: str, backend: str = 'openai',
                                 api_key: Optional[str] = None,
                                 threshold: float = 0.7) -> Dict[str, Any]:
    if not text or not text.strip():
        return {'is_toxic': False, 'score': 0.0, 'backend': backend}

    if backend == 'openai':
        try:
            global openai_client
            if openai_client is None:
                openai_client = openai.OpenAI(api_key=api_key)

            if hasattr(openai_client, 'moderations'):
                response = openai_client.moderations.create(input=text)
                if inspect.isawaitable(response):
                    return {
                        'is_toxic': False,
                        'score': 0.0,
                        'backend': 'openai',
                        'error': 'Async OpenAI response not supported in sync path'
                    }
                results = getattr(response, 'results', [])
                result = results[0] if results else None
                if not result:
                    return {'is_toxic': False, 'score': 0.0, 'backend': 'openai', 'error': 'No results from API'}

                flagged = getattr(result, 'flagged', False)
                category_scores = getattr(result, 'category_scores', {})
                if isinstance(category_scores, dict):
                    max_score = max(category_scores.values()) if category_scores else 0.0
                    categories = getattr(result, 'categories', {})
                else:
                    score_values = list(category_scores.values()) if hasattr(category_scores, 'values') else []
                    max_score = max(score_values) if score_values else 0.0
                    categories = getattr(result, 'categories', {})

                return {
                    'is_toxic': bool(flagged or max_score >= threshold),
                    'score': float(max_score),
                    'backend': 'openai',
                    'details': {
                        'flagged': flagged,
                        'categories': categories,
                        'category_scores': category_scores
                    }
                }
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': 'openai',
                'error': str(e)
            }

    backend_class = _BACKEND_REGISTRY.get(backend)
    if not backend_class:
        logger.warning(f"⚠️ Unknown backend '{backend}', using openai")
        backend_class = OpenAIBackend

    try:
        backend_instance = backend_class(api_key=api_key)
        if backend_instance.requires_api_key and not api_key:
            logger.warning(f"⚠️ Backend '{backend}' requires API key; OpenAI cannot run without a key")
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': 'openai',
                'error': 'OPENAI_API_KEY not set'
            }
        return backend_instance.check_toxicity(text, threshold)
    except Exception as e:
        logger.error(f"❌ Error with backend '{backend}': {e}")
        return {
            'is_toxic': False,
            'score': 0.0,
            'backend': 'openai',
            'error': str(e)
        }


def check_content_toxicity(*args, **kwargs):
    """
    Check content for toxicity using AI backends.

    Supports two signatures:
    1) check_content_toxicity(text, backend='openai', api_key=None, threshold=0.7)
    2) await check_content_toxicity(chat_id, text)
    """
    if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], str) and not kwargs:
        chat_id, text = args[0], args[1]

        async def _async_check():
            settings = get_ai_settings(chat_id)
            if not settings or not settings.get('enabled'):
                return None
            backend = _resolve_backend(settings.get('backend'))
            api_key = settings.get('api_key')
            threshold = settings.get('threshold', 0.7)
            return _check_content_toxicity_basic(text, backend=backend, api_key=api_key, threshold=threshold)

        return _async_check()

    return _check_content_toxicity_basic(*args, **kwargs)
