"""
Language management service
"""

from ..database import get_session
from ..db_models import ChatLanguage as Language


def get_chat_language(chat_id: str) -> str:
    """
    Get the language for a chat
    
    Args:
        chat_id: Chat identifier
    
    Returns:
        Language code (default: 'he')
    """
    session = get_session()
    try:
        lang = session.query(Language).filter_by(chat_id=chat_id).first()
        return lang.lang_code if lang else 'he'
    finally:
        session.close()


def set_chat_language(chat_id: str, lang_code: str) -> None:
    """
    Set the language for a chat
    
    Args:
        chat_id: Chat identifier
        lang_code: Language code (he, en, etc.)
    """
    session = get_session()
    try:
        lang = session.query(Language).filter_by(chat_id=chat_id).first()
        if lang:
            lang.lang_code = lang_code
        else:
            lang = Language(chat_id=chat_id, lang_code=lang_code)
            session.add(lang)
        session.commit()
    finally:
        session.close()


def get_translated_text(chat_id: str, key: str, **kwargs) -> str:
    """
    Get translated text for a chat
    
    Args:
        chat_id: Chat identifier
        key: Translation key
        **kwargs: Format parameters
    
    Returns:
        Translated and formatted text
    """
    from ..i18n import get_text
    lang = get_chat_language(chat_id)
    return get_text(lang, key, **kwargs)
