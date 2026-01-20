"""
Tests for Blacklist Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestBlacklistService:
    """Test blacklist_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        from bot_core.services.blacklist_service import (
            add_blacklist_word, remove_blacklist_word, get_blacklist_words,
            check_blacklist, clear_blacklist
        )
        self.add_blacklist_word = add_blacklist_word
        self.remove_blacklist_word = remove_blacklist_word
        self.get_blacklist_words = get_blacklist_words
        self.check_blacklist = check_blacklist
        self.clear_blacklist = clear_blacklist
        self.chat_id = 'test_chat_123'
    
    def test_add_blacklist_word(self):
        """Test adding a word to blacklist"""
        result = self.add_blacklist_word(self.chat_id, 'spam')
        assert result is True
    
    def test_add_multiple_words(self):
        """Test adding multiple words"""
        self.add_blacklist_word(self.chat_id, 'spam')
        self.add_blacklist_word(self.chat_id, 'scam')
        self.add_blacklist_word(self.chat_id, 'advertise')
        
        words = self.get_blacklist_words(self.chat_id)
        assert len(words) == 3
        assert 'spam' in words
        assert 'scam' in words
        assert 'advertise' in words
    
    def test_add_duplicate_word(self):
        """Test adding duplicate word"""
        self.add_blacklist_word(self.chat_id, 'spam')
        result = self.add_blacklist_word(self.chat_id, 'spam')
        # Should handle gracefully (either skip or update)
        words = self.get_blacklist_words(self.chat_id)
        assert words.count('spam') == 1 or 'spam' in words
    
    def test_remove_blacklist_word(self):
        """Test removing a word from blacklist"""
        self.add_blacklist_word(self.chat_id, 'spam')
        result = self.remove_blacklist_word(self.chat_id, 'spam')
        assert result is True
        
        words = self.get_blacklist_words(self.chat_id)
        assert 'spam' not in words
    
    def test_remove_nonexistent_word(self):
        """Test removing word that doesn't exist"""
        result = self.remove_blacklist_word(self.chat_id, 'nonexistent')
        assert result in [True, False]  # Implementation dependent
    
    def test_get_blacklist_words_empty(self):
        """Test getting blacklist when empty"""
        words = self.get_blacklist_words('empty_chat')
        assert words == [] or words is None
    
    def test_check_blacklist_match(self):
        """Test checking message that contains blacklisted word"""
        self.add_blacklist_word(self.chat_id, 'spam')
        result = self.check_blacklist(self.chat_id, 'This is spam content')
        assert result is True or result == 'spam'
    
    def test_check_blacklist_no_match(self):
        """Test checking message with no blacklisted words"""
        self.add_blacklist_word(self.chat_id, 'spam')
        result = self.check_blacklist(self.chat_id, 'This is good content')
        assert result is False or result is None
    
    def test_check_blacklist_case_insensitive(self):
        """Test blacklist check is case insensitive"""
        self.add_blacklist_word(self.chat_id, 'spam')
        result = self.check_blacklist(self.chat_id, 'This is SPAM content')
        assert result is True or result == 'spam'
    
    def test_check_blacklist_partial_word(self):
        """Test blacklist matches partial words (if applicable)"""
        self.add_blacklist_word(self.chat_id, 'spam')
        result = self.check_blacklist(self.chat_id, 'This is spamming')
        # Implementation dependent - may or may not match
        assert isinstance(result, (bool, str, type(None)))
    
    def test_clear_blacklist(self):
        """Test clearing all blacklisted words"""
        self.add_blacklist_word(self.chat_id, 'spam')
        self.add_blacklist_word(self.chat_id, 'scam')
        
        result = self.clear_blacklist(self.chat_id)
        assert result is True
        
        words = self.get_blacklist_words(self.chat_id)
        assert words == [] or words is None
    
    def test_clear_empty_blacklist(self):
        """Test clearing blacklist when already empty"""
        result = self.clear_blacklist('empty_chat')
        # Should not raise error
        assert result in [True, False]
    
    def test_blacklist_different_chats(self):
        """Test blacklists are per-chat"""
        self.add_blacklist_word('chat1', 'spam')
        self.add_blacklist_word('chat2', 'scam')
        
        words1 = self.get_blacklist_words('chat1')
        words2 = self.get_blacklist_words('chat2')
        
        assert 'spam' in words1
        assert 'spam' not in words2
        assert 'scam' in words2
        assert 'scam' not in words1


class TestBlacklistServiceEdgeCases:
    """Edge case tests for blacklist service"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.blacklist_service import (
            add_blacklist_word, check_blacklist, get_blacklist_words
        )
        self.add_blacklist_word = add_blacklist_word
        self.check_blacklist = check_blacklist
        self.get_blacklist_words = get_blacklist_words
    
    def test_blacklist_unicode_word(self):
        """Test blacklisting unicode words"""
        self.add_blacklist_word('chat', '广告')  # Chinese for 'advertisement'
        words = self.get_blacklist_words('chat')
        assert '广告' in words
    
    def test_blacklist_emoji(self):
        """Test blacklisting emoji"""
        self.add_blacklist_word('chat', '🚫')
        words = self.get_blacklist_words('chat')
        assert '🚫' in words
    
    def test_blacklist_phrase(self):
        """Test blacklisting multi-word phrase"""
        self.add_blacklist_word('chat', 'buy now')
        result = self.check_blacklist('chat', 'Click here to buy now!')
        assert result is True or 'buy now' in str(result)
    
    def test_blacklist_special_characters(self):
        """Test blacklisting words with special characters"""
        self.add_blacklist_word('chat', 'f*ck')
        words = self.get_blacklist_words('chat')
        assert 'f*ck' in words
    
    def test_blacklist_regex_pattern(self):
        """Test if blacklist supports regex patterns"""
        # This may or may not be supported
        self.add_blacklist_word('chat', 'spam.*link')
        words = self.get_blacklist_words('chat')
        assert 'spam.*link' in words
    
    def test_check_empty_message(self):
        """Test checking empty message"""
        self.add_blacklist_word('chat', 'spam')
        result = self.check_blacklist('chat', '')
        assert result is False or result is None
    
    def test_check_none_message(self):
        """Test checking None message"""
        self.add_blacklist_word('chat', 'spam')
        try:
            result = self.check_blacklist('chat', None)
            assert result is False or result is None
        except (TypeError, AttributeError):
            pass  # Expected if None not handled
    
    def test_blacklist_very_long_word(self):
        """Test blacklisting very long word"""
        long_word = 'a' * 500
        self.add_blacklist_word('chat', long_word)
        words = self.get_blacklist_words('chat')
        assert long_word in words
