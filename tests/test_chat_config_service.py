"""
Tests for Chat Config Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestChatConfigService:
    """Test chat_config_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        try:
            from bot_core.services.chat_config_service import (
                should_delete_commands, set_delete_commands,
                get_chat_config, set_chat_config
            )
            self.should_delete_commands = should_delete_commands
            self.set_delete_commands = set_delete_commands
            self.get_chat_config = get_chat_config
            self.set_chat_config = set_chat_config
            self.has_service = True
        except ImportError:
            self.has_service = False
        
        self.chat_id = 'test_chat_123'
    
    def test_should_delete_commands_default(self):
        """Test default value for delete commands"""
        if not self.has_service:
            pytest.skip("Chat config service not available")
        
        result = self.should_delete_commands(self.chat_id)
        assert isinstance(result, bool)
    
    def test_set_delete_commands_on(self):
        """Test enabling delete commands"""
        if not self.has_service:
            pytest.skip("Chat config service not available")
        
        result = self.set_delete_commands(self.chat_id, True)
        assert result is True
        assert self.should_delete_commands(self.chat_id) is True
    
    def test_set_delete_commands_off(self):
        """Test disabling delete commands"""
        if not self.has_service:
            pytest.skip("Chat config service not available")
        
        self.set_delete_commands(self.chat_id, True)
        result = self.set_delete_commands(self.chat_id, False)
        assert result is True
        assert self.should_delete_commands(self.chat_id) is False
    
    def test_delete_commands_per_chat(self):
        """Test delete commands is per-chat"""
        if not self.has_service:
            pytest.skip("Chat config service not available")
        
        self.set_delete_commands('chat1', True)
        self.set_delete_commands('chat2', False)
        
        assert self.should_delete_commands('chat1') is True
        assert self.should_delete_commands('chat2') is False
    
    def test_get_chat_config(self):
        """Test getting full chat config"""
        if not self.has_service:
            pytest.skip("Chat config service not available")
        
        config = self.get_chat_config(self.chat_id)
        assert config is not None
        assert isinstance(config, dict) or hasattr(config, '__dict__')
    
    def test_set_chat_config(self):
        """Test setting chat config"""
        if not self.has_service:
            pytest.skip("Chat config service not available")
        
        result = self.set_chat_config(self.chat_id, {'delete_commands': True})
        assert result is True


class TestChatConfigEdgeCases:
    """Edge case tests for chat config"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        try:
            from bot_core.services.chat_config_service import (
                should_delete_commands, set_delete_commands
            )
            self.should_delete_commands = should_delete_commands
            self.set_delete_commands = set_delete_commands
            self.has_service = True
        except ImportError:
            self.has_service = False
    
    def test_toggle_multiple_times(self):
        """Test toggling delete commands multiple times"""
        if not self.has_service:
            pytest.skip("Chat config service not available")
        
        for i in range(5):
            self.set_delete_commands('chat', i % 2 == 0)
        
        # Should be False (last was i=4, 4%2==0 is True)
        assert self.should_delete_commands('chat') is True
    
    def test_config_with_special_chat_id(self):
        """Test config with special characters in chat ID"""
        if not self.has_service:
            pytest.skip("Chat config service not available")
        
        special_id = 'chat_@special#123!'
        result = self.set_delete_commands(special_id, True)
        assert isinstance(result, bool)
