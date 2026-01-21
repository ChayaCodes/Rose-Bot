from typing import Optional


class BotUser:
    """
    Abstract user model that works across different messaging platforms
    """
    def __init__(
        self,
        user_id: Optional[str] = None,
        first_name: str = "",
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        is_bot: bool = False,
        language_code: Optional[str] = None,
        *,
        name: Optional[str] = None,
        **kwargs
    ):
        legacy_id = kwargs.get('id')
        legacy_name = kwargs.get('name')
        self.id = user_id or legacy_id or ""
        effective_name = name or legacy_name
        if effective_name:
            self.first_name = effective_name
            self.last_name = None
        else:
            self.first_name = first_name
            self.last_name = last_name
        self.username = username
        self.is_bot = is_bot
        self.language_code = language_code

    @property
    def name(self) -> str:
        return self.full_name
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def mention(self) -> str:
        """Get a mention string for the user"""
        if self.username:
            return f"@{self.username}"
        return self.full_name
    
    def __repr__(self) -> str:
        return f"BotUser(id={self.id}, name={self.full_name})"
