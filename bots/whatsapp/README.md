# WhatsApp Bot

Full-featured WhatsApp group management bot.

## 🚀 Quick Start

### 1. Configuration

```bash
# Copy sample config and edit
cp sample_config.py wa_config.py

# Edit wa_config.py:
# - Set OWNER_ID to your WhatsApp number (format: "972501234567@c.us")
```

### 2. Run the Bot

**🎯 Easy Way (Recommended) - One Command:**

**Windows (PowerShell):**
```powershell
cd bots/whatsapp
.\start.ps1
```

**Linux/Mac:**
```bash
cd bots/whatsapp
chmod +x start.sh
./start.sh
```

**Python (Cross-platform):**
```bash
cd bots/whatsapp
python start.py
```

**⚙️ Manual Way (Advanced) - Two Terminals:**

**Terminal 1 - Start Bridge:**
```bash
cd bots/whatsapp
node bridge.js
```

**Terminal 2 - Start Bot:**
```bash
cd bots/whatsapp
python bot.py
```

### 3. Scan QR Code

- QR code will appear in the terminal
- Scan with WhatsApp on your phone (Linked Devices)
- Bot is ready! ✅

## 📁 Files

- `bot.py` - Main bot logic
- `bridge.js` - WhatsApp Web bridge (Node.js)
- `wa_config.py` - Configuration (create from sample_config.py)
- `sample_config.py` - Configuration template

## 🔧 Configuration

Edit `wa_config.py`:

```python
class Development(WhatsAppConfig):
    # Your WhatsApp number (bot owner)
    OWNER_ID = "972501234567@c.us"
    
    # Database (SQLite by default)
    SQLALCHEMY_DATABASE_URI = "sqlite:///bot.db"
    
    # Bridge connection
    BRIDGE_URL = "http://localhost:5000"
```

## 🗄️ Database

Database file `bot.db` is created automatically in this directory on first run.

Tables:
- `warns` - User warnings
- `warn_settings` - Warning limits per chat
- `rules` - Chat rules
- `welcome` - Welcome messages
- `blacklist` - Blacklisted words
- `locks` - Content locks
- And more...

## 🛠️ Troubleshooting

### Bot not connecting to bridge
- Make sure `bridge.js` is running first
- Check `BRIDGE_URL` in wa_config.py (default: http://localhost:5000)

### QR code expired
- Restart `bridge.js`
- Delete `.wwebjs_auth/` folder and try again

### Database errors
- Delete `bot.db` and restart bot (will create fresh database)

## 📚 Documentation

See [main documentation](../../docs/) for full feature list and usage.
