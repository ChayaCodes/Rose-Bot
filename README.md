# Rose Bot - Multi-Platform Group Management Bot

![Made with Python](http://ForTheBadge.com/images/badges/made-with-python.svg)

A modular group management bot that works on **both Telegram and WhatsApp**. Originally designed for Telegram, it now features a platform-independent architecture that allows seamless operation on WhatsApp Web.

## 🌟 Features

- **Multi-Platform Support**: Works on both Telegram and WhatsApp
- **Modular Architecture**: Clean separation between bot logic and platform connection
- **Group Management**: Ban, kick, mute, and warn users
- **Auto Moderation**: Anti-flood, blacklist, and spam protection
- **Custom Commands**: Create custom filters and auto-responses
- **Welcome Messages**: Greet new members automatically
- **Admin Tools**: Comprehensive admin commands for group management
- **Easy to Extend**: Simple adapter pattern for adding new platforms

## 📚 Documentation

- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - 📂 Project structure and architecture
- **[bot_core/README.md](bot_core/README.md)** - 🧠 Core module documentation
- **[NAVIGATION.md](docs/NAVIGATION.md)** - 🗺️ Quick navigation map
- **[INDEX.md](docs/INDEX.md)** - 📑 Quick index and stats
- **[SETUP.md](docs/SETUP.md)** - Comprehensive technical setup guide
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Quick start guide for developers
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - User guide for non-technical users
- **[AI_MODERATION_SETUP.md](docs/AI_MODERATION_SETUP.md)** - AI moderation configuration

## 🚀 Quick Start

### For WhatsApp

1. **Install Dependencies**:
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

2. **Configure the Bot**:
```bash
# Go to WhatsApp bot directory
cd bots/whatsapp

# Copy and edit configuration
cp sample_config.py wa_config.py
# Edit wa_config.py with your settings
```

3. **Run Automated Setup** (Recommended):
```bash
python scripts/setup.py
```

4. **Or Start Manually**:
```bash
# Terminal 1: Start WhatsApp Bridge
node bots/whatsapp/bridge.js

# Terminal 2: Start Bot
python bots/whatsapp/bot.py
```

5. **Scan QR Code**:
   - QR code will appear in terminal
   - Scan with WhatsApp on your phone
   - Bot is ready! 
### For Telegram

The original Telegram bot still works!

```bash
python -m bots.telegram
```

See below for Telegram-specific configuration.

## 🏗️ Architecture

```
bot_core/                    # Platform-independent core
├── models/                  # Abstract models (User, Chat, Message)
├── adapters/               # Platform adapters
│   ├── base_adapter.py     # Abstract adapter interface
│   ├── telegram_adapter.py # Telegram implementation
│   └── whatsapp_adapter.py # WhatsApp implementation
└── whatsapp_bridge_client.py # Python client for WhatsApp bridge

whatsapp_bridge.js          # Node.js server for WhatsApp Web API
tg_bot/                     # Telegram-specific bot code
tests/                      # Test suite
```

## 📦 Requirements

### For WhatsApp:
- Python 3.6+
- Node.js 14+
- Dependencies in `requirements.txt` and `package.json`

### For Telegram:
- Python 3.6+
- Dependencies in `requirements.txt`

## ⚙️ Configuration

### WhatsApp Configuration

Create `wa_config.py` from `sample_wa_config.py`:

```python
class WhatsAppConfig:
    OWNER_ID = "1234567890@c.us"  # Your WhatsApp ID
    OWNER_NAME = "Your Name"
    SESSION_NAME = "whatsapp-bot-session"
    PLATFORM = "whatsapp"
    SQLALCHEMY_DATABASE_URI = "sqlite:///bot.db"
    # ... more settings
```

### Telegram Configuration

Create `config.py` in `tg_bot/` folder:

```python
from tg_bot.sample_config import Config

class Development(Config):
    OWNER_ID = 254318997
    OWNER_USERNAME = "YourUsername"
    API_KEY = "your_bot_token"
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost:5432/dbname'
    # ... more settings
```

## 🧪 Testing

Run the test suite:

```bash
python tests/test_bot_core.py
```

All tests should pass before deployment.

## 📖 Available Modules

The bot includes many modules for group management:

- **Admin**: Admin-only commands
- **Bans**: Ban and unban users
- **Muting**: Temporarily silence users
- **Warns**: Warning system with auto-kick
- **Filters**: Custom auto-responses
- **Notes**: Save and retrieve information
- **Welcome**: Welcome new members
- **Rules**: Set and display group rules
- **Blacklist**: Block specific words
- **Antiflood**: Prevent message spam
- **Locks**: Lock specific message types
- **And more!**

## 🚀 Deployment Options

### Method 1: Systemd Service (Linux)

```bash
python setup.py
# Follow prompts to create systemd services
```

### Method 2: Docker

```bash
python setup.py
# Choose Docker option
docker-compose up -d
```

### Method 3: Heroku (Telegram only)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/MRK-YT/Rose-Bot)

## 📝 Module Development

### Creating Custom Modules

1. Create a new `.py` file in `tg_bot/modules/`
2. Import the dispatcher:
   ```python
   from tg_bot import dispatcher
   ```
3. Add handlers:
   ```python
   dispatcher.add_handler(CommandHandler("mycommand", my_function))
   ```

### Module Load Order

Configure in your `config.py` or `wa_config.py`:

```python
LOAD = []  # Empty = load all modules
NO_LOAD = ['translation', 'rss']  # Modules to skip
```

If a module appears in both `LOAD` and `NO_LOAD`, it won't be loaded.

## 🗄️ Database Setup

For database-dependent modules (locks, notes, filters, etc.):

### PostgreSQL (Recommended)

```bash
# Install PostgreSQL
sudo apt-get update && sudo apt-get install postgresql

# Create user
sudo su - postgres
createuser -P -s -e YOUR_USER

# Create database
createdb -O YOUR_USER YOUR_DB_NAME

# Connection URI
postgresql://YOUR_USER:password@localhost:5432/YOUR_DB_NAME
```

### SQLite (Development)

```python
SQLALCHEMY_DATABASE_URI = "sqlite:///bot.db"
```

## 🔧 Environment Variables

For deployment without config files (e.g., Heroku):

```bash
ENV=1  # Enable env mode
TOKEN=your_bot_token
OWNER_ID=your_telegram_id
OWNER_USERNAME=your_username
DATABASE_URL=your_database_url
LOAD=module1 module2
NO_LOAD=module3 module4
SUDO_USERS=user_id1 user_id2
# ... more variables
```

See `sample_config.py` for all available options.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests/test_bot_core.py`
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

See [LICENSE](LICENSE) for details.

## 💡 Support

For help and support:

- Read [USER_GUIDE.md](USER_GUIDE.md) for user instructions
- Check [SETUP.md](SETUP.md) for technical setup
- Review [QUICKSTART.md](QUICKSTART.md) for quick reference

## ⚠️ Disclaimer

This bot is provided as-is. WhatsApp Web automation may violate WhatsApp's Terms of Service. Use at your own risk.

## 🙏 Credits

Originally based on the Rose Bot for Telegram. Extended to support WhatsApp with a modular architecture.

Assigning the `__help__` variable to a string describing this modules' available
commands will allow the bot to load it and add the documentation for
your module to the `/help` command. Setting the `__mod_name__` variable will also allow you to use a nicer, user
friendly name for a module.

The `__migrate__()` function is used for migrating chats - when a chat is upgraded to a supergroup, the ID changes, so 
it is necessary to migrate it in the db.

The `__stats__()` function is for retrieving module statistics, eg number of users, number of chats. This is accessed 
through the `/stats` command, which is only available to the bot owner.
