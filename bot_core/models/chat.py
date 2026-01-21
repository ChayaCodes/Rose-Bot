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
        chat_id: Optional[str] = None,
        chat_type: ChatType = ChatType.PRIVATE,
        name: Optional[str] = None,
        title: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        legacy_id = kwargs.get('id')
        legacy_name = kwargs.get('name')
        is_group = kwargs.get('is_group')
        if is_group is True and chat_type == ChatType.PRIVATE:
            chat_type = ChatType.GROUP
        elif is_group is False and chat_type != ChatType.PRIVATE:
            chat_type = ChatType.PRIVATE
        self.id = chat_id or legacy_id or ""
        self.type = chat_type
        self.title = title or name or legacy_name
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

    @property
    def name(self) -> str:
        return self.display_name
    
    def __repr__(self) -> str:
        return f"BotChat(id={self.id}, type={self.type.value}, name={self.display_name})"
