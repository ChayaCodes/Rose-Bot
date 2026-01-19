# 📂 Project Structure

## Overview

Rose Bot is a modular bot project supporting WhatsApp and Telegram with a shared architecture.

## 🗂️ Directory Structure

```
Rose-Bot/
│
├── 🤖 Bots (Platform-specific)
│   ├── whatsapp_bot.py              # WhatsApp bot (main entry point)
│   ├── whatsapp_bridge.js           # Node.js WhatsApp bridge
│   ├── wa_config.py                 # WhatsApp configuration
│   └── tg_bot/                      # Telegram bot
│       ├── __main__.py              # Telegram entry point
│       ├── sample_config.py         # Configuration template
│       └── modules/                 # Telegram modules
│           ├── admin.py
│           ├── warns.py
│           ├── rules.py
│           └── ... (more modules)
│
├── 🧠 Core Logic (Platform-agnostic)
│   └── bot_core/
│       ├── __init__.py              # Central exports
│       ├── database.py              # Database management
│       ├── i18n.py                  # Translation system
│       ├── models.py                # SQLAlchemy models (DB)
│       ├── content_filter.py        # AI content moderation
│       ├── whatsapp_bridge_client.py # WhatsApp API client
│       │
│       ├── adapters/                # Platform adapters
│       │   ├── base_adapter.py      # Base interface
│       │   ├── whatsapp_adapter.py  # WhatsApp adapter
│       │   └── telegram_adapter.py  # Telegram adapter
│       │
│       ├── models/                  # Abstract models
│       │   ├── message.py           # BotMessage
│       │   ├── user.py              # BotUser
│       │   └── chat.py              # BotChat
│       │
│       └── services/                # Business logic (reusable)
│           ├── language_service.py  # Language management
│           ├── warn_service.py      # Warnings
│           ├── rules_service.py     # Rules
│           ├── welcome_service.py   # Welcome messages
│           ├── blacklist_service.py # Blacklist
│           ├── locks_service.py     # Locks
│           ├── ai_moderation_service.py # AI moderation
│           └── flood_service.py     # Flood control
│
├── 🧪 Tests
│   └── tests/
│       └── test_bot_core.py         # Core tests
│
├── 📝 Documentation
│   ├── README.md                    # Overview
│   ├── QUICKSTART.md                # Quick start guide
│   ├── SETUP.md                     # Setup instructions
│   ├── USER_GUIDE.md                # User manual
│   ├── AI_MODERATION_SETUP.md       # AI setup guide
│   ├── FEATURE_COMPARISON.md        # Feature comparison
│   ├── DEPLOYMENT_CHECKLIST.md      # Deploy checklist
│   └── CONTRIBUTING.md              # Contribution guide
│
├── ⚙️ Configuration
│   ├── requirements.txt             # Python dependencies
│   ├── package.json                 # Node.js dependencies
│   ├── runtime.txt                  # Python version
│   ├── Procfile                     # Heroku config
│   ├── app.json                     # Heroku app config
│   └── .gitignore                   # Git ignore rules
│
└── 🗄️ Runtime Generated Files
    ├── bot.db                       # SQLite database
    ├── .wwebjs_auth/                # WhatsApp session
    └── .wwebjs_cache/               # WhatsApp cache
```

## 🎯 Architecture Principles

### 1. Separation of Concerns

```
Platform Code    →    Adapters    →    Services    →    Database
(WhatsApp/TG)         (Convert)       (Business)       (Storage)
```

### 2. Code Reuse

- **Services**: לוגיקה עסקית משותפת לכל הפלטפורמות
- **Models**: מודלי DB אחידים
- **i18n**: מערכת תרגום משותפת

### 3. Platform Independence

- Services לא יודעים על WhatsApp או Telegram
- Adapters מתרגמים הודעות לפורמט אחיד
- כל פלטפורמה יכולה להשתמש באותם services

## 🔄 Data Flow

### WhatsApp Flow

```
User (WhatsApp)
    ↓
whatsapp_bridge.js (Node.js)
    ↓ (HTTP POST)
whatsapp_bot.py
    ↓
WhatsAppAdapter (converts to BotMessage)
    ↓
Services (business logic)
    ↓
Database (SQLAlchemy)
```

### Telegram Flow

```
User (Telegram)
    ↓
python-telegram-bot (Library)
    ↓
tg_bot/modules/*.py
    ↓
TelegramAdapter (converts to BotMessage)
    ↓
Services (business logic)
    ↓
Database (SQLAlchemy)
```

## 📦 Dependencies

### Python (requirements.txt)
- **SQLAlchemy 2.x** - ORM
- **Flask** - WhatsApp webhook
- **requests** - HTTP client

### Node.js (package.json)
- **whatsapp-web.js** - WhatsApp client
- **qrcode-terminal** - QR code display

## 🚀 Running

### WhatsApp Bot

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run bridge
node whatsapp_bridge.js

# Run bot (another window)
python whatsapp_bot.py
```

### Telegram Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp tg_bot/sample_config.py tg_bot/config.py

# Run bot
python -m tg_bot
```

## 🧩 Adding New Features

1. **Add service in bot_core/services/**
   ```python
   # bot_core/services/my_feature_service.py
   def my_feature(chat_id: str):
       # Business logic here
       pass
   ```

2. **Import and use in WhatsApp**
   ```python
   # whatsapp_bot.py
   from bot_core.services.my_feature_service import my_feature
   
   if command == 'myfeature':
       my_feature(chat_id)
   ```

3. **Import and use in Telegram**
   ```python
   # tg_bot/modules/my_module.py
   from bot_core.services.my_feature_service import my_feature
   
   def cmd_myfeature(update, context):
       my_feature(update.effective_chat.id)
   ```

## 📊 Statistics

- **Services**: 8 independent services
- **Models**: 9 DB tables
- **Languages**: 2 languages (Hebrew, English)
- **Translation Keys**: 40+ מפתחות
- **Platforms**: 2 (WhatsApp, Telegram)

## 🔐 Security

- ✅ `.gitignore` - Prevents uploading config files
- ✅ `wa_config.py` - Not in version control
- ✅ `tg_bot/config.py` - Not in version control
- ✅ `bot.db` - Not in version control
- ✅ Sessions/Cache - Not in version control

## 📚 Further Reading

- [QUICKSTART.md](QUICKSTART.md) - התחלה מהירה
- [bot_core/README.md](bot_core/README.md) - תיעוד Core
- [USER_GUIDE.md](USER_GUIDE.md) - מדריך משתמש
