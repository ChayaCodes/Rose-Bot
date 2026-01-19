"""
WhatsApp Bot Configuration Example
Copy this file to wa_config.py and fill in your settings
"""

if not __name__.endswith("sample_wa_config"):
    import sys
    print("Copy this file to wa_config.py and configure it. Don't just rename it.", 
          file=sys.stderr)
    quit(1)


class WhatsAppConfig:
    """
    WhatsApp Bot Configuration
    """
    
    # REQUIRED
    OWNER_ID = "972XXXXXXXXX@c.us"  # Your WhatsApp ID (phone number with country code)
    OWNER_NAME = "Your Name"
    SESSION_NAME = "whatsapp-bot-session"  # Session name for storing login data
    
    # PLATFORM - Choose which platform to use
    PLATFORM = "whatsapp"  # Options: "telegram", "whatsapp"
    
    # For Telegram (if using telegram)
    TELEGRAM_TOKEN = None  # Your Telegram bot token
    
    # DATABASE (same as before)
    SQLALCHEMY_DATABASE_URI = 'sqldbtype://username:pw@hostname:port/db_name'
    MESSAGE_DUMP = None
    
    # MODULE LOADING
    LOAD = []
    NO_LOAD = ['translation', 'rss']
    
    # OPTIONAL
    SUDO_USERS = []  # List of WhatsApp IDs (phone numbers with @c.us)
    SUPPORT_USERS = []
    WHITELIST_USERS = []
    DONATION_LINK = None
    DEL_CMDS = False
    STRICT_GBAN = False
    WORKERS = 8
    
    # WhatsApp Specific
    WHATSAPP_QR_TERMINAL = True  # Display QR code in terminal for authentication
    WHATSAPP_HEADLESS = True  # Run in headless mode (no browser window)
    
    # Features to enable/disable
    ENABLE_STICKERS = True
    ENABLE_MEDIA = True
    ENABLE_VOICE = True


class Production(WhatsAppConfig):
    LOGGER = False


class Development(WhatsAppConfig):
    LOGGER = True
