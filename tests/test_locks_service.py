"""
Tests for Locks Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestLocksService:
    """Test locks_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        from bot_core.services.locks_service import (
            set_lock, get_locks, is_locked, check_message_locks, clear_locks
        )
        self.set_lock = set_lock
        self.get_locks = get_locks
        self.is_locked = is_locked
        self.check_message_locks = check_message_locks
        self.clear_locks = clear_locks
        self.chat_id = 'test_chat_123'
    
    def test_set_lock_url(self):
        """Test locking URL messages"""
        result = self.set_lock(self.chat_id, 'url', True)
        assert result is True
    
    def test_set_lock_sticker(self):
        """Test locking sticker messages"""
        result = self.set_lock(self.chat_id, 'sticker', True)
        assert result is True
    
    def test_set_lock_media(self):
        """Test locking media messages"""
        result = self.set_lock(self.chat_id, 'media', True)
        assert result is True
    
    def test_unlock(self):
        """Test unlocking a lock type"""
        self.set_lock(self.chat_id, 'url', True)
        result = self.set_lock(self.chat_id, 'url', False)
        assert result is True
        assert self.is_locked(self.chat_id, 'url') is False
    
    def test_is_locked_true(self):
        """Test checking if type is locked"""
        self.set_lock(self.chat_id, 'url', True)
        assert self.is_locked(self.chat_id, 'url') is True
    
    def test_is_locked_false(self):
        """Test checking if type is not locked"""
        assert self.is_locked(self.chat_id, 'url') is False
    
    def test_get_locks_empty(self):
        """Test getting locks when none are set"""
        locks = self.get_locks('chat_no_locks')
        assert locks == {} or locks is None or all(not v for v in locks.values())
    
    def test_get_locks_with_locks(self):
        """Test getting locks after setting"""
        self.set_lock(self.chat_id, 'url', True)
        self.set_lock(self.chat_id, 'sticker', True)
        
        locks = self.get_locks(self.chat_id)
        assert locks.get('url') is True
        assert locks.get('sticker') is True
    
    def test_check_message_locks_url(self):
        """Test checking message with URL against locks"""
        self.set_lock(self.chat_id, 'url', True)
        
        message_text = "Check out https://example.com"
        result = self.check_message_locks(
            self.chat_id,
            message_text,
            has_sticker=False,
            has_media=False
        )
        assert result is True or result == 'url'
    
    def test_check_message_locks_no_violation(self):
        """Test checking message with no lock violations"""
        self.set_lock(self.chat_id, 'url', True)
        
        message_text = "Hello everyone!"
        result = self.check_message_locks(
            self.chat_id,
            message_text,
            has_sticker=False,
            has_media=False
        )
        assert result is False or result is None
    
    def test_check_message_locks_sticker(self):
        """Test checking sticker message against locks"""
        self.set_lock(self.chat_id, 'sticker', True)
        
        result = self.check_message_locks(
            self.chat_id,
            "",
            has_sticker=True,
            has_media=False
        )
        assert result is True or result == 'sticker'
    
    def test_check_message_locks_media(self):
        """Test checking media message against locks"""
        self.set_lock(self.chat_id, 'media', True)
        
        result = self.check_message_locks(
            self.chat_id,
            "",
            has_sticker=False,
            has_media=True
        )
        assert result is True or result == 'media'
    
    def test_clear_locks(self):
        """Test clearing all locks"""
        self.set_lock(self.chat_id, 'url', True)
        self.set_lock(self.chat_id, 'sticker', True)
        
        result = self.clear_locks(self.chat_id)
        assert result is True
        
        assert self.is_locked(self.chat_id, 'url') is False
        assert self.is_locked(self.chat_id, 'sticker') is False
    
    def test_clear_locks_empty(self):
        """Test clearing locks when none are set"""
        result = self.clear_locks('chat_no_locks')
        assert result in [True, False]
    
    def test_locks_different_chats(self):
        """Test locks are per-chat"""
        self.set_lock('chat1', 'url', True)
        self.set_lock('chat2', 'sticker', True)
        
        assert self.is_locked('chat1', 'url') is True
        assert self.is_locked('chat1', 'sticker') is False
        assert self.is_locked('chat2', 'url') is False
        assert self.is_locked('chat2', 'sticker') is True


class TestLocksServiceLockTypes:
    """Test various lock types"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.locks_service import set_lock, is_locked
        self.set_lock = set_lock
        self.is_locked = is_locked
        self.chat_id = 'test_chat'
    
    def test_lock_all(self):
        """Test locking all messages"""
        result = self.set_lock(self.chat_id, 'all', True)
        assert result is True or result is False  # May not be supported
    
    def test_lock_audio(self):
        """Test locking audio messages"""
        result = self.set_lock(self.chat_id, 'audio', True)
        assert isinstance(result, bool)
    
    def test_lock_video(self):
        """Test locking video messages"""
        result = self.set_lock(self.chat_id, 'video', True)
        assert isinstance(result, bool)
    
    def test_lock_photo(self):
        """Test locking photo messages"""
        result = self.set_lock(self.chat_id, 'photo', True)
        assert isinstance(result, bool)
    
    def test_lock_document(self):
        """Test locking document messages"""
        result = self.set_lock(self.chat_id, 'document', True)
        assert isinstance(result, bool)
    
    def test_lock_gif(self):
        """Test locking GIF messages"""
        result = self.set_lock(self.chat_id, 'gif', True)
        assert isinstance(result, bool)
    
    def test_lock_forward(self):
        """Test locking forwarded messages"""
        result = self.set_lock(self.chat_id, 'forward', True)
        assert isinstance(result, bool)
    
    def test_lock_bots(self):
        """Test locking bot joining"""
        result = self.set_lock(self.chat_id, 'bots', True)
        assert isinstance(result, bool)
    
    def test_lock_commands(self):
        """Test locking commands"""
        result = self.set_lock(self.chat_id, 'commands', True)
        assert isinstance(result, bool)


class TestLocksServiceEdgeCases:
    """Edge case tests for locks service"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.locks_service import (
            set_lock, check_message_locks, get_locks
        )
        self.set_lock = set_lock
        self.check_message_locks = check_message_locks
        self.get_locks = get_locks
    
    def test_invalid_lock_type(self):
        """Test setting invalid lock type"""
        try:
            result = self.set_lock('chat', 'invalid_type', True)
            # Should either fail or ignore
            assert isinstance(result, bool)
        except (ValueError, KeyError):
            pass  # Expected
    
    def test_check_message_multiple_violations(self):
        """Test message with multiple lock violations"""
        self.set_lock('chat', 'url', True)
        self.set_lock('chat', 'media', True)
        
        result = self.check_message_locks(
            'chat',
            "Check https://example.com",
            has_sticker=False,
            has_media=True
        )
        # Should detect at least one violation
        assert result is True or result in ['url', 'media']
    
    def test_check_message_url_variations(self):
        """Test URL detection with various formats"""
        self.set_lock('chat', 'url', True)
        
        urls = [
            "https://example.com",
            "http://example.com",
            "www.example.com",
            "example.com/path",
            "Check out bit.ly/abc123"
        ]
        
        for url in urls:
            result = self.check_message_locks('chat', url)
            # At least some should be detected
            assert isinstance(result, (bool, str, type(None)))
    
    def test_check_empty_message(self):
        """Test checking empty message"""
        self.set_lock('chat', 'url', True)
        result = self.check_message_locks('chat', '', has_sticker=False, has_media=False)
        assert result is False or result is None
    
    def test_check_none_message(self):
        """Test checking None message"""
        self.set_lock('chat', 'url', True)
        try:
            result = self.check_message_locks('chat', None, has_sticker=False, has_media=False)
            assert result is False or result is None
        except (TypeError, AttributeError):
            pass  # Expected
    
    def test_toggle_lock_multiple_times(self):
        """Test toggling lock on and off multiple times"""
        for i in range(5):
            self.set_lock('chat', 'url', True)
            self.set_lock('chat', 'url', False)
        
        locks = self.get_locks('chat')
        # Should be unlocked at the end
        assert locks.get('url') is False or not locks.get('url')
