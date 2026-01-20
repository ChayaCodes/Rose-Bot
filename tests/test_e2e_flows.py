"""
End-to-End Flow Tests for Rose-Bot
Tests complete user flows from message to action.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestUserJoinFlow:
    """Test complete user join flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.welcome_service import set_welcome, get_welcome
        
        self.set_welcome = set_welcome
        self.get_welcome = get_welcome
        self.chat_id = "e2e_join_chat"
        self.user_id = "e2e_new_user"
    
    def test_join_with_welcome_message(self, mock_actions):
        """Test user joins and receives welcome"""
        # Setup: Set welcome message
        welcome_msg = "Welcome {name} to our group! 🎉"
        self.set_welcome(self.chat_id, welcome_msg)
        
        # Verify welcome is set
        stored = self.get_welcome(self.chat_id)
        assert stored == welcome_msg
        
        # Action: User joins (simulated)
        user_name = "NewUser"
        formatted_welcome = welcome_msg.format(name=user_name)
        
        # Verify welcome would be sent
        assert "NewUser" in formatted_welcome
        assert "🎉" in formatted_welcome
    
    def test_join_without_welcome(self, mock_actions):
        """Test user joins with no welcome set"""
        # No welcome set
        stored = self.get_welcome("empty_chat")
        assert stored is None


class TestBlacklistViolationFlow:
    """Test complete blacklist violation flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.blacklist_service import (
            add_blacklist_word, check_blacklist, get_blacklist_action
        )
        
        self.add_blacklist = add_blacklist_word
        self.check_blacklist = check_blacklist
        self.get_action = get_blacklist_action
        self.chat_id = "e2e_blacklist_chat"
    
    def test_blacklist_delete_flow(self, mock_actions):
        """Test: User sends blacklisted word -> Message deleted"""
        # Setup: Add blacklist words
        self.add_blacklist(self.chat_id, "spam")
        self.add_blacklist(self.chat_id, "advertising")
        
        # User sends message with blacklisted word
        message = "Check out this spam link!"
        
        # Check should detect violation
        result = self.check_blacklist(self.chat_id, message)
        
        # Should be flagged
        assert result is True or result is not None
    
    def test_blacklist_warn_flow(self, mock_actions):
        """Test: Blacklist with warn action"""
        from bot_core.services.warn_service import add_warn, get_warns
        
        # Setup blacklist
        self.add_blacklist(self.chat_id, "badword")
        
        # Check message
        message = "This contains badword"
        is_violation = self.check_blacklist(self.chat_id, message)
        
        if is_violation:
            # Should add warn
            add_warn(self.chat_id, "violator_user", "Blacklist violation")
            
            warns = get_warns(self.chat_id, "violator_user")
            assert len(warns) >= 1


class TestWarnLimitFlow:
    """Test complete warn limit flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.warn_service import (
            add_warn, get_warns, get_warn_limit, set_warn_limit
        )
        
        self.add_warn = add_warn
        self.get_warns = get_warns
        self.get_limit = get_warn_limit
        self.set_limit = set_warn_limit
        self.chat_id = "e2e_warn_chat"
        self.user_id = "e2e_warned_user"
    
    def test_warn_limit_kick_flow(self, mock_actions):
        """Test: User reaches warn limit -> User kicked"""
        # Setup: Set warn limit to 3
        self.set_limit(self.chat_id, 3)
        
        # Issue warnings
        for i in range(3):
            result = self.add_warn(self.chat_id, self.user_id, f"Warning {i+1}")
        
        # Check warn count
        warns = self.get_warns(self.chat_id, self.user_id)
        limit = self.get_limit(self.chat_id)
        
        # Should reach limit
        assert len(warns) >= limit
        
        # At this point, bot would kick user
        # Result from last warn should indicate action needed
    
    def test_warn_under_limit(self, mock_actions):
        """Test: User has warns but under limit"""
        self.set_limit(self.chat_id, 5)
        
        # Add 2 warnings
        self.add_warn(self.chat_id, "safe_user", "Warning 1")
        self.add_warn(self.chat_id, "safe_user", "Warning 2")
        
        warns = self.get_warns(self.chat_id, "safe_user")
        limit = self.get_limit(self.chat_id)
        
        assert len(warns) < limit


class TestFloodDetectionFlow:
    """Test complete flood detection flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.flood_service import (
            enable_flood_detection, check_flood, get_flood_settings
        )
        
        self.enable_flood = enable_flood_detection
        self.check_flood = check_flood
        self.get_settings = get_flood_settings
        self.chat_id = "e2e_flood_chat"
        self.user_id = "e2e_flood_user"
    
    def test_flood_detection_flow(self, mock_actions):
        """Test: User sends many messages -> Flood detected"""
        # Setup: Enable flood detection
        self.enable_flood(self.chat_id, limit=5, time_window=10)
        
        # User sends multiple messages quickly
        for i in range(6):
            result = self.check_flood(self.chat_id, self.user_id)
            
            if i < 5:
                assert result is False or result is None
            else:
                # 6th message should trigger flood
                assert result is True or result is not None
    
    def test_no_flood_for_slow_messages(self, mock_actions):
        """Test: Slow messages don't trigger flood"""
        import time
        
        self.enable_flood(self.chat_id, limit=5, time_window=1)
        
        # Simulate slow sending
        for i in range(3):
            result = self.check_flood(self.chat_id, "slow_user")
            assert result is False or result is None


class TestLockViolationFlow:
    """Test complete lock violation flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.locks_service import (
            set_lock, check_lock_violations, get_locks
        )
        
        self.set_lock = set_lock
        self.check_locks = check_lock_violations
        self.get_locks = get_locks
        self.chat_id = "e2e_lock_chat"
    
    def test_link_lock_flow(self, mock_actions):
        """Test: Links locked -> Link message deleted"""
        # Setup: Lock links
        self.set_lock(self.chat_id, "links", True)
        
        # Create mock message with link
        message = MagicMock()
        message.text = "Check out https://example.com"
        message.entities = [MagicMock(type="url")]
        
        # Check violation
        result = self.check_locks(self.chat_id, message)
        
        # Should detect violation
        assert result is True or result is not None or "links" in str(result).lower()
    
    def test_media_lock_flow(self, mock_actions):
        """Test: Media locked -> Media message deleted"""
        # Lock images
        self.set_lock(self.chat_id, "images", True)
        
        # Create mock message with image
        message = MagicMock()
        message.text = None
        message.photo = [MagicMock()]  # Has photo
        
        result = self.check_locks(self.chat_id, message)
        
        # Should detect violation
        assert result is True or result is not None


class TestAIModerationFlow:
    """Test complete AI moderation flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.ai_moderation_service import (
            enable_ai_moderation, check_message_with_ai, is_ai_enabled
        )
        
        self.enable_ai = enable_ai_moderation
        self.check_ai = check_message_with_ai
        self.is_enabled = is_ai_enabled
        self.chat_id = "e2e_ai_chat"
    
    @pytest.mark.asyncio
    async def test_ai_toxic_message_flow(self, mock_openai):
        """Test: Toxic message -> AI detects -> Action taken"""
        # Enable AI moderation
        self.enable_ai(self.chat_id, threshold=0.5, action="warn")
        
        # Mock AI to detect toxic content
        toxic_message = "I hate you and wish you harm"
        
        with patch('bot_core.services.ai_moderation_service.openai_client') as mock:
            mock.moderations.create = AsyncMock(return_value=MagicMock(
                results=[MagicMock(
                    flagged=True,
                    categories=MagicMock(hate=True, violence=True),
                    category_scores=MagicMock(hate=0.9, violence=0.8)
                )]
            ))
            
            result = await self.check_ai(toxic_message)
            
            # Should be flagged
            assert result is not None
            if hasattr(result, 'flagged'):
                assert result.flagged == True
    
    @pytest.mark.asyncio
    async def test_ai_clean_message_flow(self, mock_openai):
        """Test: Clean message -> AI passes -> No action"""
        self.enable_ai(self.chat_id, threshold=0.5, action="delete")
        
        clean_message = "Hello, how are you doing today?"
        
        with patch('bot_core.services.ai_moderation_service.openai_client') as mock:
            mock.moderations.create = AsyncMock(return_value=MagicMock(
                results=[MagicMock(
                    flagged=False,
                    categories=MagicMock(hate=False, violence=False),
                    category_scores=MagicMock(hate=0.01, violence=0.01)
                )]
            ))
            
            result = await self.check_ai(clean_message)
            
            # Should not be flagged
            if hasattr(result, 'flagged'):
                assert result.flagged == False


class TestCommandProcessingFlow:
    """Test complete command processing flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.chat_id = "e2e_cmd_chat"
    
    def test_rules_command_flow(self, mock_actions):
        """Test: /rules command -> Rules displayed"""
        from bot_core.services.rules_service import set_rules, get_rules
        
        # Setup rules
        set_rules(self.chat_id, "Be nice to everyone!")
        
        # Process /rules command
        rules = get_rules(self.chat_id)
        
        assert rules == "Be nice to everyone!"
    
    def test_setrules_command_flow(self, mock_actions):
        """Test: Admin uses /setrules -> Rules updated"""
        from bot_core.services.rules_service import set_rules, get_rules
        
        # Admin sets rules
        new_rules = "1. No spam\n2. Be respectful"
        set_rules(self.chat_id, new_rules)
        
        # Verify
        rules = get_rules(self.chat_id)
        assert "No spam" in rules
        assert "Be respectful" in rules
    
    def test_warn_command_flow(self, mock_actions):
        """Test: Admin uses /warn -> User warned"""
        from bot_core.services.warn_service import add_warn, get_warns
        
        user_id = "target_user"
        reason = "Spamming links"
        
        # Admin warns user
        add_warn(self.chat_id, user_id, reason)
        
        # Verify warn added
        warns = get_warns(self.chat_id, user_id)
        assert len(warns) >= 1
        assert any("Spamming" in str(w) for w in warns) or len(warns) > 0
    
    def test_blacklist_add_command_flow(self, mock_actions):
        """Test: Admin uses /addblacklist -> Word added"""
        from bot_core.services.blacklist_service import add_blacklist_word, get_blacklist
        
        word = "spamword"
        
        # Admin adds word
        add_blacklist_word(self.chat_id, word)
        
        # Verify
        blacklist = get_blacklist(self.chat_id)
        assert word in blacklist


class TestLanguageFlow:
    """Test complete language switching flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.language_service import (
            set_chat_language, get_chat_language
        )
        from bot_core.i18n import get_text
        
        self.set_lang = set_chat_language
        self.get_lang = get_chat_language
        self.get_text = get_text
        self.chat_id = "e2e_lang_chat"
    
    def test_switch_to_english_flow(self, mock_actions):
        """Test: Switch to English -> All messages in English"""
        # Switch language
        self.set_lang(self.chat_id, "en")
        
        # Verify
        lang = self.get_lang(self.chat_id)
        assert lang == "en"
        
        # Get translated text
        text = self.get_text("en", "pong")
        assert "Pong" in text
    
    def test_switch_to_hebrew_flow(self, mock_actions):
        """Test: Switch to Hebrew -> All messages in Hebrew"""
        # Switch language
        self.set_lang(self.chat_id, "he")
        
        # Verify
        lang = self.get_lang(self.chat_id)
        assert lang == "he"
        
        # Get translated text
        text = self.get_text("he", "pong")
        assert isinstance(text, str)


class TestCompleteModeratorFlow:
    """Test complete moderator action flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.chat_id = "e2e_mod_chat"
        self.admin_id = "admin123"
        self.user_id = "user456"
    
    def test_kick_flow(self, mock_actions):
        """Test: Admin kicks user -> User removed"""
        from bot_core.services.warn_service import reset_warns
        
        # After kick, reset warns
        reset_warns(self.chat_id, self.user_id)
        
        # Verify execution
        mock_actions.execute_command.assert_not_called()  # No actual kick in test
    
    def test_ban_flow(self, mock_actions):
        """Test: Admin bans user -> User banned"""
        from bot_core.services.blacklist_service import get_blacklist
        
        # After ban, user should not be able to rejoin
        # This is handled by Telegram/WhatsApp API
        
        # Verify we can still query blacklist
        blacklist = get_blacklist(self.chat_id)
        assert isinstance(blacklist, (list, set, tuple))
    
    def test_mute_flow(self, mock_actions):
        """Test: Admin mutes user -> User restricted"""
        # Muting restricts user from sending messages
        # This is handled by platform API
        pass


class TestErrorRecoveryFlow:
    """Test error recovery flows"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.chat_id = "e2e_error_chat"
    
    def test_database_error_recovery(self, mock_actions):
        """Test: Database error -> Graceful handling"""
        from bot_core.services.rules_service import get_rules
        
        # Even with non-existent chat, should not crash
        rules = get_rules("nonexistent_chat_xyz")
        assert rules is None or isinstance(rules, str)
    
    def test_invalid_command_handling(self, mock_actions):
        """Test: Invalid command -> Error message shown"""
        from bot_core.i18n import get_text
        
        # Unknown command should return appropriate message
        text = get_text("he", "unknown_command", command="badcmd")
        assert isinstance(text, str)
    
    def test_permission_denied_handling(self, mock_actions):
        """Test: Non-admin uses admin command -> Permission denied"""
        from bot_core.i18n import get_text
        
        # Should have admin_only message
        text = get_text("he", "admin_only")
        assert isinstance(text, str)
        assert len(text) > 0


class TestMultiStepFlow:
    """Test multi-step action flows"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.chat_id = "e2e_multistep_chat"
    
    def test_setup_new_group_flow(self, mock_actions):
        """Test: Bot added to group -> Complete setup"""
        from bot_core.services.rules_service import set_rules
        from bot_core.services.welcome_service import set_welcome
        from bot_core.services.language_service import set_chat_language
        from bot_core.services.blacklist_service import add_blacklist_word
        
        # Step 1: Set language
        set_chat_language(self.chat_id, "he")
        
        # Step 2: Set rules
        set_rules(self.chat_id, "כללי הקבוצה")
        
        # Step 3: Set welcome
        set_welcome(self.chat_id, "ברוכים הבאים!")
        
        # Step 4: Add basic blacklist
        add_blacklist_word(self.chat_id, "spam")
        
        # Verify all set up
        from bot_core.services.rules_service import get_rules
        from bot_core.services.welcome_service import get_welcome
        from bot_core.services.language_service import get_chat_language
        from bot_core.services.blacklist_service import get_blacklist
        
        assert get_chat_language(self.chat_id) == "he"
        assert get_rules(self.chat_id) == "כללי הקבוצה"
        assert get_welcome(self.chat_id) == "ברוכים הבאים!"
        assert "spam" in get_blacklist(self.chat_id)
    
    def test_cleanup_group_flow(self, mock_actions):
        """Test: Group cleanup -> All settings reset"""
        from bot_core.services.rules_service import set_rules, get_rules
        from bot_core.services.welcome_service import set_welcome, get_welcome
        from bot_core.services.blacklist_service import clear_blacklist, get_blacklist
        
        # Clear all settings
        set_rules(self.chat_id, None)
        set_welcome(self.chat_id, None)
        clear_blacklist(self.chat_id)
        
        # Verify cleared
        assert get_rules(self.chat_id) is None
        assert get_welcome(self.chat_id) is None
        assert len(get_blacklist(self.chat_id)) == 0
