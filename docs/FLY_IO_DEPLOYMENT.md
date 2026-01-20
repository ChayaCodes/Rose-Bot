# Deploying Rose-Bot to Fly.io

This guide explains how to deploy Rose-Bot (WhatsApp + Python) to Fly.io for free/low-cost hosting.

## Prerequisites

1. **Fly.io Account**: Create one at [fly.io](https://fly.io)
2. **Fly CLI**: Install from [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl/)
3. **GitHub Account**: For CI/CD deployment

## Architecture

Rose-Bot runs as a single container with two processes managed by Supervisor:
- **WhatsApp Bridge** (Node.js): Connects to WhatsApp Web using whatsapp-web.js
- **Python Bot**: Handles commands, moderation, and database operations

```
┌─────────────────────────────────────────┐
│              Fly.io Container           │
│  ┌─────────────────┐  ┌──────────────┐  │
│  │  WhatsApp       │  │  Python Bot  │  │
│  │  Bridge (3000)  │◄─┤  (5000)      │  │
│  │  Node.js        │  │  Flask       │  │
│  └────────┬────────┘  └──────────────┘  │
│           │                              │
│  ┌────────▼────────┐                    │
│  │  Chromium       │                    │
│  │  (headless)     │                    │
│  └─────────────────┘                    │
│                                          │
│  Volume: /app/data (session + database)  │
└─────────────────────────────────────────┘
```

## Initial Setup

### 1. Login to Fly.io

```bash
flyctl auth login
```

### 2. Create the App

```bash
flyctl apps create rose-bot-wa
```

### 3. Create Persistent Volume

The volume stores WhatsApp session and SQLite database:

```bash
flyctl volumes create rose_bot_data --region ams --size 1 -a rose-bot-wa
```

### 4. Set Secrets

```bash
# Required
flyctl secrets set OWNER_ID="your_phone@c.us" -a rose-bot-wa

# Optional
flyctl secrets set OWNER_NAME="Your Name" -a rose-bot-wa
flyctl secrets set OPENAI_API_KEY="sk-..." -a rose-bot-wa
```

**Note**: Phone format is `972501234567@c.us` (country code + number, no leading zeros)

## Deployment Options

### Option A: GitHub Actions (Recommended)

1. Get a Fly.io API token:
   ```bash
   flyctl tokens create deploy -x 999999h
   ```

2. Add the token to GitHub:
   - Go to your repo → Settings → Secrets → Actions
   - Add `FLY_API_TOKEN` with the token value

3. Push to `production` branch:
   ```bash
   git push origin main:production
   ```

4. GitHub Actions will automatically deploy on every push to `production`.

### Option B: Manual Deploy

```bash
flyctl deploy --remote-only
```

## First-Time Authentication

After deployment, you need to scan a QR code to link WhatsApp:

### 1. Watch the Logs

```bash
flyctl logs -a rose-bot-wa
```

### 2. Find the QR Code

Look for output like:
```
QR Code received. Scan with WhatsApp:
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█ ▄▄▄▄▄ █ ▄▄█  █▄▀ ▀█▄██▄▄█▄▄█
...
```

### 3. Scan with WhatsApp

1. Open WhatsApp on your phone
2. Go to **Settings** → **Linked Devices** → **Link a Device**
3. Scan the QR code from the logs

### 4. Verify Connection

You should see:
```
WhatsApp Client is ready!
✅ WhatsApp Bridge is ready!
Bot is running! Send /start to test
```

## Configuration Files

### fly.toml

```toml
app = "rose-bot-wa"
primary_region = "ams"

[build]

[env]
  NODE_ENV = "production"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = "off"
  auto_start_machines = true
  min_machines_running = 1

  [http_service.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

[[http_service.checks]]
  grace_period = "60s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"

[[vm]]
  memory = "2gb"
  cpu_kind = "shared"
  cpus = 1

[mounts]
  source = "rose_bot_data"
  destination = "/app/data"
```

### Dockerfile

The Dockerfile installs:
- Node.js 18 (for WhatsApp bridge)
- Python 3 (for bot logic)
- Chromium (for WhatsApp Web)
- Supervisor (process manager)

## Useful Commands

```bash
# View logs
flyctl logs -a rose-bot-wa

# SSH into container
flyctl ssh console -a rose-bot-wa

# Check app status
flyctl status -a rose-bot-wa

# Restart the machine
flyctl machine restart -a rose-bot-wa

# Check health
flyctl ssh console -a rose-bot-wa -C "curl -s http://localhost:3000/health"

# View QR code endpoint
flyctl ssh console -a rose-bot-wa -C "curl -s http://localhost:3000/qr"
```

## Troubleshooting

### QR Code Not Appearing

1. Delete existing session:
   ```bash
   flyctl ssh console -a rose-bot-wa -C "rm -rf /app/data/.wwebjs_auth/session-*"
   ```

2. Restart the machine:
   ```bash
   flyctl machine restart -a rose-bot-wa
   ```

### Chromium Crashes (SIGSEGV)

Increase memory in `fly.toml`:
```toml
[[vm]]
  memory = "2gb"
```

### Database Errors

The database is initialized automatically on startup. If you see "no such table" errors, restart the machine.

### WhatsApp Disconnects

The session is stored in `/app/data/.wwebjs_auth/`. If you get disconnected:
1. Check WhatsApp on your phone for "Linked Devices"
2. Remove and re-link if needed
3. The QR code will appear in logs

## Cost Estimation

Fly.io pricing (as of 2025):
- **Free tier**: 3 shared-cpu-1x VMs with 256MB RAM
- **This bot**: Uses ~$5-10/month with 2GB RAM

To reduce costs:
- Use `memory = "1gb"` (may be unstable)
- Use a region closer to you for lower latency

## Security Notes

1. **Secrets**: Never commit API keys or tokens to git
2. **Owner ID**: Only the owner can execute admin commands
3. **Database**: SQLite is stored on a persistent volume
4. **Session**: WhatsApp session is encrypted and stored on the volume

## Support

- **Fly.io Docs**: [fly.io/docs](https://fly.io/docs)
- **whatsapp-web.js**: [github.com/pedroslopez/whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js)
- **Issues**: Open an issue in this repository
