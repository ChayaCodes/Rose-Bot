"""
Tests for Warn Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestWarnService:
    """Test warn_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        from bot_core.services.warn_service import (
            warn_user, get_user_warns, reset_user_warns,
            set_warn_limit, get_warn_limit, get_warn_settings
        )
        self.warn_user = warn_user
        self.get_user_warns = get_user_warns
        self.reset_user_warns = reset_user_warns
        self.set_warn_limit = set_warn_limit
        self.get_warn_limit = get_warn_limit
        self.get_warn_settings = get_warn_settings
        self.chat_id = 'test_chat_123'
        self.user_id = 'user_456'
        self.user_name = 'Test User'
    
    def test_warn_user_first_warning(self):
        """Test adding first warning to user"""
        count, limit = self.warn_user(self.chat_id, self.user_id, self.user_name, "spam")
        assert count == 1
        assert limit == 3  # Default limit
    
    def test_warn_user_multiple_warnings(self):
        """Test multiple warnings accumulate"""
        self.warn_user(self.chat_id, self.user_id, self.user_name, "spam")
        self.warn_user(self.chat_id, self.user_id, self.user_name, "offensive")
        count, limit = self.warn_user(self.chat_id, self.user_id, self.user_name, "third")
        assert count == 3
    
    def test_warn_user_reaches_limit(self):
        """Test warning count at limit"""
        for i in range(3):
            count, limit = self.warn_user(self.chat_id, self.user_id, self.user_name)
        assert count == 3
        assert count >= limit
    
    def test_get_user_warns_no_warnings(self):
        """Test getting warns for user with no warnings"""
        count, limit = self.get_user_warns(self.chat_id, 'new_user')
        assert count == 0
        assert limit == 3
    
    def test_get_user_warns_with_warnings(self):
        """Test getting warns after adding warnings"""
        self.warn_user(self.chat_id, self.user_id, self.user_name)
        self.warn_user(self.chat_id, self.user_id, self.user_name)
        count, limit = self.get_user_warns(self.chat_id, self.user_id)
        assert count == 2
    
    def test_reset_user_warns(self):
        """Test resetting user warnings"""
        self.warn_user(self.chat_id, self.user_id, self.user_name)
        self.warn_user(self.chat_id, self.user_id, self.user_name)
        
        old_count = self.reset_user_warns(self.chat_id, self.user_id)
        assert old_count == 2
        
        count, _ = self.get_user_warns(self.chat_id, self.user_id)
        assert count == 0
    
    def test_reset_warns_no_warnings(self):
        """Test resetting warns when user has no warnings"""
        old_count = self.reset_user_warns(self.chat_id, 'no_warns_user')
        assert old_count == 0
    
    def test_set_warn_limit(self):
        """Test setting custom warn limit"""
        self.set_warn_limit(self.chat_id, 5)
        limit = self.get_warn_limit(self.chat_id)
        assert limit == 5
    
    def test_set_warn_limit_updates_existing(self):
        """Test updating existing warn limit"""
        self.set_warn_limit(self.chat_id, 5)
        self.set_warn_limit(self.chat_id, 10)
        limit = self.get_warn_limit(self.chat_id)
        assert limit == 10
    
    def test_get_warn_limit_default(self):
        """Test default warn limit is 3"""
        limit = self.get_warn_limit('new_chat')
        assert limit == 3
    
    def test_get_warn_settings(self):
        """Test getting all warn settings"""
        self.set_warn_limit(self.chat_id, 7)
        limit, soft = self.get_warn_settings(self.chat_id)
        assert limit == 7
        assert isinstance(soft, bool)
    
    def test_warn_different_users(self):
        """Test warnings are per-user"""
        self.warn_user(self.chat_id, 'user1', 'User 1')
        self.warn_user(self.chat_id, 'user1', 'User 1')
        self.warn_user(self.chat_id, 'user2', 'User 2')
        
        count1, _ = self.get_user_warns(self.chat_id, 'user1')
        count2, _ = self.get_user_warns(self.chat_id, 'user2')
        
        assert count1 == 2
        assert count2 == 1
    
    def test_warn_different_chats(self):
        """Test warnings are per-chat"""
        self.warn_user('chat1', self.user_id, self.user_name)
        self.warn_user('chat1', self.user_id, self.user_name)
        self.warn_user('chat2', self.user_id, self.user_name)
        
        count1, _ = self.get_user_warns('chat1', self.user_id)
        count2, _ = self.get_user_warns('chat2', self.user_id)
        
        assert count1 == 2
        assert count2 == 1


class TestWarnServiceEdgeCases:
    """Edge case tests for warn service"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.warn_service import (
            warn_user, set_warn_limit, get_warn_limit
        )
        self.warn_user = warn_user
        self.set_warn_limit = set_warn_limit
        self.get_warn_limit = get_warn_limit
    
    def test_warn_with_empty_reason(self):
        """Test warning with empty reason"""
        count, limit = self.warn_user('chat', 'user', 'name', '')
        assert count == 1
    
    def test_warn_with_none_reason(self):
        """Test warning with None reason"""
        count, limit = self.warn_user('chat', 'user', 'name', None)
        assert count == 1
    
    def test_warn_with_long_reason(self):
        """Test warning with very long reason"""
        long_reason = 'x' * 1000
        count, limit = self.warn_user('chat', 'user', 'name', long_reason)
        assert count == 1
    
    def test_warn_with_special_characters(self):
        """Test warning with special characters in reason"""
        special_reason = "שלום 🎉 <script>alert('xss')</script>"
        count, limit = self.warn_user('chat', 'user', 'name', special_reason)
        assert count == 1
    
    def test_warn_limit_minimum(self):
        """Test setting warn limit to 1"""
        self.set_warn_limit('chat', 1)
        assert self.get_warn_limit('chat') == 1
    
    def test_warn_limit_large_number(self):
        """Test setting large warn limit"""
        self.set_warn_limit('chat', 100)
        assert self.get_warn_limit('chat') == 100
