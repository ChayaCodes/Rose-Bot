from typing import Optional, List, Any, Iterator
from datetime import datetime
from .user import BotUser
from .chat import BotChat, ChatType


class CommandData:
    """Command data returned from BotMessage parsing."""

    def __init__(self, command: str, args: str):
        self.command = command
        self.args = args

    def __iter__(self) -> Iterator[str]:
        yield self.command
        yield self.args

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.command == other
        if isinstance(other, CommandData):
            return self.command == other.command and self.args == other.args
        return False

    def __repr__(self) -> str:
        return f"CommandData(command={self.command}, args={self.args})"


class BotMessage:
    """
    Abstract message model that works across different messaging platforms
    """
    def __init__(
        self,
        message_id: Optional[str] = None,
        chat: Optional[BotChat] = None,
        sender: Optional[BotUser] = None,
        text: Optional[str] = None,
        date: Optional[datetime] = None,
        reply_to_message: Optional['BotMessage'] = None,
        reply_to_user_id: Optional[str] = None,
        entities: Optional[List[Any]] = None,
        photo: Optional[List[Any]] = None,
        document: Optional[Any] = None,
        sticker: Optional[Any] = None,
        audio: Optional[Any] = None,
        video: Optional[Any] = None,
        voice: Optional[Any] = None,
        caption: Optional[str] = None,
        platform_message: Optional[Any] = None,
        **kwargs
    ):
        legacy_id = kwargs.get('id')
        chat_id = kwargs.get('chat_id')
        user_id = kwargs.get('user_id')
        self.message_id = message_id or legacy_id or ""
        self.chat = chat or BotChat(chat_id or "", ChatType.PRIVATE)
        self.sender = sender or BotUser(user_id or "", "")
        self.text = text
        self.date = date or datetime.now()
        self.reply_to_message = reply_to_message
        self.reply_to_user_id = reply_to_user_id or kwargs.get('reply_to_user_id')
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
    
    def get_command(self) -> Optional[CommandData]:
        """Extract command name and args from message, if any."""
        if not self.text:
            return None

        parts = self.text.split(None, 1)
        if not parts or not parts[0].startswith(('/', '!')):
            return None

        command = parts[0][1:]
        if not command:
            return None
        if '@' in command:
            command = command.split('@', 1)[0]
        args = parts[1] if len(parts) > 1 else ""
        return CommandData(command.lower(), args)

    def get_command_data(self) -> Optional[tuple]:
        """Extract command name and args from message."""
        command_data = self.get_command()
        if not command_data:
            return None
        return (command_data.command, command_data.args)

    def is_command(self) -> bool:
        return self.get_command() is not None

    def get_args(self) -> str:
        command_data = self.get_command()
        if not command_data:
            return ""
        return command_data.args or ""

    def get_target_user(self) -> Optional[str]:
        args = self.get_args()
        for arg in args.split():
            if arg.startswith('@') and len(arg) > 1:
                return arg[1:]
        return self.reply_to_user_id

    @property
    def id(self) -> str:
        return self.message_id
    
    def __repr__(self) -> str:
        return f"BotMessage(id={self.message_id}, from={self.sender.full_name}, text={self.text[:30] if self.text else 'None'})"
