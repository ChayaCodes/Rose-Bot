from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Dict, Any
from ..models import BotMessage, BotUser, BotChat


class BotAdapter(ABC):
    """
    Abstract base class for messaging platform adapters
    All messaging platforms (Telegram, WhatsApp, etc.) should implement this interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.handlers = {
            'message': [],
            'command': {},
            'callback': [],
            'error': []
        }
    
    @abstractmethod
    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
        reply_markup: Optional[Any] = None
    ) -> BotMessage:
        """Send a text message"""
        pass
    
    @abstractmethod
    def send_photo(
        self,
        chat_id: str,
        photo: Any,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> BotMessage:
        """Send a photo"""
        pass
    
    @abstractmethod
    def send_document(
        self,
        chat_id: str,
        document: Any,
        caption: Optional[str] = None
    ) -> BotMessage:
        """Send a document"""
        pass
    
    @abstractmethod
    def delete_message(
        self,
        chat_id: str,
        message_id: str
    ) -> bool:
        """Delete a message"""
        pass
    
    @abstractmethod
    def edit_message_text(
        self,
        chat_id: str,
        message_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Any] = None
    ) -> BotMessage:
        """Edit message text"""
        pass
    
    @abstractmethod
    def get_chat(self, chat_id: str) -> BotChat:
        """Get chat information"""
        pass
    
    @abstractmethod
    def get_chat_member(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Get chat member information"""
        pass
    
    @abstractmethod
    def ban_chat_member(
        self,
        chat_id: str,
        user_id: str,
        until_date: Optional[int] = None
    ) -> bool:
        """Ban a chat member"""
        pass
    
    @abstractmethod
    def unban_chat_member(
        self,
        chat_id: str,
        user_id: str
    ) -> bool:
        """Unban a chat member"""
        pass
    
    @abstractmethod
    def restrict_chat_member(
        self,
        chat_id: str,
        user_id: str,
        until_date: Optional[int] = None,
        **permissions
    ) -> bool:
        """Restrict a chat member"""
        pass
    
    @abstractmethod
    def promote_chat_member(
        self,
        chat_id: str,
        user_id: str,
        **permissions
    ) -> bool:
        """Promote a chat member"""
        pass
    
    @abstractmethod
    def pin_message(
        self,
        chat_id: str,
        message_id: str,
        disable_notification: bool = False
    ) -> bool:
        """Pin a message"""
        pass
    
    @abstractmethod
    def unpin_message(
        self,
        chat_id: str,
        message_id: Optional[str] = None
    ) -> bool:
        """Unpin a message"""
        pass
    
    # Handler registration methods
    def on_message(self, handler: Callable):
        """Register a message handler"""
        self.handlers['message'].append(handler)
        return handler
    
    def on_command(self, command: str, handler: Callable):
        """Register a command handler"""
        self.handlers['command'][command] = handler
        return handler
    
    def on_callback(self, handler: Callable):
        """Register a callback query handler"""
        self.handlers['callback'].append(handler)
        return handler
    
    def on_error(self, handler: Callable):
        """Register an error handler"""
        self.handlers['error'].append(handler)
        return handler
    
    @abstractmethod
    def start(self):
        """Start the bot"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the bot"""
        pass
    
    @abstractmethod
    def run(self):
        """Run the bot (blocking)"""
        pass
