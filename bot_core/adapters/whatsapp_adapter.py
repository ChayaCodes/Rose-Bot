from typing import Optional, Any, Dict
import logging
from datetime import datetime

try:
    # WhatsApp integration using yowsup or other libraries
    # For now, creating a placeholder that can be implemented
    WHATSAPP_AVAILABLE = False
except ImportError:
    WHATSAPP_AVAILABLE = False

from .base_adapter import BotAdapter
from ..models import BotMessage, BotUser, BotChat
from ..models.chat import ChatType

logger = logging.getLogger(__name__)


class WhatsAppAdapter(BotAdapter):
    """
    WhatsApp adapter implementation
    
    This adapter requires whatsapp-web.js or similar library
    Install: npm install whatsapp-web.js
    
    Note: This implementation requires a Node.js bridge or Python wrapper
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        if not WHATSAPP_AVAILABLE:
            logger.warning("WhatsApp library not available. Install whatsapp-web.js or yowsup")
        
        self.session_name = config.get('session_name', 'whatsapp-session')
        self.qr_callback = config.get('qr_callback', None)
        self.client = None
        self._running = False
        
        # Initialize WhatsApp client
        self._init_client()
    
    def _init_client(self):
        """Initialize WhatsApp client"""
        # This is a placeholder. Actual implementation requires:
        # 1. Node.js process running whatsapp-web.js
        # 2. Python bridge to communicate with Node process
        # 3. Or use yowsup library for Python (less stable)
        
        logger.info("Initializing WhatsApp client...")
        logger.info("To implement: Use whatsapp-web.js with Node bridge or yowsup")
        
        # Placeholder for client initialization
        # self.client = WhatsAppClient(session_name=self.session_name)
        pass
    
    def _convert_wa_user(self, wa_contact) -> BotUser:
        """Convert WhatsApp contact to BotUser"""
        # WhatsApp format: phone number is the ID
        return BotUser(
            user_id=wa_contact.get('id', ''),
            first_name=wa_contact.get('name', wa_contact.get('pushname', 'Unknown')),
            last_name=None,
            username=None,
            is_bot=False,
            language_code=None
        )
    
    def _convert_wa_chat(self, wa_chat) -> BotChat:
        """Convert WhatsApp chat to BotChat"""
        # Determine chat type based on WhatsApp ID format
        chat_id = wa_chat.get('id', '')
        is_group = '@g.us' in chat_id  # Group chats end with @g.us
        
        chat_type = ChatType.GROUP if is_group else ChatType.PRIVATE
        
        return BotChat(
            chat_id=chat_id,
            chat_type=chat_type,
            title=wa_chat.get('name') if is_group else None,
            username=None,
            first_name=wa_chat.get('name') if not is_group else None,
            last_name=None,
            description=wa_chat.get('description')
        )

    @staticmethod
    def is_group_chat_id(chat_id: str) -> bool:
        """Check if WhatsApp ID is a group"""
        return chat_id.endswith('@g.us')

    @staticmethod
    def is_private_chat_id(chat_id: str) -> bool:
        """Check if WhatsApp ID is a private chat"""
        return chat_id.endswith('@s.whatsapp.net')

    @staticmethod
    def normalize_phone(phone_number: str) -> str:
        """Normalize phone number to digits only"""
        return ''.join(ch for ch in phone_number if ch.isdigit())

    @staticmethod
    def normalize_user_id(user: str) -> str:
        """Normalize to WhatsApp user ID format (xxx@s.whatsapp.net)"""
        if user.endswith('@s.whatsapp.net'):
            return user
        digits = WhatsAppAdapter.normalize_phone(user)
        return f"{digits}@s.whatsapp.net"

    @staticmethod
    def normalize_group_id(group: str) -> str:
        """Normalize to WhatsApp group ID format (xxx@g.us)"""
        if group.endswith('@g.us'):
            return group
        digits = WhatsAppAdapter.normalize_phone(group)
        return f"{digits}@g.us"

    @staticmethod
    def format_mention(user_id: str) -> str:
        """Format a WhatsApp mention string from user ID or phone"""
        normalized = WhatsAppAdapter.normalize_user_id(user_id)
        phone = normalized.split('@')[0]
        return f"@{phone}"
    
    def _convert_wa_message(self, wa_msg) -> BotMessage:
        """Convert WhatsApp message to BotMessage"""
        return BotMessage(
            message_id=wa_msg.get('id', ''),
            chat=self._convert_wa_chat(wa_msg.get('chat', {})),
            sender=self._convert_wa_user(wa_msg.get('from', {})),
            text=wa_msg.get('body'),
            date=datetime.fromtimestamp(wa_msg.get('timestamp', 0)),
            reply_to_message=None,  # TODO: Handle quoted messages
            entities=[],
            photo=None,  # TODO: Handle media
            document=None,
            sticker=None,
            audio=None,
            video=None,
            voice=None,
            caption=wa_msg.get('caption'),
            platform_message=wa_msg
        )
    
    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
        reply_markup: Optional[Any] = None
    ) -> BotMessage:
        """Send a text message"""
        if not self.client:
            raise RuntimeError("WhatsApp client not initialized")
        
        logger.info(f"Sending message to {chat_id}: {text[:50]}")
        
        # Format text based on parse_mode
        formatted_text = text
        if parse_mode == "Markdown":
            # Convert markdown to WhatsApp format
            formatted_text = self._markdown_to_whatsapp(text)
        
        # TODO: Implement actual message sending
        # result = self.client.send_message(chat_id, formatted_text)
        
        # Return placeholder
        return BotMessage(
            message_id="temp_id",
            chat=BotChat(chat_id, ChatType.PRIVATE),
            sender=BotUser("bot", "Bot"),
            text=text,
            date=datetime.now()
        )
    
    def _markdown_to_whatsapp(self, text: str) -> str:
        """Convert markdown to WhatsApp formatting"""
        # WhatsApp uses: *bold*, _italic_, ~strikethrough~, ```monospace```
        # Basic conversion (can be enhanced)
        import re
        
        # Bold: **text** or __text__ -> *text*
        text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
        text = re.sub(r'__(.+?)__', r'*\1*', text)
        
        # Italic: *text* or _text_ -> _text_
        # (already compatible, but handle conflicts)
        
        # Code: `text` -> ```text```
        text = re.sub(r'`(.+?)`', r'```\1```', text)
        
        return text
    
    def send_photo(
        self,
        chat_id: str,
        photo: Any,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> BotMessage:
        """Send a photo"""
        if not self.client:
            raise RuntimeError("WhatsApp client not initialized")
        
        logger.info(f"Sending photo to {chat_id}")
        
        # TODO: Implement actual photo sending
        # result = self.client.send_image(chat_id, photo, caption)
        
        return BotMessage(
            message_id="temp_id",
            chat=BotChat(chat_id, ChatType.PRIVATE),
            sender=BotUser("bot", "Bot"),
            caption=caption,
            date=datetime.now()
        )
    
    def send_document(
        self,
        chat_id: str,
        document: Any,
        caption: Optional[str] = None
    ) -> BotMessage:
        """Send a document"""
        if not self.client:
            raise RuntimeError("WhatsApp client not initialized")
        
        logger.info(f"Sending document to {chat_id}")
        
        # TODO: Implement actual document sending
        # result = self.client.send_document(chat_id, document, caption)
        
        return BotMessage(
            message_id="temp_id",
            chat=BotChat(chat_id, ChatType.PRIVATE),
            sender=BotUser("bot", "Bot"),
            caption=caption,
            date=datetime.now()
        )
    
    def delete_message(
        self,
        chat_id: str,
        message_id: str
    ) -> bool:
        """Delete a message"""
        if not self.client:
            return False
        
        logger.info(f"Deleting message {message_id} from {chat_id}")
        
        # TODO: Implement message deletion
        # WhatsApp has limited delete capabilities
        # return self.client.delete_message(message_id)
        
        return False
    
    def edit_message_text(
        self,
        chat_id: str,
        message_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Any] = None
    ) -> BotMessage:
        """Edit message text - NOT SUPPORTED in WhatsApp"""
        logger.warning("WhatsApp does not support message editing")
        raise NotImplementedError("WhatsApp does not support editing messages")
    
    def get_chat(self, chat_id: str) -> BotChat:
        """Get chat information"""
        if not self.client:
            raise RuntimeError("WhatsApp client not initialized")
        
        # TODO: Implement
        # chat_info = self.client.get_chat(chat_id)
        # return self._convert_wa_chat(chat_info)
        
        return BotChat(chat_id, ChatType.PRIVATE)
    
    def get_chat_member(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Get chat member information"""
        if not self.client:
            raise RuntimeError("WhatsApp client not initialized")
        
        # TODO: Implement for group chats
        # member_info = self.client.get_group_member(chat_id, user_id)
        
        return {
            'user': BotUser(user_id, "Unknown"),
            'status': 'member',
            'can_change_info': False,
            'can_delete_messages': False,
            'can_invite_users': False,
            'can_restrict_members': False,
            'can_pin_messages': False,
            'can_promote_members': False,
        }
    
    def ban_chat_member(
        self,
        chat_id: str,
        user_id: str,
        until_date: Optional[int] = None
    ) -> bool:
        """Ban a chat member (remove from group)"""
        if not self.client:
            return False
        
        logger.info(f"Removing {user_id} from {chat_id}")
        
        # TODO: Implement
        # return self.client.remove_participant(chat_id, user_id)
        
        return False
    
    def unban_chat_member(
        self,
        chat_id: str,
        user_id: str
    ) -> bool:
        """Unban a chat member - WhatsApp doesn't have ban/unban"""
        logger.warning("WhatsApp doesn't have ban/unban, only remove from group")
        return False
    
    def restrict_chat_member(
        self,
        chat_id: str,
        user_id: str,
        until_date: Optional[int] = None,
        **permissions
    ) -> bool:
        """Restrict a chat member - Limited in WhatsApp"""
        logger.warning("WhatsApp has limited restriction capabilities")
        return False
    
    def promote_chat_member(
        self,
        chat_id: str,
        user_id: str,
        **permissions
    ) -> bool:
        """Promote a chat member to admin"""
        if not self.client:
            return False
        
        logger.info(f"Promoting {user_id} in {chat_id}")
        
        # TODO: Implement
        # return self.client.promote_participant(chat_id, user_id)
        
        return False
    
    def pin_message(
        self,
        chat_id: str,
        message_id: str,
        disable_notification: bool = False
    ) -> bool:
        """Pin a message - NOT SUPPORTED in WhatsApp"""
        logger.warning("WhatsApp does not support pinning messages")
        return False
    
    def unpin_message(
        self,
        chat_id: str,
        message_id: Optional[str] = None
    ) -> bool:
        """Unpin a message - NOT SUPPORTED in WhatsApp"""
        logger.warning("WhatsApp does not support unpinning messages")
        return False
    
    def start(self):
        """Start the bot"""
        logger.info("Starting WhatsApp bot...")
        self._running = True
        
        # TODO: Start listening for messages
        # self.client.on('message', self._handle_message)
        # self.client.on('qr', self._handle_qr)
        # self.client.initialize()
    
    def stop(self):
        """Stop the bot"""
        logger.info("Stopping WhatsApp bot...")
        self._running = False
        
        # TODO: Stop client
        # if self.client:
        #     self.client.destroy()
    
    def run(self):
        """Run the bot (blocking)"""
        logger.info("Running WhatsApp bot...")
        self.start()
        
        # Keep running
        try:
            while self._running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def _handle_qr(self, qr_code: str):
        """Handle QR code for authentication"""
        logger.info("QR Code received for WhatsApp authentication")
        if self.qr_callback:
            self.qr_callback(qr_code)
        else:
            # Print QR to terminal
            try:
                import qrcode
                qr = qrcode.QRCode()
                qr.add_data(qr_code)
                qr.print_ascii()
            except ImportError:
                logger.error("Install qrcode library to display QR: pip install qrcode")
                logger.info(f"QR Code: {qr_code}")
    
    def _handle_message(self, wa_msg):
        """Handle incoming WhatsApp message"""
        try:
            message = self._convert_wa_message(wa_msg)
            
            # Check if it's a command
            command_data = message.get_command()
            if command_data:
                command, args = command_data
                if command in self.handlers['command']:
                    handler = self.handlers['command'][command]
                    handler(self, message, args)
                    return
            
            # Call general message handlers
            for handler in self.handlers['message']:
                handler(self, message)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            for error_handler in self.handlers['error']:
                try:
                    error_handler(self, e, wa_msg)
                except:
                    pass
