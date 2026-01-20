"""
Tests for Welcome Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestWelcomeService:
    """Test welcome_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        from bot_core.services.welcome_service import (
            get_welcome_message, set_welcome_message, clear_welcome_message,
            format_welcome_message
        )
        self.get_welcome_message = get_welcome_message
        self.set_welcome_message = set_welcome_message
        self.clear_welcome_message = clear_welcome_message
        self.format_welcome_message = format_welcome_message
        self.chat_id = 'test_chat_123'
    
    def test_set_welcome_message(self):
        """Test setting welcome message"""
        message = "Welcome to the group, {name}!"
        result = self.set_welcome_message(self.chat_id, message)
        assert result is True
    
    def test_get_welcome_message_after_set(self):
        """Test getting welcome message after setting"""
        message = "Welcome to the group!"
        self.set_welcome_message(self.chat_id, message)
        retrieved = self.get_welcome_message(self.chat_id)
        assert retrieved == message
    
    def test_get_welcome_message_not_set(self):
        """Test getting welcome message when not set"""
        result = self.get_welcome_message('chat_without_welcome')
        # Should return None or default message
        assert result is None or isinstance(result, str)
    
    def test_update_welcome_message(self):
        """Test updating existing welcome message"""
        self.set_welcome_message(self.chat_id, "Old welcome")
        self.set_welcome_message(self.chat_id, "New welcome")
        result = self.get_welcome_message(self.chat_id)
        assert result == "New welcome"
    
    def test_clear_welcome_message(self):
        """Test clearing welcome message"""
        self.set_welcome_message(self.chat_id, "Welcome!")
        result = self.clear_welcome_message(self.chat_id)
        assert result is True
        
        msg = self.get_welcome_message(self.chat_id)
        assert msg is None or msg == ""
    
    def test_clear_welcome_not_set(self):
        """Test clearing welcome when not set"""
        result = self.clear_welcome_message('chat_without_welcome')
        # Should not raise error
        assert result in [True, False]
    
    def test_format_welcome_name(self):
        """Test formatting welcome message with name placeholder"""
        template = "Welcome, {name}!"
        formatted = self.format_welcome_message(
            template, 
            user_name="John",
            chat_name="Test Group",
            user_id="123"
        )
        assert "John" in formatted
    
    def test_format_welcome_chat(self):
        """Test formatting welcome message with chat placeholder"""
        template = "Welcome to {chat}!"
        formatted = self.format_welcome_message(
            template,
            user_name="John",
            chat_name="Test Group",
            user_id="123"
        )
        assert "Test Group" in formatted
    
    def test_format_welcome_user_id(self):
        """Test formatting welcome message with user ID placeholder"""
        template = "Welcome, user {id}!"
        formatted = self.format_welcome_message(
            template,
            user_name="John",
            chat_name="Test Group",
            user_id="12345"
        )
        assert "12345" in formatted
    
    def test_format_welcome_multiple_placeholders(self):
        """Test formatting with multiple placeholders"""
        template = "Hello {name}! Welcome to {chat}!"
        formatted = self.format_welcome_message(
            template,
            user_name="John",
            chat_name="My Group",
            user_id="123"
        )
        assert "John" in formatted
        assert "My Group" in formatted
    
    def test_format_welcome_no_placeholders(self):
        """Test formatting with no placeholders"""
        template = "Hello and welcome!"
        formatted = self.format_welcome_message(
            template,
            user_name="John",
            chat_name="Test Group",
            user_id="123"
        )
        assert formatted == template
    
    def test_welcome_different_chats(self):
        """Test welcome messages are per-chat"""
        self.set_welcome_message('chat1', "Welcome to chat 1!")
        self.set_welcome_message('chat2', "Welcome to chat 2!")
        
        assert "chat 1" in self.get_welcome_message('chat1')
        assert "chat 2" in self.get_welcome_message('chat2')


class TestWelcomeServiceEdgeCases:
    """Edge case tests for welcome service"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.welcome_service import (
            set_welcome_message, get_welcome_message, format_welcome_message
        )
        self.set_welcome_message = set_welcome_message
        self.get_welcome_message = get_welcome_message
        self.format_welcome_message = format_welcome_message
    
    def test_welcome_with_unicode(self):
        """Test welcome message with unicode"""
        message = "مرحبا {name}! 欢迎来到 {chat}! 🎉"
        self.set_welcome_message('chat', message)
        assert self.get_welcome_message('chat') == message
    
    def test_welcome_with_markdown(self):
        """Test welcome message with markdown"""
        message = "**Welcome**, _{name}_! Join `#general`"
        self.set_welcome_message('chat', message)
        assert self.get_welcome_message('chat') == message
    
    def test_welcome_very_long(self):
        """Test very long welcome message"""
        long_message = "Welcome! " * 100
        self.set_welcome_message('chat', long_message)
        assert self.get_welcome_message('chat') == long_message
    
    def test_welcome_empty_string(self):
        """Test setting empty string welcome"""
        self.set_welcome_message('chat', "")
        result = self.get_welcome_message('chat')
        assert result == "" or result is None
    
    def test_format_missing_placeholder_value(self):
        """Test formatting when placeholder value is missing"""
        template = "Welcome, {name}!"
        # If user_name is None or missing
        try:
            formatted = self.format_welcome_message(
                template,
                user_name=None,
                chat_name="Test",
                user_id="123"
            )
            assert isinstance(formatted, str)
        except (TypeError, KeyError):
            pass  # Expected behavior
    
    def test_format_invalid_placeholder(self):
        """Test formatting with invalid placeholder"""
        template = "Welcome, {invalid_placeholder}!"
        formatted = self.format_welcome_message(
            template,
            user_name="John",
            chat_name="Test",
            user_id="123"
        )
        # Should either keep the placeholder or handle gracefully
        assert isinstance(formatted, str)
    
    def test_welcome_with_newlines(self):
        """Test welcome message with multiple lines"""
        message = "Welcome!\n\nRules:\n1. Be nice\n2. No spam"
        self.set_welcome_message('chat', message)
        assert self.get_welcome_message('chat') == message
    
    def test_format_with_special_chars_in_name(self):
        """Test formatting with special chars in user name"""
        template = "Welcome, {name}!"
        formatted = self.format_welcome_message(
            template,
            user_name="<John>'s \"Account\" & More",
            chat_name="Test",
            user_id="123"
        )
        assert "John" in formatted


class TestGoodbyeService:
    """Tests for goodbye/farewell messages (Future Feature)"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for goodbye tests"""
        # Import when implemented
        self.chat_id = 'test_chat_123'
    
    @pytest.mark.skip(reason="Goodbye feature not yet implemented")
    def test_set_goodbye_message(self):
        """Test setting goodbye message"""
        pass
    
    @pytest.mark.skip(reason="Goodbye feature not yet implemented")
    def test_get_goodbye_message(self):
        """Test getting goodbye message"""
        pass
    
    @pytest.mark.skip(reason="Goodbye feature not yet implemented")
    def test_clear_goodbye_message(self):
        """Test clearing goodbye message"""
        pass
    
    @pytest.mark.skip(reason="Goodbye feature not yet implemented")
    def test_format_goodbye_message(self):
        """Test formatting goodbye message with placeholders"""
        pass
    
    @pytest.mark.skip(reason="Goodbye feature not yet implemented")
    def test_goodbye_toggle(self):
        """Test enabling/disabling goodbye messages"""
        pass
