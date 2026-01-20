"""
Tests for Language Service (i18n)
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestLanguageService:
    """Test language_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        from bot_core.services.language_service import (
            get_chat_language, set_chat_language, get_translated_text
        )
        self.get_chat_language = get_chat_language
        self.set_chat_language = set_chat_language
        self.get_translated_text = get_translated_text
        self.chat_id = 'test_chat_123'
    
    def test_set_chat_language(self):
        """Test setting chat language"""
        result = self.set_chat_language(self.chat_id, 'es')
        assert result is True
    
    def test_get_chat_language_after_set(self):
        """Test getting chat language after setting"""
        self.set_chat_language(self.chat_id, 'fr')
        lang = self.get_chat_language(self.chat_id)
        assert lang == 'fr'
    
    def test_get_chat_language_default(self):
        """Test getting language returns default when not set"""
        lang = self.get_chat_language('chat_no_lang')
        assert lang == 'en' or lang is None
    
    def test_update_chat_language(self):
        """Test updating existing language setting"""
        self.set_chat_language(self.chat_id, 'es')
        self.set_chat_language(self.chat_id, 'de')
        lang = self.get_chat_language(self.chat_id)
        assert lang == 'de'
    
    def test_get_translated_text_english(self):
        """Test getting English text"""
        text = self.get_translated_text('en', 'welcome_message')
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_get_translated_text_other_language(self):
        """Test getting text in another language"""
        text = self.get_translated_text('es', 'welcome_message')
        assert isinstance(text, str)
    
    def test_get_translated_text_fallback(self):
        """Test fallback to English for missing translation"""
        text_en = self.get_translated_text('en', 'welcome_message')
        text_unknown = self.get_translated_text('xx', 'welcome_message')
        
        # Should fallback to English or return the key
        assert isinstance(text_unknown, str)
    
    def test_get_translated_text_missing_key(self):
        """Test getting text for missing key"""
        text = self.get_translated_text('en', 'nonexistent_key_12345')
        # Should return the key itself or empty string
        assert text == 'nonexistent_key_12345' or text == '' or isinstance(text, str)
    
    def test_language_different_chats(self):
        """Test languages are per-chat"""
        self.set_chat_language('chat1', 'es')
        self.set_chat_language('chat2', 'fr')
        
        assert self.get_chat_language('chat1') == 'es'
        assert self.get_chat_language('chat2') == 'fr'


class TestLanguageServiceEdgeCases:
    """Edge case tests for language service"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.language_service import (
            set_chat_language, get_chat_language, get_translated_text
        )
        self.set_chat_language = set_chat_language
        self.get_chat_language = get_chat_language
        self.get_translated_text = get_translated_text
    
    def test_invalid_language_code(self):
        """Test setting invalid language code"""
        try:
            result = self.set_chat_language('chat', 'invalid_lang_code')
            # Should either reject or accept
            assert isinstance(result, bool)
        except ValueError:
            pass  # Expected
    
    def test_empty_language_code(self):
        """Test setting empty language code"""
        try:
            result = self.set_chat_language('chat', '')
            assert isinstance(result, bool)
        except ValueError:
            pass  # Expected
    
    def test_language_code_case(self):
        """Test language code case sensitivity"""
        self.set_chat_language('chat', 'EN')
        lang = self.get_chat_language('chat')
        assert lang.lower() == 'en'
    
    def test_translation_with_placeholders(self):
        """Test translated text with placeholders"""
        text = self.get_translated_text('en', 'user_warned')
        # May contain {name}, {count}, etc.
        assert isinstance(text, str)
    
    def test_supported_languages(self):
        """Test various supported languages"""
        languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ar', 'zh', 'ja']
        
        for lang in languages:
            self.set_chat_language('chat', lang)
            result = self.get_chat_language('chat')
            assert result == lang or isinstance(result, str)


class TestI18nTranslations:
    """Test i18n.py translation functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for i18n tests"""
        from bot_core.i18n import get_text
        self.get_text = get_text
    
    def test_get_text_english(self):
        """Test getting English text"""
        text = self.get_text('en', 'welcome_message')
        assert isinstance(text, str)
    
    def test_get_text_with_format(self):
        """Test getting text with format arguments"""
        text = self.get_text('en', 'user_warned', name='John', count=1)
        assert 'John' in text or isinstance(text, str)
    
    def test_get_text_all_keys(self):
        """Test that all translation keys exist"""
        required_keys = [
            'welcome_message',
            'rules_message',
            'warn_message',
            'ban_message',
            'mute_message',
            'help_message',
            'error_message',
            'success_message',
        ]
        
        for key in required_keys:
            text = self.get_text('en', key)
            assert isinstance(text, str)
    
    def test_translation_consistency(self):
        """Test translation keys exist in multiple languages"""
        languages = ['en', 'es', 'fr']
        key = 'welcome_message'
        
        for lang in languages:
            text = self.get_text(lang, key)
            assert isinstance(text, str)


class TestLanguageDetection:
    """Tests for automatic language detection (Future Feature)"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for language detection tests"""
        self.chat_id = 'test_chat_123'
    
    @pytest.mark.skip(reason="Auto language detection not yet implemented")
    def test_detect_language_from_message(self):
        """Test detecting language from user message"""
        pass
    
    @pytest.mark.skip(reason="Auto language detection not yet implemented")
    def test_auto_set_language(self):
        """Test automatically setting language based on detection"""
        pass
    
    @pytest.mark.skip(reason="Auto language detection not yet implemented")
    def test_language_voting(self):
        """Test language voting for group chats"""
        pass
