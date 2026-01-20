# Rose Bot - Test Checklist

## 📋 Comprehensive Test Coverage Plan

**Test Files Created:**
- ✅ `conftest.py` - Pytest fixtures and configuration
- ✅ `test_warn_service.py` - Warn service tests
- ✅ `test_rules_service.py` - Rules service tests
- ✅ `test_welcome_service.py` - Welcome service tests
- ✅ `test_blacklist_service.py` - Blacklist service tests
- ✅ `test_locks_service.py` - Locks service tests
- ✅ `test_flood_service.py` - Flood service tests
- ✅ `test_language_service.py` - Language/i18n tests
- ✅ `test_ban_service.py` - Ban/mute/kick tests
- ✅ `test_ai_moderation_service.py` - AI moderation tests
- ✅ `test_shared_bot_logic.py` - Command handling tests
- ✅ `test_integration.py` - Integration tests
- ✅ `test_future_features.py` - Planned feature tests (skipped)

---

### 1. 🗄️ Database & Models Tests
- [x] Database connection and session management
- [x] Model creation (all SQLAlchemy models)
- [x] CRUD operations for each model
- [x] Foreign key relationships
- [ ] Index performance

### 2. 📦 Service Layer Tests

#### 2.1 Warn Service (`warn_service.py`) ✅
- [x] `warn_user()` - Add warning to user
- [x] `warn_user()` - Auto-kick on warn limit reached
- [x] `get_user_warns()` - Get current warnings
- [x] `reset_user_warns()` - Reset warnings to 0
- [x] `set_warn_limit()` - Set custom warn limit
- [x] `get_warn_limit()` - Get warn limit (default 3)
- [x] `get_warn_settings()` - Get all warn settings
- [x] Edge cases: Non-existent user, limit of 0, negative values

#### 2.2 Rules Service (`rules_service.py`) ✅
- [x] `get_rules()` - Get rules (exists/not exists)
- [x] `set_rules()` - Set new rules
- [x] `set_rules()` - Update existing rules
- [x] `clear_rules()` - Delete rules
- [x] Edge cases: Empty rules, very long text, special characters

#### 2.3 Welcome Service (`welcome_service.py`) ✅
- [x] `get_welcome_message()` - Get welcome (exists/not exists)
- [x] `set_welcome_message()` - Set new welcome
- [x] `clear_welcome_message()` - Delete welcome
- [x] `format_welcome_message()` - Variable replacement ({mention}, {name})
- [x] Edge cases: Empty message, {mention} variations

#### 2.4 Blacklist Service (`blacklist_service.py`) ✅
- [x] `add_blacklist_word()` - Add word
- [x] `add_blacklist_word()` - Duplicate word handling
- [x] `remove_blacklist_word()` - Remove existing word
- [x] `remove_blacklist_word()` - Non-existent word
- [x] `get_blacklist_words()` - List all words
- [x] `check_blacklist()` - Detect blacklisted word
- [x] `check_blacklist()` - Case insensitivity
- [x] `check_blacklist()` - Partial word matching
- [x] `clear_blacklist()` - Clear all words
- [x] Edge cases: Empty blacklist, special characters, Hebrew words

#### 2.5 Locks Service (`locks_service.py`) ✅
- [x] `set_lock()` - Enable lock type
- [x] `set_lock()` - Disable lock type
- [x] `get_locks()` - Get all locks for chat
- [x] `is_locked()` - Check specific lock
- [x] `check_message_locks()` - Check message against locks
- [x] `clear_locks()` - Clear all locks
- [x] Lock types: links, stickers, media
- [x] Edge cases: Invalid lock type, multiple locks

#### 2.6 Ban Service (`ban_service.py`) ✅
- [x] `add_ban()` - Ban user
- [x] `add_ban()` - Re-ban already banned user
- [x] `remove_ban()` - Unban user
- [x] `is_banned()` - Check ban status
- [x] `get_banned_users()` - List banned users
- [x] Edge cases: Ban reason, ban by admin tracking

#### 2.7 Flood Service (`flood_service.py`) ✅
- [x] `check_flood()` - Normal message rate
- [x] `check_flood()` - Flood detected
- [x] `clear_old_flood_records()` - Cleanup old records
- [x] `reset_user_flood()` - Reset user flood counter
- [x] Edge cases: Time window, burst messages

#### 2.8 Language Service (`language_service.py`) ✅
- [x] `get_chat_language()` - Get language (default 'he')
- [x] `set_chat_language()` - Set Hebrew
- [x] `set_chat_language()` - Set English
- [x] `get_translated_text()` - Get text in correct language
- [x] Edge cases: Invalid language code, missing translation key

#### 2.9 AI Moderation Service (`ai_moderation_service.py`) ✅
- [x] `get_ai_settings()` - Default settings
- [x] `set_ai_enabled()` - Enable/disable
- [x] `set_ai_threshold()` - Set threshold (0.0-1.0)
- [x] `set_ai_action()` - Set action (warn/delete/kick/ban)
- [x] `set_ai_category_thresholds()` - Per-category thresholds
- [x] `check_content_toxicity()` - OpenAI backend
- [x] `_resolve_backend()` - Force OpenAI
- [x] Edge cases: Invalid threshold, API errors, timeout

#### 2.10 Chat Config Service (`chat_config_service.py`)
- [ ] `should_delete_commands()` - Get delete commands setting
- [ ] `set_delete_commands()` - Enable/disable

### 3. 🤖 Bot Logic Tests (`shared_bot_logic.py`) ✅

#### 3.1 Command Parsing
- [x] Parse `/command` format
- [x] Parse `/command args` format
- [ ] Parse `/command@bot` format
- [ ] Handle invalid commands
- [ ] Handle empty input

#### 3.2 Admin Commands
- [ ] `/kick` - Kick user (admin only)
- [ ] `/ban` - Ban user (admin only)
- [ ] `/warn` - Warn user
- [ ] `/warns` - Show user warnings
- [ ] `/resetwarns` - Reset warnings
- [ ] `/setwarn` - Set warn limit
- [ ] Non-admin attempting admin commands

#### 3.3 Rules & Welcome Commands
- [ ] `/rules` - Show rules
- [ ] `/setrules` - Set rules (admin)
- [ ] `/clearrules` - Clear rules (admin)
- [ ] `/welcome` - Show welcome
- [ ] `/setwelcome` - Set welcome (admin)

#### 3.4 Blacklist Commands
- [ ] `/blacklist` - Show blacklist
- [ ] `/addblacklist` - Add word (admin)
- [ ] `/rmblacklist` - Remove word (admin)
- [ ] Auto-delete on blacklist match

#### 3.5 Lock Commands
- [ ] `/lock` - Lock type (admin)
- [ ] `/unlock` - Unlock type (admin)
- [ ] `/locks` - Show locks

#### 3.6 AI Moderation Commands
- [ ] `/aimod on` - Enable AI
- [ ] `/aimod off` - Disable AI
- [ ] `/aimodstatus` - Show status
- [ ] `/aimodset` - Set thresholds
- [ ] `/aimodthreshold` - Set global threshold
- [ ] `/aimodaction` - Set action
- [ ] `/aitest` - Test text
- [ ] `/aihelp` - Show help

#### 3.7 Utility Commands
- [ ] `/start` - Start message
- [ ] `/help` - Help message
- [ ] `/ping` - Pong response
- [ ] `/id` - Show chat/user ID
- [ ] `/lang` - Language commands
- [ ] `/info` - Bot info

### 4. 🌐 i18n Tests (`i18n.py`)
- [ ] Hebrew translations complete
- [ ] English translations complete
- [ ] Variable substitution ({var})
- [ ] Missing key fallback
- [ ] COMMAND_HELP structure

### 5. 🔌 Integration Tests

#### 5.1 WhatsApp Bridge Client
- [ ] Connect to bridge
- [ ] Send message
- [ ] Receive message
- [ ] Health check
- [ ] Reconnection on disconnect

#### 5.2 End-to-End Flows
- [ ] User joins → welcome sent
- [ ] User warned 3 times → kicked
- [ ] Blacklisted word → message deleted
- [ ] Toxic content → AI action taken
- [ ] Locked content → message blocked

### 6. 🚀 Future Features Tests (Planned)

#### 6.1 Filters System
- [ ] `add_filter()` - Add auto-reply
- [ ] `remove_filter()` - Remove filter
- [ ] `get_filters()` - List filters
- [ ] `check_filters()` - Check message matches
- [ ] Multi-word triggers
- [ ] Media filters

#### 6.2 Notes System
- [ ] `save_note()` - Save note
- [ ] `get_note()` - Get note by name
- [ ] `delete_note()` - Delete note
- [ ] `list_notes()` - List all notes
- [ ] `#notename` trigger

#### 6.3 Antiflood Actions
- [ ] Configurable flood limit
- [ ] Configurable time window
- [ ] Actions: warn/mute/kick/ban
- [ ] Admin exemption

#### 6.4 Goodbye Messages
- [ ] Set goodbye message
- [ ] Auto-send on user leave
- [ ] Variable substitution

#### 6.5 Report System
- [ ] `/report` command
- [ ] Notify admins
- [ ] Report logging

### 7. 📊 Performance Tests
- [ ] Database query performance
- [ ] Message processing latency
- [ ] Concurrent message handling
- [ ] Memory usage under load

### 8. 🔒 Security Tests
- [ ] Admin permission checks
- [ ] Owner-only commands
- [ ] Input sanitization
- [ ] SQL injection prevention
- [ ] Rate limiting

---

## 🏃 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_services.py -v

# Run with coverage
python -m pytest tests/ --cov=bot_core --cov-report=html

# Run only fast tests (no API calls)
python -m pytest tests/ -m "not slow" -v
```

## 📈 Coverage Goals
- **Minimum:** 70%
- **Target:** 85%
- **Ideal:** 95%

---
*Last Updated: January 20, 2026*
