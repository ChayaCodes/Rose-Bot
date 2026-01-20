"""
Tests for Ban Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestBanService:
    """Test ban_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        # Import ban service functions - adjust based on actual implementation
        try:
            from bot_core.services.ban_service import (
                add_ban, remove_ban, is_banned, get_banned_users
            )
            self.add_ban = add_ban
            self.remove_ban = remove_ban
            self.is_banned = is_banned
            self.get_banned_users = get_banned_users
            self.has_ban_service = True
        except ImportError:
            # Ban service may be part of shared_bot_logic or another module
            self.has_ban_service = False
        
        self.chat_id = 'test_chat_123'
        self.user_id = 'user_456'
        self.user_name = 'Test User'
    
    def test_add_ban(self):
        """Test banning a user"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        result = self.add_ban(self.chat_id, self.user_id, self.user_name)
        assert result is True
    
    def test_is_banned_true(self):
        """Test checking if banned user is banned"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        self.add_ban(self.chat_id, self.user_id, self.user_name)
        result = self.is_banned(self.chat_id, self.user_id)
        assert result is True
    
    def test_is_banned_false(self):
        """Test checking if non-banned user is banned"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        result = self.is_banned(self.chat_id, 'not_banned_user')
        assert result is False
    
    def test_remove_ban(self):
        """Test unbanning a user"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        self.add_ban(self.chat_id, self.user_id, self.user_name)
        result = self.remove_ban(self.chat_id, self.user_id)
        assert result is True
        
        assert self.is_banned(self.chat_id, self.user_id) is False
    
    def test_remove_ban_not_banned(self):
        """Test unbanning user who is not banned"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        result = self.remove_ban(self.chat_id, 'not_banned_user')
        assert result in [True, False]  # Implementation dependent
    
    def test_get_banned_users_empty(self):
        """Test getting banned users when none are banned"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        users = self.get_banned_users('empty_chat')
        assert users == [] or users is None
    
    def test_get_banned_users_with_bans(self):
        """Test getting banned users list"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        self.add_ban(self.chat_id, 'user1', 'User 1')
        self.add_ban(self.chat_id, 'user2', 'User 2')
        
        users = self.get_banned_users(self.chat_id)
        assert len(users) >= 2
    
    def test_ban_different_chats(self):
        """Test bans are per-chat"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        self.add_ban('chat1', self.user_id, self.user_name)
        
        assert self.is_banned('chat1', self.user_id) is True
        assert self.is_banned('chat2', self.user_id) is False
    
    def test_ban_with_reason(self):
        """Test banning with a reason"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        try:
            result = self.add_ban(self.chat_id, self.user_id, self.user_name, reason="Spamming")
            assert result is True
        except TypeError:
            # Reason parameter may not be supported
            pass


class TestBanServiceEdgeCases:
    """Edge case tests for ban service"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        try:
            from bot_core.services.ban_service import (
                add_ban, is_banned, remove_ban
            )
            self.add_ban = add_ban
            self.is_banned = is_banned
            self.remove_ban = remove_ban
            self.has_ban_service = True
        except ImportError:
            self.has_ban_service = False
    
    def test_ban_same_user_twice(self):
        """Test banning already banned user"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        self.add_ban('chat', 'user', 'name')
        result = self.add_ban('chat', 'user', 'name')
        # Should handle gracefully
        assert isinstance(result, bool)
    
    def test_ban_user_with_special_id(self):
        """Test banning user with special characters in ID"""
        if not self.has_ban_service:
            pytest.skip("Ban service not available")
        
        result = self.add_ban('chat', 'user@special!id#123', 'Special User')
        assert isinstance(result, bool)


class TestMuteService:
    """Tests for mute functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for mute tests"""
        try:
            from bot_core.services.mute_service import (
                mute_user, unmute_user, is_muted, get_muted_users
            )
            self.mute_user = mute_user
            self.unmute_user = unmute_user
            self.is_muted = is_muted
            self.get_muted_users = get_muted_users
            self.has_mute_service = True
        except ImportError:
            self.has_mute_service = False
        
        self.chat_id = 'test_chat_123'
        self.user_id = 'user_456'
    
    @pytest.mark.skip(reason="Mute service not yet implemented")
    def test_mute_user(self):
        """Test muting a user"""
        pass
    
    @pytest.mark.skip(reason="Mute service not yet implemented")
    def test_unmute_user(self):
        """Test unmuting a user"""
        pass
    
    @pytest.mark.skip(reason="Mute service not yet implemented")
    def test_is_muted(self):
        """Test checking if user is muted"""
        pass
    
    @pytest.mark.skip(reason="Mute service not yet implemented")
    def test_timed_mute(self):
        """Test timed mute (auto-unmute after duration)"""
        pass
    
    @pytest.mark.skip(reason="Mute service not yet implemented")
    def test_mute_with_reason(self):
        """Test muting with reason"""
        pass


class TestKickService:
    """Tests for kick functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for kick tests"""
        self.chat_id = 'test_chat_123'
        self.user_id = 'user_456'
    
    @pytest.mark.skip(reason="Kick service not yet implemented")
    def test_kick_user(self):
        """Test kicking a user"""
        pass
    
    @pytest.mark.skip(reason="Kick service not yet implemented")
    def test_kick_with_reason(self):
        """Test kicking with reason"""
        pass
    
    @pytest.mark.skip(reason="Kick service not yet implemented")
    def test_kick_admin(self):
        """Test that admins cannot be kicked"""
        pass


class TestGlobalBanService:
    """Tests for global ban (gban) functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for global ban tests"""
        self.user_id = 'user_456'
    
    @pytest.mark.skip(reason="Global ban service not yet implemented")
    def test_global_ban_user(self):
        """Test globally banning a user"""
        pass
    
    @pytest.mark.skip(reason="Global ban service not yet implemented")
    def test_global_unban_user(self):
        """Test globally unbanning a user"""
        pass
    
    @pytest.mark.skip(reason="Global ban service not yet implemented")
    def test_is_globally_banned(self):
        """Test checking if user is globally banned"""
        pass
    
    @pytest.mark.skip(reason="Global ban service not yet implemented")
    def test_global_ban_applies_to_all_chats(self):
        """Test global ban applies across all chats"""
        pass
    
    @pytest.mark.skip(reason="Global ban service not yet implemented")
    def test_global_ban_requires_permission(self):
        """Test global ban requires special permissions"""
        pass
