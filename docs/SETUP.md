# WhatsApp Bot Setup Guide

## Overview

This bot is a powerful group management tool for WhatsApp. It has been refactored with a modular architecture that separates bot logic from platform-specific code.

## Architecture

```
┌─────────────────────────────────┐
│     Bot Logic (Modules)         │
│  (Admin, Bans, Warns, etc.)     │
└────────────┬────────────────────┘
             │
     ┌───────┴────────┐
     │   Bot Core     │
     │   (Abstract)   │
     └───────┬────────┘
             │
     ┌───────┴────────┐
     │                │
┌────┴─────┐   ┌─────┴────┐
│ Telegram │   │ WhatsApp │
│ Adapter  │   │ Adapter  │
└──────────┘   └──────────┘
```

### Key Components

- **bot_core/** - Platform-independent core framework
  - **models/** - Abstract models (Message, User, Chat)
  - **adapters/** - Platform adapters (Telegram, WhatsApp)
- **whatsapp_bot.py** - WhatsApp bot entry point
- **whatsapp_bridge.js** - Node.js bridge for WhatsApp Web

## Features

### Supported Features

✅ Text messages
✅ Media (images, videos, audio)
✅ Group management
✅ Admin promotion
✅ Member removal
✅ Basic formatting

### WhatsApp Limitations

❌ **Not Supported:**
- Message editing
- Message pinning
- Inline keyboards
- Temporary bans

## Installation

### Prerequisites

1. **Python 3.6+**
2. **Node.js 14+** (required for WhatsApp Web API)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install WhatsApp Web Library

```bash
npm install
```

### Step 3: Configure the Bot

1. Copy the sample config:
```bash
copy sample_wa_config.py wa_config.py
```

2. Edit `wa_config.py` and set:
   - `OWNER_ID` - Your phone number in format: `CountryCodeNumber@c.us` (e.g., `14155551234@c.us`)
   - `OWNER_NAME` - Your name
   - `SQLALCHEMY_DATABASE_URI` - Database connection string

### Step 4: Run the Bridge Server

In terminal 1:
```bash
npm start
```

Or:
```bash
node whatsapp_bridge.js
```

You should see:
```
WhatsApp Bridge running on port 3000
Waiting for WhatsApp authentication...
```

### Step 5: Run the Bot

In terminal 2:
```bash
python whatsapp_bot.py
```

### Step 6: Scan QR Code

1. Open WhatsApp on your phone
2. Go to Settings > Linked Devices
3. Tap "Link a Device"
4. Scan the QR code displayed in the terminal

✅ The bot is ready! Send it a message: `/start`

## Message Formatting

### WhatsApp Formatting:
```
*bold*
_italic_
~strikethrough~
```monospace```
```

The adapter automatically converts Markdown to WhatsApp format!

## Example Commands

```python
# Send a simple message
adapter.send_message(chat_id, "Hello!")

# Send formatted message
adapter.send_message(
    chat_id, 
    "*Bold text* and _italic_",
    parse_mode="Markdown"
)

# Ban user (remove from group)
adapter.ban_chat_member(group_id, user_id)

# Promote to admin
adapter.promote_chat_member(
    group_id, 
    user_id,
    can_change_info=True,
    can_delete_messages=True
)
```

## Advanced: WhatsApp Web Bridge

The WhatsApp adapter requires a Node.js bridge to communicate with WhatsApp Web.

### Bridge API Endpoints:

- `GET /health` - Check bridge status
- `POST /send-message` - Send text message
- `POST /send-media` - Send media
- `GET /chat/:chatId` - Get chat info
- `GET /group/:groupId/members` - Get group members
- `POST /group/:groupId/remove` - Remove participant
- `POST /group/:groupId/promote` - Promote to admin
- `POST /group/:groupId/demote` - Demote from admin

## Troubleshooting

### QR Code not appearing
- Make sure Node.js and whatsapp-web.js are installed
- Install qrcode library: `pip install qrcode[pil]`

### Session expired
- Delete the session folder and scan QR again
- Default location: `.wwebjs_auth/`

### Messages not sending
- Check if the WhatsApp bridge is running
- Verify phone numbers are in correct format: `CountryCodeNumber@c.us`

### Bridge connection issues
```bash
# Check if bridge is running
curl http://localhost:3000/health

# Expected response:
# {"status": "ok", "ready": true}
```

## Phone Number Format

```
USA: 14155551234@c.us
UK: 441234567890@c.us
India: 919876543210@c.us
```

**Formula:** `[CountryCode][Number without leading 0]@c.us`

## Production Deployment

### Using Docker (Recommended):

```bash
# Build
docker build -t whatsapp-bot .

# Run
docker run -d whatsapp-bot
```

### Using PM2 (Node.js):

```bash
# Install PM2
npm install -g pm2

# Run Bridge
pm2 start whatsapp_bridge.js --name wa-bridge

# Run Bot (Python)
pm2 start python --name wa-bot -- whatsapp_bot.py

# Check status
pm2 status
```

## Security

1. **Don't share your session folder:**
   - `.wwebjs_auth/` - contains your authentication

2. **Use Environment Variables:**
```bash
export OWNER_ID="14155551234@c.us"
python whatsapp_bot.py
```

3. **Limit access:**
```python
# In config file
SUDO_USERS = ["14155551234@c.us"]  # Only these users can use admin commands
```

## Monitoring

Check logs:

**Bridge:**
```bash
# If running in terminal
# Logs appear there

# If running with PM2
pm2 logs wa-bridge
```

**Bot:**
```bash
# Python logs
tail -f bot.log

# Or with PM2
pm2 logs wa-bot
```

## Updates

Update the bot:

```bash
# Update Python packages
pip install -r requirements.txt --upgrade

# Update Node.js packages
npm update

# Restart
pm2 restart all
```

## License

Same as original Rose Bot - check LICENSE file
