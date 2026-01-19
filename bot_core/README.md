# Bot Core - Project Structure

## 📁 Directory Structure

```
bot_core/
├── __init__.py                    # ייצוא מרכזי של כל המודולים
├── database.py                    # ניהול מסד נתונים (SQLAlchemy)
├── i18n.py                        # מערכת תרגום (עברית/אנגלית)
├── models.py                      # מודלי SQLAlchemy (DB tables)
├── content_filter.py              # סינון תוכן (AI moderation)
├── whatsapp_bridge_client.py      # WhatsApp Bridge API client
│
├── adapters/                      # מתאמים לפלטפורמות שונות
│   ├── __init__.py
│   ├── base_adapter.py           # ממשק בסיסי
│   ├── whatsapp_adapter.py       # מתאם WhatsApp
│   └── telegram_adapter.py       # מתאם Telegram
│
├── models/                        # מודלים מופשטים (לאדפטרים)
│   ├── __init__.py
│   ├── message.py                # BotMessage
│   ├── user.py                   # BotUser
│   └── chat.py                   # BotChat
│
└── services/                      # לוגיקה עסקית (platform-agnostic)
    ├── __init__.py
    ├── language_service.py       # ניהול שפות
    ├── warn_service.py           # אזהרות
    ├── rules_service.py          # חוקים
    ├── welcome_service.py        # הודעות קבלת פנים
    ├── blacklist_service.py      # רשימה שחורה
    ├── locks_service.py          # נעילות
    ├── ai_moderation_service.py  # AI moderation
    └── flood_service.py          # בקרת ספאם
```

## 🎯 Architecture

### Layers

1. **Database Layer** (`database.py`, `models.py`)
   - SQLAlchemy models
   - Session management
   - Tables: Warn, Rules, Welcome, Blacklist, Locks, AI Settings, Language

2. **Service Layer** (`services/`)
   - Pure business logic
   - **Platform-independent**
   - Reusable in both WhatsApp and Telegram

3. **Adapter Layer** (`adapters/`)
   - Adapts between platforms to unified model
   - BotMessage, BotUser, BotChat - common interfaces
   - Each platform implements base_adapter

4. **i18n Layer** (`i18n.py`)
   - Translations (Hebrew/English)
   - `get_text(lang, key, **kwargs)`
   - Format support and dynamic replacement

## 📦 Usage

### Importing Services

```python
from bot_core import (
    # Database
    init_db, get_session,
    
    # i18n
    get_chat_language, set_chat_language, get_translated_text,
    
    # Services
    warn_user, get_rules, set_welcome_message,
    check_blacklist, set_lock, get_ai_settings
)
```

### Initialization

```python
from bot_core import init_db

# Initialize database
init_db()
```

### Using Services

```python
from bot_core.services import warn_service, rules_service

# Warn user
count, limit = warn_service.warn_user(
    chat_id="123",
    user_id="456",
    user_name="John",
    reason="Spam"
)

# Set rules
rules_service.set_rules(chat_id="123", rules_text="No spam!")
```

## 🌍 Internationalization

```python
from bot_core.services.language_service import get_translated_text

# Get translated text
text = get_translated_text(
    chat_id="123",
    key="warn_issued",
    user="John",
    reason="Spam",
    count=1,
    limit=3
)
```

## 🔧 Extension

### Adding a New Service

1. Create new file in `services/`: `my_service.py`
2. Define functions with business logic
3. Add to `services/__init__.py`
4. Use it from any platform

### Adding a New Platform

1. Create new adapter: `adapters/my_platform_adapter.py`
2. Extend `base_adapter.py`
3. Convert messages to `BotMessage`, `BotUser`, `BotChat` format
4. Use existing services

## ✅ Principles

- ✨ **Platform-agnostic** - Business logic without platform dependencies
- 🔄 **Reusable** - Shared code for all bots
- 📝 **Type-safe** - Full typing with type hints
- 🧩 **Modular** - Clear separation between layers
- 🌍 **i18n ready** - Full internationalization support
