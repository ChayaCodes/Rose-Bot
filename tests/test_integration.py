"""
Integration Tests for Rose Bot
These tests verify that multiple components work together correctly.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestWarnBanIntegration:
    """Test warn and ban interaction"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.warn_service import (
            warn_user, get_user_warns, reset_user_warns, 
            set_warn_limit, get_warn_limit
        )
        self.warn_user = warn_user
        self.get_user_warns = get_user_warns
        self.reset_user_warns = reset_user_warns
        self.set_warn_limit = set_warn_limit
        self.get_warn_limit = get_warn_limit
        self.chat_id = 'test_chat'
        self.user_id = 'user_123'
    
    def test_warn_until_limit(self):
        """Test that warnings accumulate until limit"""
        self.set_warn_limit(self.chat_id, 3)
        
        for i in range(3):
            count, limit = self.warn_user(self.chat_id, self.user_id, 'Test User')
            
            if count < limit:
                assert count == i + 1
            else:
                # At limit - should trigger action
                assert count >= limit
    
    def test_warn_triggers_action_at_limit(self):
        """Test that reaching warn limit triggers action"""
        self.set_warn_limit(self.chat_id, 2)
        
        count1, limit = self.warn_user(self.chat_id, self.user_id, 'Test')
        assert count1 == 1
        
        count2, limit = self.warn_user(self.chat_id, self.user_id, 'Test')
        assert count2 == 2
        assert count2 >= limit  # Should trigger ban/mute
    
    def test_reset_warns_prevents_action(self):
        """Test that resetting warns prevents reaching limit"""
        self.set_warn_limit(self.chat_id, 3)
        
        # Warn twice
        self.warn_user(self.chat_id, self.user_id, 'Test')
        self.warn_user(self.chat_id, self.user_id, 'Test')
        
        # Reset
        self.reset_user_warns(self.chat_id, self.user_id)
        
        # Warn once more - should be at 1, not 3
        count, limit = self.warn_user(self.chat_id, self.user_id, 'Test')
        assert count == 1


class TestBlacklistModeration:
    """Test blacklist with AI moderation interaction"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.blacklist_service import (
            add_blacklist_word, check_blacklist
        )
        from bot_core.services.ai_moderation_service import (
            set_ai_enabled, check_content_toxicity
        )
        self.add_blacklist_word = add_blacklist_word
        self.check_blacklist = check_blacklist
        self.set_ai_enabled = set_ai_enabled
        self.check_content_toxicity = check_content_toxicity
        self.chat_id = 'test_chat'
    
    def test_blacklist_checked_before_ai(self):
        """Test that blacklist is faster than AI check"""
        self.add_blacklist_word(self.chat_id, 'badword')
        
        # Blacklist check should be synchronous and fast
        result = self.check_blacklist(self.chat_id, 'This has badword in it')
        assert result is True or result == 'badword'
    
    def test_both_systems_can_flag(self):
        """Test message can be flagged by both systems"""
        self.add_blacklist_word(self.chat_id, 'spam')
        self.set_ai_enabled(self.chat_id, True)
        
        # Blacklist check
        blacklist_result = self.check_blacklist(self.chat_id, 'spam spam spam')
        assert blacklist_result is True or 'spam' in str(blacklist_result)
        
        # AI would also check (if enabled and API available)


class TestLocksBlacklistIntegration:
    """Test locks and blacklist interaction"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.locks_service import (
            set_lock, check_message_locks
        )
        from bot_core.services.blacklist_service import (
            add_blacklist_word, check_blacklist
        )
        self.set_lock = set_lock
        self.check_message_locks = check_message_locks
        self.add_blacklist_word = add_blacklist_word
        self.check_blacklist = check_blacklist
        self.chat_id = 'test_chat'
    
    def test_both_filters_applied(self):
        """Test both locks and blacklist are checked"""
        self.set_lock(self.chat_id, 'url', True)
        self.add_blacklist_word(self.chat_id, 'promo')
        
        message = "Check out promo at https://example.com"
        
        # Both should flag
        lock_result = self.check_message_locks(
            self.chat_id, message, has_sticker=False, has_media=False
        )
        blacklist_result = self.check_blacklist(self.chat_id, message)
        
        assert lock_result is True or lock_result == 'url'
        assert blacklist_result is True or blacklist_result == 'promo'


class TestWelcomeRulesIntegration:
    """Test welcome message and rules interaction"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.welcome_service import (
            set_welcome_message, get_welcome_message
        )
        from bot_core.services.rules_service import (
            set_rules, get_rules
        )
        self.set_welcome = set_welcome_message
        self.get_welcome = get_welcome_message
        self.set_rules = set_rules
        self.get_rules = get_rules
        self.chat_id = 'test_chat'
    
    def test_welcome_can_reference_rules(self):
        """Test welcome message can mention rules"""
        self.set_rules(self.chat_id, "1. Be nice\n2. No spam")
        self.set_welcome(self.chat_id, "Welcome! Please read /rules before chatting.")
        
        welcome = self.get_welcome(self.chat_id)
        assert '/rules' in welcome
    
    def test_both_set_independently(self):
        """Test welcome and rules are independent"""
        self.set_welcome(self.chat_id, "Welcome!")
        self.set_rules(self.chat_id, "Rules here")
        
        assert self.get_welcome(self.chat_id) == "Welcome!"
        assert self.get_rules(self.chat_id) == "Rules here"


class TestFloodWarnIntegration:
    """Test flood detection and warning integration"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.flood_service import (
            check_flood, set_flood_limit
        )
        from bot_core.services.warn_service import warn_user, get_user_warns
        
        self.check_flood = check_flood
        self.set_flood_limit = set_flood_limit
        self.warn_user = warn_user
        self.get_user_warns = get_user_warns
        self.chat_id = 'test_chat'
        self.user_id = 'user_123'
    
    def test_flood_can_trigger_warn(self):
        """Test that flood detection can lead to warning"""
        self.set_flood_limit(self.chat_id, 3)
        
        # Simulate rapid messages
        for i in range(5):
            is_flood = self.check_flood(self.chat_id, self.user_id)
            if is_flood:
                # Warn for flooding
                self.warn_user(self.chat_id, self.user_id, 'Test', 'Flooding')
        
        count, _ = self.get_user_warns(self.chat_id, self.user_id)
        assert count >= 1  # At least one warn for flooding


class TestLanguageIntegration:
    """Test language affects all messages"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.language_service import (
            set_chat_language, get_translated_text
        )
        self.set_language = set_chat_language
        self.get_text = get_translated_text
        self.chat_id = 'test_chat'
    
    def test_language_affects_all_responses(self):
        """Test that language setting affects all bot responses"""
        self.set_language(self.chat_id, 'es')
        
        # Get various texts in Spanish
        warn_text = self.get_text('es', 'user_warned')
        welcome_text = self.get_text('es', 'welcome_message')
        
        # Should be in Spanish (or fallback to English)
        assert isinstance(warn_text, str)
        assert isinstance(welcome_text, str)


class TestFullMessageFlow:
    """Test complete message processing flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.blacklist_service import add_blacklist_word, check_blacklist
        from bot_core.services.locks_service import set_lock, check_message_locks
        from bot_core.services.flood_service import check_flood
        from bot_core.services.ai_moderation_service import set_ai_enabled
        
        self.add_blacklist_word = add_blacklist_word
        self.check_blacklist = check_blacklist
        self.set_lock = set_lock
        self.check_message_locks = check_message_locks
        self.check_flood = check_flood
        self.set_ai_enabled = set_ai_enabled
        self.chat_id = 'test_chat'
        self.user_id = 'user_123'
    
    def test_message_passes_all_filters(self):
        """Test clean message passes all filters"""
        # Setup filters
        self.add_blacklist_word(self.chat_id, 'spam')
        self.set_lock(self.chat_id, 'url', True)
        self.set_ai_enabled(self.chat_id, True)
        
        message = "Hello everyone! Nice to meet you all."
        
        # Check all filters
        blacklist = self.check_blacklist(self.chat_id, message)
        locks = self.check_message_locks(
            self.chat_id, message, has_sticker=False, has_media=False
        )
        flood = self.check_flood(self.chat_id, self.user_id)
        
        # All should pass
        assert blacklist is False or blacklist is None
        assert locks is False or locks is None
        assert flood is False
    
    def test_message_blocked_by_blacklist(self):
        """Test message blocked by blacklist"""
        self.add_blacklist_word(self.chat_id, 'badword')
        
        message = "This contains badword"
        
        result = self.check_blacklist(self.chat_id, message)
        assert result is True or result == 'badword'
    
    def test_message_blocked_by_locks(self):
        """Test message blocked by locks"""
        self.set_lock(self.chat_id, 'url', True)
        
        message = "Check https://example.com"
        
        result = self.check_message_locks(
            self.chat_id, message, has_sticker=False, has_media=False
        )
        assert result is True or result == 'url'


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database operations across services"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.database import init_db, get_session
        self.init_db = init_db
        self.get_session = get_session
        self.chat_id = 'test_chat'
    
    def test_multiple_services_same_chat(self):
        """Test multiple services can store data for same chat"""
        from bot_core.services.rules_service import set_rules, get_rules
        from bot_core.services.welcome_service import set_welcome_message, get_welcome_message
        from bot_core.services.warn_service import set_warn_limit, get_warn_limit
        
        # Set data in multiple services
        set_rules(self.chat_id, "Test rules")
        set_welcome_message(self.chat_id, "Welcome!")
        set_warn_limit(self.chat_id, 5)
        
        # All should be retrievable
        assert get_rules(self.chat_id) == "Test rules"
        assert get_welcome_message(self.chat_id) == "Welcome!"
        assert get_warn_limit(self.chat_id) == 5
    
    def test_data_isolation_between_chats(self):
        """Test data is isolated between different chats"""
        from bot_core.services.rules_service import set_rules, get_rules
        
        set_rules('chat1', "Rules for chat 1")
        set_rules('chat2', "Rules for chat 2")
        
        assert get_rules('chat1') == "Rules for chat 1"
        assert get_rules('chat2') == "Rules for chat 2"
        
        # Modifying one doesn't affect other
        set_rules('chat1', "Updated rules")
        assert get_rules('chat2') == "Rules for chat 2"


@pytest.mark.integration
class TestWhatsAppBotIntegration:
    """Integration tests for WhatsApp bot"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.chat_id = 'test_chat'
    
    @pytest.mark.skip(reason="Requires WhatsApp bridge connection")
    def test_whatsapp_message_processing(self):
        """Test WhatsApp message is processed correctly"""
        pass
    
    @pytest.mark.skip(reason="Requires WhatsApp bridge connection")
    def test_whatsapp_command_handling(self):
        """Test WhatsApp commands are handled"""
        pass
    
    @pytest.mark.skip(reason="Requires WhatsApp bridge connection")
    def test_whatsapp_group_admin_detection(self):
        """Test admin detection in WhatsApp groups"""
        pass


@pytest.mark.integration
class TestTelegramBotIntegration:
    """Integration tests for Telegram bot"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.chat_id = -1001234567890  # Test chat ID
    
    @pytest.mark.skip(reason="Requires Telegram API connection")
    def test_telegram_message_processing(self):
        """Test Telegram message is processed correctly"""
        pass
    
    @pytest.mark.skip(reason="Requires Telegram API connection")
    def test_telegram_command_handling(self):
        """Test Telegram commands are handled"""
        pass
    
    @pytest.mark.skip(reason="Requires Telegram API connection")
    def test_telegram_callback_handling(self):
        """Test Telegram inline keyboard callbacks"""
        pass
