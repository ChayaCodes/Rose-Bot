"""
Bot Core - Platform-independent business logic
Shared services for WhatsApp and Telegram bots
"""

from .database import init_db, get_session
from .db_models import (
    Base, Warn, WarnSettings, Ban, Rules, Welcome,
    BlacklistWord, Lock, ChatLanguage, AIModeration
)
from .i18n import TRANSLATIONS, LANG_NAMES, get_text

# Service imports
from .services.language_service import (
    get_chat_language,
    set_chat_language,
    get_translated_text
)

from .services.warn_service import (
    warn_user,
    get_user_warns,
    reset_user_warns,
    set_warn_limit,
    get_warn_limit
)

from .services.rules_service import (
    get_rules,
    set_rules,
    clear_rules
)

from .services.welcome_service import (
    get_welcome_message,
    set_welcome_message,
    clear_welcome_message,
    format_welcome_message
)

from .services.blacklist_service import (
    add_blacklist_word,
    remove_blacklist_word,
    get_blacklist_words,
    check_blacklist,
    clear_blacklist
)

from .services.locks_service import (
    set_lock,
    get_locks,
    is_locked,
    check_message_locks,
    clear_locks,
    LOCK_TYPES
)

from .services.ai_moderation_service import (
    get_ai_settings,
    set_ai_enabled,
    set_ai_backend,
    set_ai_api_key,
    set_ai_threshold,
    set_ai_action,
    check_content_toxicity,
    SUPPORTED_BACKENDS
)

from .services.flood_service import (
    check_flood,
    clear_old_flood_records,
    reset_user_flood
)

__all__ = [
    # Database
    'init_db',
    'get_session',
    
    # Models
    'Warn',
    'WarnSettings',
    'Rules',
    'Welcome',
    'Blacklist',
    'Locks',
    'FloodControl',
    'AIModerationSettings',
    'Language',
    
    # i18n
    'TRANSLATIONS',
    'LANG_NAMES',
    'get_text',
    'get_chat_language',
    'set_chat_language',
    'get_translated_text',
    
    # Warn service
    'warn_user',
    'get_user_warns',
    'reset_user_warns',
    'set_warn_limit',
    'get_warn_limit',
    
    # Rules service
    'get_rules',
    'set_rules',
    'clear_rules',
    
    # Welcome service
    'get_welcome_message',
    'set_welcome_message',
    'clear_welcome_message',
    'format_welcome_message',
    
    # Blacklist service
    'add_blacklist_word',
    'remove_blacklist_word',
    'get_blacklist_words',
    'check_blacklist',
    'clear_blacklist',
    
    # Locks service
    'set_lock',
    'get_locks',
    'is_locked',
    'check_message_locks',
    'clear_locks',
    'LOCK_TYPES',
    
    # AI moderation service
    'get_ai_settings',
    'set_ai_enabled',
    'set_ai_backend',
    'set_ai_api_key',
    'set_ai_threshold',
    'set_ai_action',
    'check_content_toxicity',
    'SUPPORTED_BACKENDS',
    
    # Flood service
    'check_flood',
    'clear_old_flood_records',
    'reset_user_flood',
]
