from typing import Optional, Any, Dict, Callable
from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
from telegram.error import TelegramError
import logging

from ..base_adapter import BotAdapter
from ...models import BotMessage, BotUser, BotChat
from ...models.chat import ChatType

logger = logging.getLogger(__name__)


class TelegramAdapter(BotAdapter):
    """
    Telegram adapter implementation
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.token = config.get('token')
        if not self.token:
            raise ValueError("Telegram token is required")
        
        self.workers = config.get('workers', 8)
        self.updater = Updater(self.token, workers=self.workers)
        self.bot = self.updater.bot
        self.dispatcher = self.updater.dispatcher
        
        # Register internal handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register internal telegram handlers"""
        # Handle all messages
        self.dispatcher.add_handler(
            MessageHandler(Filters.all, self._handle_message)
        )
        
        # Handle callback queries
        self.dispatcher.add_handler(
            CallbackQueryHandler(self._handle_callback)
        )
        
        # Error handler
        self.dispatcher.add_error_handler(self._handle_error)
    
    def _convert_user(self, tg_user) -> BotUser:
        """Convert Telegram User to BotUser"""
        if not tg_user:
            return None
        
        return BotUser(
            user_id=str(tg_user.id),
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            username=tg_user.username,
            is_bot=tg_user.is_bot,
            language_code=tg_user.language_code
        )
    
    def _convert_chat(self, tg_chat) -> BotChat:
        """Convert Telegram Chat to BotChat"""
        if not tg_chat:
            return None
        
        # Map telegram chat types
        type_mapping = {
            'private': ChatType.PRIVATE,
            'group': ChatType.GROUP,
            'supergroup': ChatType.SUPERGROUP,
            'channel': ChatType.CHANNEL
        }
        
        chat_type = type_mapping.get(tg_chat.type, ChatType.PRIVATE)
        
        return BotChat(
            chat_id=str(tg_chat.id),
            chat_type=chat_type,
            title=tg_chat.title,
            username=tg_chat.username,
            first_name=tg_chat.first_name,
            last_name=tg_chat.last_name,
            description=tg_chat.description
        )
    
    def _convert_message(self, tg_message) -> BotMessage:
        """Convert Telegram Message to BotMessage"""
        if not tg_message:
            return None
        
        reply_to = None
        if tg_message.reply_to_message:
            reply_to = self._convert_message(tg_message.reply_to_message)
        
        return BotMessage(
            message_id=str(tg_message.message_id),
            chat=self._convert_chat(tg_message.chat),
            sender=self._convert_user(tg_message.from_user),
            text=tg_message.text,
            date=tg_message.date,
            reply_to_message=reply_to,
            entities=tg_message.entities,
            photo=tg_message.photo,
            document=tg_message.document,
            sticker=tg_message.sticker,
            audio=tg_message.audio,
            video=tg_message.video,
            voice=tg_message.voice,
            caption=tg_message.caption,
            platform_message=tg_message  # Store original message
        )
    
    def _handle_message(self, bot: Bot, update: Update):
        """Internal handler for all messages"""
        try:
            message = self._convert_message(update.effective_message)
            
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
            self._trigger_error_handlers(e, update)
    
    def _handle_callback(self, bot: Bot, update: Update):
        """Internal handler for callback queries"""
        try:
            for handler in self.handlers['callback']:
                handler(self, update.callback_query)
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            self._trigger_error_handlers(e, update)
    
    def _handle_error(self, bot: Bot, update: Update, error: Exception):
        """Internal error handler"""
        logger.error(f"Telegram error: {error}")
        self._trigger_error_handlers(error, update)
    
    def _trigger_error_handlers(self, error: Exception, update: Update = None):
        """Trigger registered error handlers"""
        for handler in self.handlers['error']:
            try:
                handler(self, error, update)
            except Exception as e:
                logger.error(f"Error in error handler: {e}")
    
    # Implement abstract methods
    
    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
        reply_markup: Optional[Any] = None
    ) -> BotMessage:
        """Send a text message"""
        try:
            tg_message = self.bot.send_message(
                chat_id=int(chat_id),
                text=text,
                parse_mode=parse_mode,
                reply_to_message_id=int(reply_to_message_id) if reply_to_message_id else None,
                reply_markup=reply_markup
            )
            return self._convert_message(tg_message)
        except TelegramError as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    def send_photo(
        self,
        chat_id: str,
        photo: Any,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> BotMessage:
        """Send a photo"""
        try:
            tg_message = self.bot.send_photo(
                chat_id=int(chat_id),
                photo=photo,
                caption=caption,
                parse_mode=parse_mode
            )
            return self._convert_message(tg_message)
        except TelegramError as e:
            logger.error(f"Error sending photo: {e}")
            raise
    
    def send_document(
        self,
        chat_id: str,
        document: Any,
        caption: Optional[str] = None
    ) -> BotMessage:
        """Send a document"""
        try:
            tg_message = self.bot.send_document(
                chat_id=int(chat_id),
                document=document,
                caption=caption
            )
            return self._convert_message(tg_message)
        except TelegramError as e:
            logger.error(f"Error sending document: {e}")
            raise
    
    def delete_message(
        self,
        chat_id: str,
        message_id: str
    ) -> bool:
        """Delete a message"""
        try:
            return self.bot.delete_message(
                chat_id=int(chat_id),
                message_id=int(message_id)
            )
        except TelegramError as e:
            logger.error(f"Error deleting message: {e}")
            return False
    
    def edit_message_text(
        self,
        chat_id: str,
        message_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Any] = None
    ) -> BotMessage:
        """Edit message text"""
        try:
            tg_message = self.bot.edit_message_text(
                chat_id=int(chat_id),
                message_id=int(message_id),
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
            return self._convert_message(tg_message)
        except TelegramError as e:
            logger.error(f"Error editing message: {e}")
            raise
    
    def get_chat(self, chat_id: str) -> BotChat:
        """Get chat information"""
        try:
            tg_chat = self.bot.get_chat(chat_id=int(chat_id))
            return self._convert_chat(tg_chat)
        except TelegramError as e:
            logger.error(f"Error getting chat: {e}")
            raise
    
    def get_chat_member(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Get chat member information"""
        try:
            member = self.bot.get_chat_member(
                chat_id=int(chat_id),
                user_id=int(user_id)
            )
            return {
                'user': self._convert_user(member.user),
                'status': member.status,
                'can_change_info': getattr(member, 'can_change_info', False),
                'can_delete_messages': getattr(member, 'can_delete_messages', False),
                'can_invite_users': getattr(member, 'can_invite_users', False),
                'can_restrict_members': getattr(member, 'can_restrict_members', False),
                'can_pin_messages': getattr(member, 'can_pin_messages', False),
                'can_promote_members': getattr(member, 'can_promote_members', False),
            }
        except TelegramError as e:
            logger.error(f"Error getting chat member: {e}")
            raise
    
    def ban_chat_member(
        self,
        chat_id: str,
        user_id: str,
        until_date: Optional[int] = None
    ) -> bool:
        """Ban a chat member"""
        try:
            return self.bot.kick_chat_member(
                chat_id=int(chat_id),
                user_id=int(user_id),
                until_date=until_date
            )
        except TelegramError as e:
            logger.error(f"Error banning chat member: {e}")
            return False
    
    def unban_chat_member(
        self,
        chat_id: str,
        user_id: str
    ) -> bool:
        """Unban a chat member"""
        try:
            return self.bot.unban_chat_member(
                chat_id=int(chat_id),
                user_id=int(user_id)
            )
        except TelegramError as e:
            logger.error(f"Error unbanning chat member: {e}")
            return False
    
    def restrict_chat_member(
        self,
        chat_id: str,
        user_id: str,
        until_date: Optional[int] = None,
        **permissions
    ) -> bool:
        """Restrict a chat member"""
        try:
            return self.bot.restrict_chat_member(
                chat_id=int(chat_id),
                user_id=int(user_id),
                until_date=until_date,
                **permissions
            )
        except TelegramError as e:
            logger.error(f"Error restricting chat member: {e}")
            return False
    
    def promote_chat_member(
        self,
        chat_id: str,
        user_id: str,
        **permissions
    ) -> bool:
        """Promote a chat member"""
        try:
            return self.bot.promote_chat_member(
                chat_id=int(chat_id),
                user_id=int(user_id),
                **permissions
            )
        except TelegramError as e:
            logger.error(f"Error promoting chat member: {e}")
            return False
    
    def pin_message(
        self,
        chat_id: str,
        message_id: str,
        disable_notification: bool = False
    ) -> bool:
        """Pin a message"""
        try:
            return self.bot.pin_chat_message(
                chat_id=int(chat_id),
                message_id=int(message_id),
                disable_notification=disable_notification
            )
        except TelegramError as e:
            logger.error(f"Error pinning message: {e}")
            return False
    
    def unpin_message(
        self,
        chat_id: str,
        message_id: Optional[str] = None
    ) -> bool:
        """Unpin a message"""
        try:
            return self.bot.unpin_chat_message(
                chat_id=int(chat_id),
                message_id=int(message_id) if message_id else None
            )
        except TelegramError as e:
            logger.error(f"Error unpinning message: {e}")
            return False
    
    def start(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        self.updater.start_polling()
    
    def stop(self):
        """Stop the bot"""
        logger.info("Stopping Telegram bot...")
        self.updater.stop()
    
    def run(self):
        """Run the bot (blocking)"""
        logger.info("Running Telegram bot...")
        self.updater.start_polling()
        self.updater.idle()
