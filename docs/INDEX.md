# 📑 Quick Index - Rose Bot

## ✅ What's Been Done

### 🗂️ Reorganization
- ✅ Created `bot_core/services/` directory with 8 services
- ✅ Created `bot_core/services/__init__.py` for central export
- ✅ Moved `whatsapp_bot_full.py` → `whatsapp_bot.py`
- ✅ Deleted unnecessary files (example_bot, simple_bot)

### 📚 Documentation
- ✅ `PROJECT_STRUCTURE.md` - Detailed structure
- ✅ `NAVIGATION.md` - Navigation map
- ✅ `bot_core/README.md` - Core documentation
- ✅ `INDEX.md` - This index

### 🧠 Services Created
1. ✅ `language_service.py` - Language management
2. ✅ `warn_service.py` - Warnings
3. ✅ `rules_service.py` - Rules
4. ✅ `welcome_service.py` - Welcome messages
5. ✅ `blacklist_service.py` - Blacklist
6. ✅ `locks_service.py` - Locks
7. ✅ `ai_moderation_service.py` - AI moderation
8. ✅ `flood_service.py` - Flood control

## 📊 Statistics

### Files
- **Services**: 8 files + `__init__.py`
- **Adapters**: 3 files (base, whatsapp, telegram)
- **Models (DB)**: 1 file (9 tables)
- **Models (Abstract)**: 3 files (message, user, chat)
- **Core**: 5 files (database, i18n, models, content_filter, bridge_client)

### Lines of Code (Estimated)
- **Services**: ~1,200 lines
- **Adapters**: ~800 lines
- **Models**: ~300 lines
- **Core**: ~600 lines
- **Documentation**: ~1,500 lines

## 🎯 Project Status

### ✅ Completed
- ✅ Modular architecture
- ✅ Separation of concerns (services/adapters/models)
- ✅ Support for 2 platforms (WhatsApp, Telegram)
- ✅ Translation system (Hebrew/English)
- ✅ 8 independent services
- ✅ Comprehensive documentation

### 🔄 In Progress
- 🔄 Update `whatsapp_bot.py` to use new services
- 🔄 Update `tg_bot/modules/` to use new services
- 🔄 Unit tests for services

### 📝 Future Plans
- 📝 Add CI/CD
- 📝 Docker support
- 📝 Support for additional platforms
- 📝 Web dashboard

## 🔗 Quick Links

### Documentation
- [README.md](README.md) - Overview
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detailed structure
- [NAVIGATION.md](NAVIGATION.md) - Navigation map
- [bot_core/README.md](bot_core/README.md) - Core documentation

### Code
- [bot_core/__init__.py](bot_core/__init__.py) - Central export
- [bot_core/services/](bot_core/services/) - Services directory
- [whatsapp_bot.py](whatsapp_bot.py) - WhatsApp bot
- [tg_bot/](tg_bot/) - Telegram bot

### Configuration
- [requirements.txt](requirements.txt) - Python dependencies
- [package.json](package.json) - Node dependencies
- [.gitignore](.gitignore) - Git ignore rules

## 🛠️ Common Actions

### Getting Started
```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run WhatsApp bot
node whatsapp_bridge.js  # in one window
python whatsapp_bot.py   # in another window

# Run Telegram bot
python -m tg_bot
```

### Development
```bash
# Add new service
# 1. Create bot_core/services/my_service.py
# 2. Add to bot_core/services/__init__.py
# 3. Use in whatsapp_bot.py or tg_bot/modules/

# Run tests
python -m pytest tests/
```

### Documentation
```bash
# Read first:
# 1. PROJECT_STRUCTURE.md - Understand the structure
# 2. bot_core/README.md - Learn the Core
# 3. NAVIGATION.md - Navigate the code
```

## 📞 Support

### FAQ
**Q: Where do I add business logic?**  
A: In `bot_core/services/` - create new service or add to existing

**Q: How do I add a platform?**  
A: Create new adapter in `bot_core/adapters/`

**Q: How do I change messages?**  
A: Edit `bot_core/i18n.py` (TRANSLATIONS dict)

**Q: Where's the database?**  
A: `bot.db` (SQLite) - models in `bot_core/models.py`

**Q: How do I add translation?**  
A: Add language to `LANG_NAMES` and `TRANSLATIONS` in `bot_core/i18n.py`

### Common Issues
- ❌ **ImportError**: Make sure `__init__.py` exists in every directory
- ❌ **Database Error**: Delete `bot.db` and restart
- ❌ **WhatsApp not connecting**: Check `whatsapp_bridge.js` is running
- ❌ **Translations not working**: Check chat language in DB

## 🎓 Learning

### Recommended Starting Points:
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Examine `bot_core/services/rules_service.py` (simple)
3. Understand `bot_core/adapters/base_adapter.py`
4. See how `whatsapp_bot.py` uses services

### Code Examples
```python
# Using a service
from bot_core.services import rules_service

# Get rules
rules = rules_service.get_rules(chat_id="123")

# Set rules
rules_service.set_rules(
    chat_id="123",
    rules_text="No spam!"
)

# Using translation
from bot_core.services.language_service import get_translated_text

text = get_translated_text(
    chat_id="123",
    key="rules_set"
)
```

---

**Last Updated**: 2026-01-19  
**Version**: 2.0.0 (Refactored Architecture)
