"""
Tests for Rules Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestRulesService:
    """Test rules_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        from bot_core.services.rules_service import (
            get_rules, set_rules, clear_rules
        )
        self.get_rules = get_rules
        self.set_rules = set_rules
        self.clear_rules = clear_rules
        self.chat_id = 'test_chat_123'
    
    def test_set_rules(self):
        """Test setting rules for a chat"""
        rules_text = "1. Be respectful\n2. No spam\n3. English only"
        result = self.set_rules(self.chat_id, rules_text)
        assert result is True
    
    def test_get_rules_after_set(self):
        """Test getting rules after setting them"""
        rules_text = "1. Be respectful\n2. No spam"
        self.set_rules(self.chat_id, rules_text)
        retrieved = self.get_rules(self.chat_id)
        assert retrieved == rules_text
    
    def test_get_rules_no_rules(self):
        """Test getting rules when none are set"""
        result = self.get_rules('chat_with_no_rules')
        assert result is None or result == ""
    
    def test_update_rules(self):
        """Test updating existing rules"""
        self.set_rules(self.chat_id, "Old rules")
        self.set_rules(self.chat_id, "New rules")
        result = self.get_rules(self.chat_id)
        assert result == "New rules"
    
    def test_clear_rules(self):
        """Test clearing rules"""
        self.set_rules(self.chat_id, "Some rules")
        result = self.clear_rules(self.chat_id)
        assert result is True
        
        rules = self.get_rules(self.chat_id)
        assert rules is None or rules == ""
    
    def test_clear_rules_not_set(self):
        """Test clearing rules when none are set"""
        result = self.clear_rules('chat_with_no_rules')
        # Should not raise error
        assert result in [True, False]
    
    def test_rules_different_chats(self):
        """Test rules are per-chat"""
        self.set_rules('chat1', "Rules for chat 1")
        self.set_rules('chat2', "Rules for chat 2")
        
        assert self.get_rules('chat1') == "Rules for chat 1"
        assert self.get_rules('chat2') == "Rules for chat 2"


class TestRulesServiceEdgeCases:
    """Edge case tests for rules service"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.rules_service import (
            get_rules, set_rules, clear_rules
        )
        self.get_rules = get_rules
        self.set_rules = set_rules
        self.clear_rules = clear_rules
    
    def test_rules_with_unicode(self):
        """Test rules with unicode characters"""
        rules = "🎯 規則 1: 尊重他人\n🎯 règle 2: שלום"
        self.set_rules('chat', rules)
        assert self.get_rules('chat') == rules
    
    def test_rules_with_markdown(self):
        """Test rules with markdown formatting"""
        rules = "**Bold Rule**\n_Italic Rule_\n`Code Rule`"
        self.set_rules('chat', rules)
        assert self.get_rules('chat') == rules
    
    def test_rules_with_html(self):
        """Test rules with HTML tags"""
        rules = "<b>Bold</b>\n<i>Italic</i>\n<a href='link'>Link</a>"
        self.set_rules('chat', rules)
        assert self.get_rules('chat') == rules
    
    def test_rules_very_long(self):
        """Test setting very long rules"""
        long_rules = "\n".join([f"Rule {i}: Be good" for i in range(100)])
        self.set_rules('chat', long_rules)
        assert self.get_rules('chat') == long_rules
    
    def test_rules_empty_string(self):
        """Test setting empty string rules"""
        self.set_rules('chat', "")
        result = self.get_rules('chat')
        assert result == "" or result is None
    
    def test_rules_whitespace_only(self):
        """Test setting whitespace-only rules"""
        self.set_rules('chat', "   \n\t  ")
        result = self.get_rules('chat')
        assert result == "   \n\t  " or result.strip() == ""
    
    def test_rules_with_newlines(self):
        """Test rules preserve newlines"""
        rules = "Line 1\n\nLine 2\n\n\nLine 3"
        self.set_rules('chat', rules)
        assert self.get_rules('chat') == rules
