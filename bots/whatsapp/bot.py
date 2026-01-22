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
from bot_core.database import init_db
from bot_core.shared_bot_logic import SharedBotLogic

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration
try:
    from wa_config import Development as Config
except ImportError:
    logger.error("Copy sample_wa_config.py to wa_config.py and configure it first!")
    sys.exit(1)


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

    def get_contact(self, contact_id: str):
        return self.client.get_contact(contact_id)

    def get_invite_link(self, chat_id: str):
        return self.client.get_invite_link(chat_id)

    def get_group_members(self, chat_id: str):
        return self.client.get_group_members(chat_id)

    def is_bot_owner(self, user_id: str) -> bool:
        """Check if user is the bot owner (from config)."""
        return user_id == self.owner_id

    def is_owner(self, chat_id: str, user_id: str) -> bool:
        """Check if user is the owner of the group (superadmin/creator)."""
        role = self.get_participant_role(chat_id, user_id)
        return role == 'superadmin' or self.is_bot_owner(user_id)

    def get_participant_role(self, chat_id: str, user_id: str) -> str:
        """Get participant's role in a group.
        
        Returns:
            'owner' - Bot owner
            'superadmin' - Group creator
            'admin' - Group admin
            'member' - Regular member
            'unknown' - Could not determine role
        """
        if self.is_bot_owner(user_id):
            return 'bot_owner'
        
        if not chat_id.endswith('@g.us'):
            return 'member'  # Not a group, no special roles
        
        members = self.get_group_members(chat_id)
        if not members:
            logger.warning(f"Could not get members for {chat_id}")
            return 'unknown'
        
        # Extract the identifier part (before @)
        user_identifier = user_id.split('@')[0] if user_id else ''
        is_lid_format = user_id.endswith('@lid')
        
        for member in members:
            member_id = member.get('id', '')
            member_identifier = member_id.split('@')[0] if member_id else ''
            member_lid = member.get('lid', '')
            member_lid_identifier = member_lid.split('@')[0] if member_lid else ''
            member_phone = member.get('phone', '')
            member_phone_identifier = member_phone.split('@')[0] if member_phone else ''
            
            # Check all possible matches:
            # 1. Direct ID match
            # 2. LID to LID match
            # 3. Phone to phone match
            # 4. User LID matches member's resolved LID
            matched = False
            
            if user_identifier == member_identifier:
                matched = True
            elif is_lid_format and member_lid_identifier and user_identifier == member_lid_identifier:
                matched = True
            elif not is_lid_format and member_phone_identifier and user_identifier == member_phone_identifier:
                matched = True
            elif is_lid_format and member_id.endswith('@lid') and user_identifier == member_identifier:
                matched = True
            
            if matched:
                is_super = member.get('isSuperAdmin', False)
                is_admin = member.get('isAdmin', False)
                if is_super:
                    return 'superadmin'
                if is_admin:
                    return 'admin'
                return 'member'
        
        logger.warning(f"User {user_id} not found in group members")
        return 'unknown'

    def is_admin(self, chat_id: str, user_id: str) -> bool:
        """Check if user is an admin (or higher) in the chat."""
        role = self.get_participant_role(chat_id, user_id)
        return role in ('bot_owner', 'superadmin', 'admin')

    def is_superadmin(self, chat_id: str, user_id: str) -> bool:
        """Check if user is the group creator (superadmin)."""
        role = self.get_participant_role(chat_id, user_id)
        return role in ('bot_owner', 'superadmin')

    def get_user_display(self, user_id: str) -> str:
        return user_id.split('@')[0] if user_id else ""

    def format_mention(self, user_id: str) -> str:
        return f"@{self.get_user_display(user_id)}"


class WhatsAppBot:
    def __init__(self):
        init_db()
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

        # Check bridge status
        if self.client.is_ready():
            logger.info("✅ WhatsApp Bridge is ready!")
            logger.info("Bot is running! Send /start to test")
        else:
            logger.error("❌ WhatsApp Bridge is not ready!")
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
