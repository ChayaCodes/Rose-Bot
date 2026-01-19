from typing import Optional
from enum import Enum


class ChatType(Enum):
    """Type of chat"""
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class BotChat:
    """
    Abstract chat model that works across different messaging platforms
    """
    def __init__(
        self,
        chat_id: str,
        chat_type: ChatType,
        title: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.id = chat_id
        self.type = chat_type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.description = description
    
    @property
    def is_private(self) -> bool:
        """Check if chat is private"""
        return self.type == ChatType.PRIVATE
    
    @property
    def is_group(self) -> bool:
        """Check if chat is a group"""
        return self.type in [ChatType.GROUP, ChatType.SUPERGROUP]
    
    @property
    def display_name(self) -> str:
        """Get displayable name for the chat"""
        if self.title:
            return self.title
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name}"
            return self.first_name
        if self.username:
            return f"@{self.username}"
        return f"Chat {self.id}"
    
    def __repr__(self) -> str:
        return f"BotChat(id={self.id}, type={self.type.value}, name={self.display_name})"
