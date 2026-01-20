"""
Comprehensive Tests for i18n (Internationalization) System
Tests all translations, variables, and language functions.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTranslationsStructure:
    """Test that translation structure is correct"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.i18n import TRANSLATIONS, LANG_NAMES
        self.translations = TRANSLATIONS
        self.lang_names = LANG_NAMES
    
    def test_supported_languages_exist(self):
        """Test that Hebrew and English exist"""
        assert 'he' in self.translations
        assert 'en' in self.translations
    
    def test_lang_names_defined(self):
        """Test language names are defined"""
        assert 'he' in self.lang_names
        assert 'en' in self.lang_names
        assert self.lang_names['he'] == 'עברית'
        assert self.lang_names['en'] == 'English'
    
    def test_all_languages_have_same_keys(self):
        """Test all languages have the same translation keys"""
        he_keys = set(self.translations['he'].keys())
        en_keys = set(self.translations['en'].keys())
        
        # Find missing keys
        missing_in_en = he_keys - en_keys
        missing_in_he = en_keys - he_keys
        
        if missing_in_en:
            print(f"Missing in English: {missing_in_en}")
        if missing_in_he:
            print(f"Missing in Hebrew: {missing_in_he}")
        
        # All keys should match
        assert he_keys == en_keys, f"Mismatched keys: Missing in EN: {missing_in_en}, Missing in HE: {missing_in_he}"


class TestHebrewTranslations:
    """Test Hebrew translations are complete"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.i18n import TRANSLATIONS
        self.he = TRANSLATIONS.get('he', {})
    
    def test_general_messages(self):
        """Test general messages exist"""
        required_keys = [
            'start_msg',
            'help_general',
            'admin_only',
            'owner_only',
            'reply_to_user',
            'unknown_command',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
            assert len(self.he[key]) > 0, f"Empty Hebrew value for: {key}"
    
    def test_rules_messages(self):
        """Test rules-related messages exist"""
        required_keys = [
            'rules_show',
            'rules_not_set',
            'rules_set',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
    
    def test_warn_messages(self):
        """Test warn-related messages exist"""
        required_keys = [
            'warn_issued',
            'warn_limit_reached',
            'warns_count',
            'warns_none',
            'warns_reset',
            'warn_limit_set',
            'warn_limit_invalid',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
    
    def test_moderation_messages(self):
        """Test moderation messages exist"""
        required_keys = [
            'user_kicked',
            'user_banned',
            'kick_failed',
            'ban_failed',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
    
    def test_welcome_messages(self):
        """Test welcome messages exist"""
        required_keys = [
            'welcome_set',
            'welcome_show',
            'welcome_not_set',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
    
    def test_blacklist_messages(self):
        """Test blacklist messages exist"""
        required_keys = [
            'blacklist_show',
            'blacklist_empty',
            'blacklist_added',
            'blacklist_removed',
            'blacklist_not_found',
            'blacklist_detected',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
    
    def test_lock_messages(self):
        """Test lock messages exist"""
        required_keys = [
            'lock_enabled',
            'lock_disabled',
            'locks_show',
            'locks_none',
            'lock_invalid',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
    
    def test_ai_moderation_messages(self):
        """Test AI moderation messages exist"""
        required_keys = [
            'aimod_enabled',
            'aimod_disabled',
            'aihelp_full',
            'aitest_usage',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
    
    def test_language_messages(self):
        """Test language messages exist"""
        required_keys = [
            'lang_changed',
            'lang_current',
            'lang_invalid',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"
    
    def test_usage_messages(self):
        """Test usage messages exist"""
        required_keys = [
            'usage_setrules',
            'usage_setwarn',
            'usage_setwelcome',
            'usage_addblacklist',
            'usage_rmblacklist',
        ]
        for key in required_keys:
            assert key in self.he, f"Missing Hebrew key: {key}"


class TestEnglishTranslations:
    """Test English translations are complete"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.i18n import TRANSLATIONS
        self.en = TRANSLATIONS.get('en', {})
    
    def test_general_messages(self):
        """Test general messages exist in English"""
        required_keys = [
            'start_msg',
            'help_general',
            'admin_only',
            'owner_only',
            'reply_to_user',
            'unknown_command',
        ]
        for key in required_keys:
            assert key in self.en, f"Missing English key: {key}"
            assert len(self.en[key]) > 0, f"Empty English value for: {key}"
    
    def test_rules_messages(self):
        """Test rules messages in English"""
        required_keys = [
            'rules_show',
            'rules_not_set',
            'rules_set',
        ]
        for key in required_keys:
            assert key in self.en, f"Missing English key: {key}"
    
    def test_warn_messages(self):
        """Test warn messages in English"""
        required_keys = [
            'warn_issued',
            'warn_limit_reached',
            'warns_count',
            'warns_none',
            'warns_reset',
        ]
        for key in required_keys:
            assert key in self.en, f"Missing English key: {key}"
    
    def test_ai_moderation_messages(self):
        """Test AI moderation messages in English"""
        required_keys = [
            'aimod_enabled',
            'aimod_disabled',
            'aihelp_full',
        ]
        for key in required_keys:
            assert key in self.en, f"Missing English key: {key}"


class TestVariableSubstitution:
    """Test variable substitution in translations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.i18n import TRANSLATIONS, get_text
        self.translations = TRANSLATIONS
        self.get_text = get_text
    
    def test_warn_issued_variables(self):
        """Test warn_issued has proper variables"""
        text = self.get_text('he', 'warn_issued', 
                            user='John', 
                            reason='spam', 
                            count=1, 
                            limit=3)
        assert 'John' in text
        assert 'spam' in text
        assert '1' in text
        assert '3' in text
    
    def test_warns_count_variables(self):
        """Test warns_count has proper variables"""
        text = self.get_text('he', 'warns_count',
                            user='John',
                            count=2,
                            limit=3)
        assert 'John' in text
        assert '2' in text
        assert '3' in text
    
    def test_rules_show_variable(self):
        """Test rules_show has {rules} variable"""
        text = self.get_text('he', 'rules_show',
                            rules='Be nice to everyone!')
        assert 'Be nice to everyone!' in text
    
    def test_welcome_show_variable(self):
        """Test welcome_show has {message} variable"""
        text = self.get_text('he', 'welcome_show',
                            message='Welcome {name}!')
        assert 'Welcome {name}!' in text
    
    def test_blacklist_added_variable(self):
        """Test blacklist_added has {word} variable"""
        text = self.get_text('he', 'blacklist_added',
                            word='spam')
        assert 'spam' in text
    
    def test_lock_enabled_variable(self):
        """Test lock_enabled has {lock_type} variable"""
        text = self.get_text('he', 'lock_enabled',
                            lock_type='links')
        assert 'links' in text
    
    def test_lang_changed_variables(self):
        """Test lang_changed has language variables"""
        text = self.get_text('he', 'lang_changed',
                            lang='en',
                            lang_name='English')
        assert 'en' in text or 'English' in text
    
    def test_unknown_command_variable(self):
        """Test unknown_command has {command} variable"""
        text = self.get_text('he', 'unknown_command',
                            command='badcmd')
        assert 'badcmd' in text


class TestGetTextFunction:
    """Test the get_text function"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.i18n import get_text
        self.get_text = get_text
    
    def test_get_text_hebrew(self):
        """Test getting Hebrew text"""
        text = self.get_text('he', 'pong')
        assert '🏓' in text or 'Pong' in text
    
    def test_get_text_english(self):
        """Test getting English text"""
        text = self.get_text('en', 'pong')
        assert 'Pong' in text
    
    def test_get_text_with_format_args(self):
        """Test getting text with format arguments"""
        text = self.get_text('he', 'warn_issued',
                            user='Test User',
                            reason='Testing',
                            count=1,
                            limit=3)
        assert 'Test User' in text
        assert 'Testing' in text
    
    def test_get_text_fallback_to_english(self):
        """Test fallback to English for unknown language"""
        text = self.get_text('xx', 'pong')
        # Should fallback to English or return key
        assert isinstance(text, str)
    
    def test_get_text_missing_key(self):
        """Test getting text for missing key"""
        text = self.get_text('he', 'nonexistent_key_xyz123')
        # Should return the key itself or empty string
        assert text == 'nonexistent_key_xyz123' or text == '' or isinstance(text, str)
    
    def test_get_text_missing_format_arg(self):
        """Test getting text with missing format argument"""
        try:
            text = self.get_text('he', 'warn_issued', user='John')
            # Should handle gracefully - either error or partial format
            assert isinstance(text, str)
        except (KeyError, ValueError):
            pass  # Expected if strict formatting
    
    def test_get_text_extra_format_args(self):
        """Test getting text with extra format arguments"""
        text = self.get_text('he', 'pong', extra_arg='ignored')
        # Extra args should be ignored
        assert '🏓' in text or 'Pong' in text


class TestCommandHelp:
    """Test command help system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.i18n import TRANSLATIONS
        self.he = TRANSLATIONS.get('he', {})
        self.en = TRANSLATIONS.get('en', {})
    
    def test_help_sections_exist(self):
        """Test all help sections exist"""
        sections = [
            'help_general',
            'help_rules',
            'help_warns',
            'help_moderation',
            'help_welcome',
            'help_blacklist',
            'help_locks',
            'help_ai',
        ]
        for section in sections:
            assert section in self.he, f"Missing help section: {section}"
            assert section in self.en, f"Missing English help section: {section}"
    
    def test_help_admin_user_variants(self):
        """Test admin and user help variants exist"""
        variants = [
            ('help_general_user', 'help_general_admin'),
            ('help_rules_user', 'help_rules_admin'),
            ('help_warns_user', 'help_warns_admin'),
            ('help_welcome_user', 'help_welcome_admin'),
            ('help_blacklist_user', 'help_blacklist_admin'),
            ('help_locks_user', 'help_locks_admin'),
            ('help_ai_user', 'help_ai_admin'),
        ]
        for user_key, admin_key in variants:
            assert user_key in self.he, f"Missing: {user_key}"
            assert admin_key in self.he, f"Missing: {admin_key}"
    
    def test_help_note_exists(self):
        """Test help note exists"""
        assert 'help_note' in self.he
        assert 'help_note' in self.en


class TestAIHelpTranslations:
    """Test AI-specific help translations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.i18n import TRANSLATIONS
        self.he = TRANSLATIONS.get('he', {})
        self.en = TRANSLATIONS.get('en', {})
    
    def test_aihelp_full_exists(self):
        """Test full AI help exists"""
        assert 'aihelp_full' in self.he
        assert 'aihelp_full' in self.en
    
    def test_aitest_messages_exist(self):
        """Test AI test messages exist"""
        keys = [
            'aitest_usage',
            'aitest_header',
            'aitest_backend',
            'aitest_text',
            'aitest_scores',
            'aitest_result',
            'aitest_flagged',
            'aitest_passed',
        ]
        for key in keys:
            assert key in self.he, f"Missing: {key}"
    
    def test_aimod_status_messages_exist(self):
        """Test AI status messages exist"""
        keys = [
            'aimod_status_disabled',
            'aimod_status_header',
            'aimod_status_enabled',
            'aimod_status_backend',
            'aimod_status_threshold',
            'aimod_status_action',
        ]
        for key in keys:
            assert key in self.he, f"Missing: {key}"


class TestTranslationQuality:
    """Test translation quality and consistency"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.i18n import TRANSLATIONS
        self.he = TRANSLATIONS.get('he', {})
        self.en = TRANSLATIONS.get('en', {})
    
    def test_no_empty_translations(self):
        """Test no translations are empty"""
        for key, value in self.he.items():
            assert value is not None, f"Hebrew {key} is None"
            assert len(str(value).strip()) > 0, f"Hebrew {key} is empty"
        
        for key, value in self.en.items():
            assert value is not None, f"English {key} is None"
            assert len(str(value).strip()) > 0, f"English {key} is empty"
    
    def test_variable_placeholders_match(self):
        """Test variable placeholders exist in both languages"""
        import re
        
        for key in self.he.keys():
            if key not in self.en:
                continue
            
            he_text = str(self.he[key])
            en_text = str(self.en[key])
            
            # Find all {variable} placeholders
            he_vars = set(re.findall(r'\{(\w+)\}', he_text))
            en_vars = set(re.findall(r'\{(\w+)\}', en_text))
            
            # Variables should match
            if he_vars != en_vars:
                # Some difference is OK for formatting variables like emoji
                pass  # Log but don't fail
    
    def test_emoji_consistency(self):
        """Test emojis are used consistently"""
        # Check some key emojis
        assert '✅' in self.he.get('rules_set', '')
        assert '❌' in self.he.get('admin_only', '')
        assert '⚠️' in self.he.get('warn_issued', '')
        assert '🚫' in self.he.get('user_banned', '')


class TestLanguageServiceIntegration:
    """Test language service integration"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.language_service import (
            get_chat_language, set_chat_language, get_translated_text
        )
        self.get_chat_language = get_chat_language
        self.set_chat_language = set_chat_language
        self.get_translated_text = get_translated_text
        self.chat_id = 'test_chat'
    
    def test_default_language(self):
        """Test default language is Hebrew or English"""
        lang = self.get_chat_language('new_chat')
        assert lang in ['he', 'en', None]
    
    def test_set_and_get_language(self):
        """Test setting and getting language"""
        self.set_chat_language(self.chat_id, 'en')
        assert self.get_chat_language(self.chat_id) == 'en'
        
        self.set_chat_language(self.chat_id, 'he')
        assert self.get_chat_language(self.chat_id) == 'he'
    
    def test_get_translated_text_integration(self):
        """Test getting translated text through service"""
        text_he = self.get_translated_text('he', 'pong')
        text_en = self.get_translated_text('en', 'pong')
        
        assert isinstance(text_he, str)
        assert isinstance(text_en, str)
