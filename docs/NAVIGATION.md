# 🗺️ Quick Navigation Map - Rose Bot

## 📌 Main Files

### Running the Bot
- 🤖 [whatsapp_bot.py](whatsapp_bot.py) - WhatsApp entry point
- 🌉 [whatsapp_bridge.js](whatsapp_bridge.js) - Node.js WhatsApp bridge
- 📱 [tg_bot/__main__.py](tg_bot/__main__.py) - Telegram entry point

### Configuration
- ⚙️ [wa_config.py](wa_config.py) - WhatsApp settings (not in version control)
- 📋 [sample_wa_config.py](sample_wa_config.py) - Configuration template
- 🔧 [tg_bot/sample_config.py](tg_bot/sample_config.py) - Telegram template

## 🧠 Bot Core

### קבצים מרכזיים
```
bot_core/
├── 📦 __init__.py              # ייצוא כל המודולים
├── 🗄️ database.py             # ניהול DB + SQLAlchemy
├── 🌍 i18n.py                 # תרגומים (עברית/אנגלית)
├── 📊 models.py               # טבלאות DB (9 models)
└── 🛡️ content_filter.py      # AI moderation
```

### Services (Business Logic)
```
bot_core/services/
├── 📦 __init__.py                  # Services export
├── 🌐 language_service.py          # Language management
├── ⚠️ warn_service.py              # Warnings
├── 📜 rules_service.py             # Rules
├── 👋 welcome_service.py           # Welcome messages
├── 🚫 blacklist_service.py         # Blacklist
├── 🔒 locks_service.py             # Locks
├── 🤖 ai_moderation_service.py    # AI moderation
└── 🌊 flood_service.py             # Flood control
```

### Adapters (Platform Adapters)
```
bot_core/adapters/
├── 📦 __init__.py              # Adapters export
├── 🎯 base_adapter.py          # Base interface
├── 💬 whatsapp_adapter.py      # WhatsApp
└── ✈️ telegram_adapter.py      # Telegram
```

### Models (Abstract Models)
```
bot_core/models/
├── 📦 __init__.py              # Models export
├── 💬 message.py               # BotMessage
├── 👤 user.py                  # BotUser
└── 💭 chat.py                  # BotChat
```

## 📚 Documentation

### Main Documentation
- 📖 [README.md](README.md) - סקירה כללית
- 🏗️ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - **מבנה מפורט**
- 🧠 [bot_core/README.md](bot_core/README.md) - תיעוד Core

### Guides
- 🚀 [QUICKSTART.md](QUICKSTART.md) - Quick start
- 🔧 [SETUP.md](SETUP.md) - Installation guide
- 👥 [USER_GUIDE.md](USER_GUIDE.md) - User guide
- 🤖 [AI_MODERATION_SETUP.md](AI_MODERATION_SETUP.md) - AI setup

### Additional Info
- 📊 [FEATURE_COMPARISON.md](FEATURE_COMPARISON.md) - Features comparison
- 🚢 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deploy checklist
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## 🔍 What am I looking for?

### "Want to add a new feature"
1. Create new service: `bot_core/services/my_service.py`
2. Add to `bot_core/services/__init__.py`
3. Use in `whatsapp_bot.py` or `tg_bot/modules/`

### "Want to understand the architecture"
1. Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. Read [bot_core/README.md](bot_core/README.md)
3. Check `bot_core/services/` for examples

### "Want to install the bot"
1. Start with [QUICKSTART.md](QUICKSTART.md)
2. Go to [SETUP.md](SETUP.md) for detailed info
3. Use `setup.py` for automation

### "Want to understand how to work with the code"
1. Check `bot_core/__init__.py` for exports list
2. See examples in `bot_core/services/`
3. See usage in `whatsapp_bot.py`

### "Want to add a new platform"
1. Create new adapter: `bot_core/adapters/my_platform_adapter.py`
2. Extend `base_adapter.py`
3. Convert messages to BotMessage, BotUser, BotChat
4. Use existing services

### "Want to translate to a new language"
1. Open `bot_core/i18n.py`
2. Add language to `LANG_NAMES`
3. Add translations to `TRANSLATIONS`

### "There's a bug"
1. Check logs
2. Check `bot.db` (SQLite)
3. See `tests/test_bot_core.py` for tests

## 📦 Dependencies

### Python
- `requirements.txt` - All packages
- SQLAlchemy, Flask, requests

### Node.js
- `package.json` - Node packages
- whatsapp-web.js, qrcode-terminal

## 🎯 Entry Points

### Development
```bash
# WhatsApp
python whatsapp_bot.py

# Telegram
python -m tg_bot
```

### Tests
```bash
python -m pytest tests/
```

### Setup
```bash
python setup.py
```

## 🔑 Important Files (not in version control)

- ⚠️ `wa_config.py` - WhatsApp keys
- ⚠️ `tg_bot/config.py` - Telegram keys
- ⚠️ `bot.db` - Database
- ⚠️ `.wwebjs_auth/` - WhatsApp session
- ⚠️ `.env` - Environment variables

## 💡 Tips

- Use `bot_core/services/` for all business logic
- Don't write platform-specific code in services
- Use `get_translated_text()` for all user messages
- Adapters only convert - no business logic
- Each service should be independent and testable

---

**Need more help?** Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed info!
