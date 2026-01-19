# Quick Start Guide

## 🚀 Quick WhatsApp Setup

### Step 1: Install Python packages

```bash
pip install -r requirements.txt
```

### Step 2: Install Node.js packages

```bash
npm install
```

### Step 3: Start the Bridge

In one terminal:
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

### Step 4: Configure the bot

```bash
copy sample_wa_config.py wa_config.py
```

Edit `wa_config.py`:
```python
OWNER_ID = "14155551234@c.us"  # Your number
OWNER_NAME = "Your Name"
```

### Step 5: Run the bot

In a second terminal:
```bash
python whatsapp_bot.py
```

### Step 6: Scan QR Code

1. Open WhatsApp on your phone
2. Go to Settings > Linked Devices
3. Tap "Link a Device"
4. Scan the QR code in the terminal

✅ Bot is ready! Send a message: `/start`

---

## 🎯 Basic Commands

```
/start - Start conversation
/help - Show help
/info - Bot information
/echo <text> - Repeat text
```

---

## 🔧 Health Check

Check if Bridge is working:
```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "ok",
  "ready": true
}
```

---

## ⚠️ Common Issues

### ❌ QR not displaying

**Solution:**
```bash
pip install qrcode[pil]
```

### ❌ Bridge not working

**Solution:**
```bash
# Verify Node.js is installed
node --version

# Reinstall packages
npm install
```

### ❌ Bot not responding

**Solution:**
1. Make sure Bridge is running (terminal 1)
2. Make sure Python bot is running (terminal 2)
3. Verify you scanned the QR code

---

## 🎨 Simple Example

Create `my_bot.py`:

```python
from bot_core.adapters import WhatsAppAdapter
from bot_core.models import BotMessage

# Configuration
config = {
    'session_name': 'my-session'
}

# Create bot
bot = WhatsAppAdapter(config)

# Add command
@bot.on_command('hi')
def say_hi(adapter, message: BotMessage, args: str):
    adapter.send_message(
        message.chat.id,
        f"Hi {message.sender.first_name}! 👋"
    )

# Run
bot.run()
```

Run it:
```bash
python my_bot.py
```

---

## 📱 WhatsApp Phone Number Format

```
USA: 14155551234@c.us
UK: 441234567890@c.us
India: 919876543210@c.us
```

**Formula:** `[CountryCode][Number without leading 0]@c.us`

---

**Ready to go! Good luck! 🎉**
