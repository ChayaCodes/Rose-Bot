# Deployment Checklist

Use this checklist before deploying your WhatsApp bot to production.

## ✅ Pre-Deployment Checklist

### 1. Requirements Installation

- [ ] Python 3.6+ installed
- [ ] Node.js 14+ installed
- [ ] npm installed
- [ ] All Python dependencies installed (`pip install -r requirements.txt`)
- [ ] All Node.js dependencies installed (`npm install`)

### 2. Configuration

- [ ] Created `wa_config.py` from `sample_wa_config.py`
- [ ] Set `OWNER_ID` with your WhatsApp number (format: `1234567890@c.us`)
- [ ] Set `OWNER_NAME`
- [ ] Set `SESSION_NAME` (unique session identifier)
- [ ] Configured database URI (`SQLALCHEMY_DATABASE_URI`)
- [ ] Added trusted users to `SUDO_USERS` list
- [ ] Configured `LOAD` and `NO_LOAD` modules

### 3. Database Setup

- [ ] Database server installed (PostgreSQL recommended)
- [ ] Database created
- [ ] Database user created with proper permissions
- [ ] Database URI tested and working
- [ ] Tables will be created automatically on first run

### 4. Testing

- [ ] Ran test suite: `python tests/test_bot_core.py`
- [ ] All 11 tests passed
- [ ] No import errors
- [ ] WhatsApp bridge starts without errors: `node whatsapp_bridge.js`
- [ ] Bot starts without errors: `python whatsapp_bot.py`

### 5. Security

- [ ] `wa_config.py` added to `.gitignore`
- [ ] No sensitive data in version control
- [ ] Strong database password set
- [ ] Limited sudo/admin users configured
- [ ] Review and restrict user permissions

### 6. WhatsApp Account

- [ ] Have a dedicated phone number for the bot (recommended)
- [ ] WhatsApp installed on that phone
- [ ] Phone can scan QR codes
- [ ] Phone has stable internet connection
- [ ] Account is not used for personal messages (to avoid ban risk)

### 7. Infrastructure

#### For Manual Deployment:

- [ ] Server or computer always on
- [ ] Stable internet connection
- [ ] Firewall configured (allow ports 3000, 5000 if needed)
- [ ] Process manager configured (PM2, systemd, or similar)

#### For Docker Deployment:

- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Dockerfile tested: `docker build -t whatsapp-bot .`
- [ ] docker-compose.yml configured
- [ ] Volumes for persistent data configured

#### For Systemd Service:

- [ ] Service files created (`whatsapp-bridge.service`, `whatsapp-bot.service`)
- [ ] Services installed in `/etc/systemd/system/`
- [ ] Services enabled: `sudo systemctl enable whatsapp-bridge whatsapp-bot`
- [ ] Services tested: `sudo systemctl start whatsapp-bridge whatsapp-bot`

---

## 🚀 Deployment Steps

### Step 1: Initial Setup

```bash
# Run automated setup
python setup.py

# Or manually:
pip install -r requirements.txt
npm install
cp sample_wa_config.py wa_config.py
# Edit wa_config.py with your settings
```

### Step 2: Start Services

#### Option A: Manual (Development)

```bash
# Terminal 1: Start Bridge
node whatsapp_bridge.js

# Terminal 2: Start Bot  
python whatsapp_bot.py
```

#### Option B: PM2 (Production)

```bash
# Install PM2
npm install -g pm2

# Start Bridge
pm2 start whatsapp_bridge.js --name whatsapp-bridge

# Start Bot
pm2 start whatsapp_bot.py --name whatsapp-bot --interpreter python3

# Save configuration
pm2 save

# Enable startup on boot
pm2 startup
```

#### Option C: Docker

```bash
docker-compose up -d
```

#### Option D: Systemd

```bash
sudo systemctl start whatsapp-bridge
sudo systemctl start whatsapp-bot
```

### Step 3: Authentication

1. Watch terminal output for QR code
2. Open WhatsApp on your phone
3. Go to Settings > Linked Devices > Link a Device
4. Scan the QR code displayed in terminal
5. Wait for "WhatsApp client is ready!" message

### Step 4: Verification

1. Send `/start` to the bot's WhatsApp
2. Verify bot responds
3. Add bot to a test group
4. Make bot an admin
5. Test commands: `/help`, `/info`
6. Test admin commands: `/warn`, `/mute` (reply to a message)

### Step 5: Monitoring

```bash
# If using PM2:
pm2 logs

# If using systemd:
sudo journalctl -fu whatsapp-bridge
sudo journalctl -fu whatsapp-bot

# If using Docker:
docker-compose logs -f
```

---

## 📊 Post-Deployment

### Daily Tasks

- [ ] Check bot is responding
- [ ] Monitor error logs
- [ ] Check database size (if SQLite)

### Weekly Tasks

- [ ] Review bot performance
- [ ] Check for updates
- [ ] Backup database
- [ ] Review user reports

### Monthly Tasks

- [ ] Update dependencies (if needed)
- [ ] Clean up old logs
- [ ] Review and update rules/filters
- [ ] Test backup restoration

---

## 🔧 Troubleshooting

### Bot Not Responding

1. Check if bridge is running: `curl http://localhost:3000/health`
2. Check if bot process is running
3. Review logs for errors
4. Verify WhatsApp is still connected (check phone)

### Authentication Failed

1. Delete `.wwebjs_auth/` folder
2. Restart bridge
3. Scan QR code again

### Database Errors

1. Check database server is running
2. Verify database URI in config
3. Check database user permissions
4. Review database logs

### High Memory Usage

1. Restart services periodically
2. Clear `.wwebjs_auth/` cache occasionally
3. Optimize database queries
4. Reduce number of loaded modules

---

## 📝 Maintenance Commands

### Check Status

```bash
# PM2
pm2 status

# Systemd
sudo systemctl status whatsapp-bridge whatsapp-bot

# Docker
docker-compose ps
```

### Restart Services

```bash
# PM2
pm2 restart all

# Systemd
sudo systemctl restart whatsapp-bridge whatsapp-bot

# Docker
docker-compose restart
```

### View Logs

```bash
# PM2
pm2 logs

# Systemd
sudo journalctl -u whatsapp-bridge -f

# Docker
docker-compose logs -f whatsapp-bot
```

### Update Bot

```bash
# Backup first!
cp wa_config.py wa_config.py.backup

# Update code
git pull  # or download new version

# Update dependencies
pip install -r requirements.txt
npm install

# Restart services
pm2 restart all  # or systemctl/docker-compose
```

### Backup

```bash
# Backup database
cp bot.db bot.db.backup  # SQLite
pg_dump dbname > backup.sql  # PostgreSQL

# Backup configuration
cp wa_config.py wa_config.py.backup

# Backup WhatsApp session
cp -r .wwebjs_auth .wwebjs_auth.backup
```

---

## ⚠️ Important Notes

### WhatsApp Terms of Service

- WhatsApp Web automation may violate WhatsApp ToS
- Use a dedicated phone number
- Don't use for spam or bulk messaging
- Risk of temporary or permanent ban
- Use at your own risk

### Best Practices

- Always backup before updates
- Test in private chat first
- Keep bot updated with security patches
- Monitor for unusual activity
- Respect user privacy
- Don't store sensitive user data
- Implement rate limiting for commands
- Use appropriate error handling

### Performance Tips

- Use PostgreSQL for production (not SQLite)
- Keep database optimized
- Limit number of active modules
- Use caching where appropriate
- Monitor memory and CPU usage
- Restart services periodically
- Clean up old data regularly

---

## 📞 Need Help?

1. Check documentation:
   - [SETUP.md](SETUP.md) - Technical setup
   - [QUICKSTART.md](QUICKSTART.md) - Quick reference
   - [USER_GUIDE.md](USER_GUIDE.md) - User instructions

2. Review logs for error messages

3. Check common issues in SETUP.md

4. Verify all checklist items completed

---

## ✅ Deployment Complete!

Once all items are checked and bot is running smoothly, your deployment is complete!

**Remember:**
- Keep bot updated
- Monitor regularly
- Backup frequently
- Follow best practices
- Use responsibly

Good luck with your WhatsApp bot! 🚀
