"""
Bot Services - Platform-independent business logic
"""

from .language_service import (
    get_chat_language,
    set_chat_language,
    get_translated_text
)

from .warn_service import (
    warn_user,
    get_user_warns,
    reset_user_warns,
    set_warn_limit,
    get_warn_limit
)

from .rules_service import (
    get_rules,
    set_rules,
    clear_rules
)

from .welcome_service import (
    get_welcome_message,
    set_welcome_message,
    clear_welcome_message,
    format_welcome_message
)

from .blacklist_service import (
    add_blacklist_word,
    remove_blacklist_word,
    get_blacklist_words,
    check_blacklist,
    clear_blacklist
)

from .locks_service import (
    set_lock,
    get_locks,
    is_locked,
    check_message_locks,
    clear_locks,
    LOCK_TYPES
)

from .ai_moderation_service import (
    get_ai_settings,
    set_ai_enabled,
    set_ai_backend,
    set_ai_api_key,
    set_ai_threshold,
    set_ai_action,
    check_content_toxicity,
    SUPPORTED_BACKENDS
)

from .flood_service import (
    check_flood,
    clear_old_flood_records,
    reset_user_flood
)

__all__ = [
    # Language service
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
