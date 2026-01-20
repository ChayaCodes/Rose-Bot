"""
Full-Featured WhatsApp Bot with Group Management
Includes: Warns, Bans, Rules, Welcome, Blacklist, Locks, Anti-flood
"""

import logging
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
from bot_core.shared_bot_logic import SharedBotLogic

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration - support both file-based and environment variables
class EnvConfig:
    """Configuration from environment variables for production"""
    OWNER_ID = os.environ.get("OWNER_ID", "")
    OWNER_NAME = os.environ.get("OWNER_NAME", "Bot Owner")
    SESSION_NAME = os.environ.get("SESSION_NAME", "whatsapp-bot-session")
    PLATFORM = "whatsapp"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///whatsapp_bot.db")
    MESSAGE_DUMP = None
    LOAD = []
    NO_LOAD = ['translation', 'rss']
    SUDO_USERS = []
    SUPPORT_USERS = []
    WHITELIST_USERS = []
    DONATION_LINK = None
    DEL_CMDS = False
    STRICT_GBAN = False
    WORKERS = 8
    WHATSAPP_QR_TERMINAL = True
    WHATSAPP_HEADLESS = True

try:
    from wa_config import Development as Config
except ImportError:
    # Use environment variables in production
    logger.info("Using environment variables for configuration")
    Config = EnvConfig


class WhatsAppActions:
    def __init__(self, client: WhatsAppBridgeClient, owner_id: str):
        self.client = client
        self.owner_id = owner_id

    def send_message(self, chat_id: str, text: str):
        return self.client.send_message(chat_id, text)

    def delete_message(self, chat_id: str, message_id: str):
        return self.client.delete_message(chat_id, message_id)

    def remove_participant(self, chat_id: str, user_id: str) -> bool:
        return self.client.remove_participant(chat_id, user_id)

    def add_participants(self, chat_id: str, participants):
        return self.client.add_participants(chat_id, participants)

    def get_invite_link(self, chat_id: str):
        return self.client.get_invite_link(chat_id)

    def is_owner(self, user_id: str) -> bool:
        return user_id == self.owner_id

    def is_admin(self, chat_id: str, user_id: str) -> bool:
        if self.is_owner(user_id):
            return True
        if chat_id.endswith('@g.us'):
            return True
        return False

    def get_user_display(self, user_id: str) -> str:
        return user_id.split('@')[0] if user_id else ""

    def format_mention(self, user_id: str) -> str:
        return f"@{self.get_user_display(user_id)}"


class WhatsAppBot:
    def __init__(self):
        self.client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000",
            callback_port=5000
        )
        self.actions = WhatsAppActions(self.client, Config.OWNER_ID)
        self.logic = SharedBotLogic(self.actions)

    def run(self):
        """Start the bot"""
        logger.info("Starting WhatsApp Bot...")
        logger.info(f"Owner: {Config.OWNER_ID}")

        # Register message handler
        self.client.on_message(self.logic.handle_message)

        # Register group join handler for welcome messages
        self.client.on_group_join(self.logic.handle_group_join)

        # Start callback server
        logger.info("Starting callback server on port 5000...")
        self.client.start_callback_server()

        # Wait for bridge to be ready (may take time for Chromium to start)
        max_wait = 300  # 5 minutes max wait
        wait_interval = 5  # Check every 5 seconds
        waited = 0
        
        logger.info("Waiting for WhatsApp Bridge to be ready...")
        while waited < max_wait:
            if self.client.is_ready():
                logger.info("✅ WhatsApp Bridge is ready!")
                logger.info("Bot is running! Send /start to test")
                break
            logger.info(f"Bridge not ready yet, waiting... ({waited}s / {max_wait}s)")
            time.sleep(wait_interval)
            waited += wait_interval
        else:
            logger.error(f"❌ WhatsApp Bridge not ready after {max_wait} seconds!")
            logger.error("Please check bridge logs and try again")
            return

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nBot stopped by user")


def main():
    """Main entry point"""
    try:
        bot = WhatsAppBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
