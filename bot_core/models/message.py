from typing import Optional, List, Any
from datetime import datetime
from .user import BotUser
from .chat import BotChat


class BotMessage:
    """
    Abstract message model that works across different messaging platforms
    """
    def __init__(
        self,
        message_id: str,
        chat: BotChat,
        sender: BotUser,
        text: Optional[str] = None,
        date: Optional[datetime] = None,
        reply_to_message: Optional['BotMessage'] = None,
        entities: Optional[List[Any]] = None,
        photo: Optional[List[Any]] = None,
        document: Optional[Any] = None,
        sticker: Optional[Any] = None,
        audio: Optional[Any] = None,
        video: Optional[Any] = None,
        voice: Optional[Any] = None,
        caption: Optional[str] = None,
        platform_message: Optional[Any] = None  # Store original platform-specific message
    ):
        self.message_id = message_id
        self.chat = chat
        self.sender = sender
        self.text = text
        self.date = date or datetime.now()
        self.reply_to_message = reply_to_message
        self.entities = entities or []
        self.photo = photo
        self.document = document
        self.sticker = sticker
        self.audio = audio
        self.video = video
        self.voice = voice
        self.caption = caption
        self.platform_message = platform_message
    
    @property
    def has_text(self) -> bool:
        """Check if message has text"""
        return bool(self.text)
    
    @property
    def has_media(self) -> bool:
        """Check if message has any media"""
        return any([self.photo, self.document, self.sticker, self.audio, self.video, self.voice])
    
    def get_command(self) -> Optional[tuple]:
        """
        Extract command from message
        Returns: (command, args) or None
        """
        if not self.text:
            return None
        
        parts = self.text.split(None, 1)
        if not parts or not parts[0].startswith(('/','!')):
            return None
        
        command = parts[0][1:].lower()  # Remove / or !
        args = parts[1] if len(parts) > 1 else ""
        
        return (command, args)
    
    def __repr__(self) -> str:
        return f"BotMessage(id={self.message_id}, from={self.sender.full_name}, text={self.text[:30] if self.text else 'None'})"
