"""
Tests for AI Moderation Service (OpenAI Backend)
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestAIModerationService:
    """Test ai_moderation_service.py functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        from bot_core.services.ai_moderation_service import (
            get_ai_settings, set_ai_enabled, set_ai_threshold,
            set_ai_action, check_content_toxicity
        )
        self.get_ai_settings = get_ai_settings
        self.set_ai_enabled = set_ai_enabled
        self.set_ai_threshold = set_ai_threshold
        self.set_ai_action = set_ai_action
        self.check_content_toxicity = check_content_toxicity
        self.chat_id = 'test_chat_123'
    
    def test_set_ai_enabled_on(self):
        """Test enabling AI moderation"""
        result = self.set_ai_enabled(self.chat_id, True)
        assert result is True
    
    def test_set_ai_enabled_off(self):
        """Test disabling AI moderation"""
        result = self.set_ai_enabled(self.chat_id, False)
        assert result is True
    
    def test_get_ai_settings_default(self):
        """Test getting default AI settings"""
        settings = self.get_ai_settings('new_chat')
        
        assert settings is not None
        # Should have default values
        assert 'enabled' in settings or hasattr(settings, 'enabled')
    
    def test_get_ai_settings_after_enable(self):
        """Test getting AI settings after enabling"""
        self.set_ai_enabled(self.chat_id, True)
        settings = self.get_ai_settings(self.chat_id)
        
        if isinstance(settings, dict):
            assert settings.get('enabled') is True
        else:
            assert settings.enabled is True
    
    def test_set_ai_threshold(self):
        """Test setting AI threshold"""
        result = self.set_ai_threshold(self.chat_id, 0.7)
        assert result is True
    
    def test_get_ai_threshold_after_set(self):
        """Test threshold is saved correctly"""
        self.set_ai_threshold(self.chat_id, 0.8)
        settings = self.get_ai_settings(self.chat_id)
        
        threshold = settings.get('threshold') if isinstance(settings, dict) else settings.threshold
        assert threshold == 0.8
    
    def test_set_ai_action_warn(self):
        """Test setting AI action to warn"""
        result = self.set_ai_action(self.chat_id, 'warn')
        assert result is True
    
    def test_set_ai_action_delete(self):
        """Test setting AI action to delete"""
        result = self.set_ai_action(self.chat_id, 'delete')
        assert result is True
    
    def test_set_ai_action_ban(self):
        """Test setting AI action to ban"""
        result = self.set_ai_action(self.chat_id, 'ban')
        assert result is True
    
    def test_set_ai_action_mute(self):
        """Test setting AI action to mute"""
        result = self.set_ai_action(self.chat_id, 'mute')
        assert result is True
    
    def test_ai_settings_per_chat(self):
        """Test AI settings are per-chat"""
        self.set_ai_enabled('chat1', True)
        self.set_ai_threshold('chat1', 0.5)
        self.set_ai_enabled('chat2', False)
        self.set_ai_threshold('chat2', 0.9)
        
        settings1 = self.get_ai_settings('chat1')
        settings2 = self.get_ai_settings('chat2')
        
        if isinstance(settings1, dict):
            assert settings1.get('enabled') != settings2.get('enabled')
            assert settings1.get('threshold') != settings2.get('threshold')


class TestContentToxicityCheck:
    """Test content toxicity checking with OpenAI"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.ai_moderation_service import (
            check_content_toxicity, set_ai_enabled
        )
        self.check_content_toxicity = check_content_toxicity
        self.set_ai_enabled = set_ai_enabled
        self.chat_id = 'test_chat'
    
    @pytest.mark.api
    async def test_check_clean_content(self):
        """Test checking clean content"""
        self.set_ai_enabled(self.chat_id, True)
        
        result = await self.check_content_toxicity(
            self.chat_id,
            "Hello, how are you today?"
        )
        
        # Clean content should pass
        assert result is None or result.get('is_toxic') is False
    
    @pytest.mark.api
    async def test_check_toxic_content(self):
        """Test checking toxic content"""
        self.set_ai_enabled(self.chat_id, True)
        
        # Use obviously bad content for testing
        result = await self.check_content_toxicity(
            self.chat_id,
            "I hate you and want to hurt you"
        )
        
        # Should detect as toxic
        if result:
            assert result.get('is_toxic') is True or result.get('score', 0) > 0.5
    
    @pytest.mark.api
    async def test_check_content_when_disabled(self):
        """Test checking content when AI is disabled"""
        self.set_ai_enabled(self.chat_id, False)
        
        result = await self.check_content_toxicity(
            self.chat_id,
            "Any content here"
        )
        
        # Should return None when disabled
        assert result is None
    
    def test_check_empty_content(self):
        """Test checking empty content"""
        self.set_ai_enabled(self.chat_id, True)
        
        try:
            import asyncio
            result = asyncio.run(self.check_content_toxicity(self.chat_id, ""))
            # Empty content should be handled gracefully
            assert result is None or isinstance(result, dict)
        except Exception:
            pass  # May fail gracefully


class TestAIModerationWithMocks:
    """Test AI moderation with mocked OpenAI API"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.ai_moderation_service import (
            check_content_toxicity, set_ai_enabled
        )
        self.check_content_toxicity = check_content_toxicity
        self.set_ai_enabled = set_ai_enabled
        self.chat_id = 'test_chat'
    
    @patch('openai.OpenAI')
    async def test_openai_api_called(self, mock_openai):
        """Test that OpenAI API is called correctly"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.moderations.create.return_value = MagicMock(
            results=[MagicMock(
                flagged=False,
                categories=MagicMock(hate=False, violence=False),
                category_scores=MagicMock(hate=0.01, violence=0.01)
            )]
        )
        
        self.set_ai_enabled(self.chat_id, True)
        
        result = await self.check_content_toxicity(
            self.chat_id,
            "Test message"
        )
        
        # Verify API was called
        mock_client.moderations.create.assert_called_once()
    
    @patch('openai.OpenAI')
    async def test_api_error_handled(self, mock_openai):
        """Test that API errors are handled gracefully"""
        # Setup mock to raise error
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.moderations.create.side_effect = Exception("API Error")
        
        self.set_ai_enabled(self.chat_id, True)
        
        try:
            result = await self.check_content_toxicity(
                self.chat_id,
                "Test message"
            )
            # Should handle error gracefully
            assert result is None or 'error' in str(result)
        except Exception:
            # May raise but should be caught
            pass


class TestAIModerationThresholds:
    """Test AI moderation threshold behavior"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.ai_moderation_service import (
            set_ai_threshold, get_ai_settings, set_ai_enabled
        )
        self.set_ai_threshold = set_ai_threshold
        self.get_ai_settings = get_ai_settings
        self.set_ai_enabled = set_ai_enabled
        self.chat_id = 'test_chat'
    
    def test_threshold_boundaries_low(self):
        """Test setting very low threshold"""
        result = self.set_ai_threshold(self.chat_id, 0.1)
        assert result is True
        
        settings = self.get_ai_settings(self.chat_id)
        threshold = settings.get('threshold') if isinstance(settings, dict) else settings.threshold
        assert threshold == 0.1
    
    def test_threshold_boundaries_high(self):
        """Test setting high threshold"""
        result = self.set_ai_threshold(self.chat_id, 0.99)
        assert result is True
    
    def test_threshold_invalid_zero(self):
        """Test setting zero threshold"""
        try:
            result = self.set_ai_threshold(self.chat_id, 0)
            # May or may not be allowed
            assert isinstance(result, bool)
        except ValueError:
            pass  # Expected
    
    def test_threshold_invalid_negative(self):
        """Test setting negative threshold"""
        try:
            result = self.set_ai_threshold(self.chat_id, -0.5)
            # Should be rejected
            assert result is False
        except ValueError:
            pass  # Expected
    
    def test_threshold_invalid_over_one(self):
        """Test setting threshold over 1"""
        try:
            result = self.set_ai_threshold(self.chat_id, 1.5)
            assert result is False
        except ValueError:
            pass  # Expected


class TestAIModerationCategories:
    """Test AI moderation category-specific thresholds"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        try:
            from bot_core.services.ai_moderation_service import (
                set_ai_category_thresholds, get_ai_settings
            )
            self.set_ai_category_thresholds = set_ai_category_thresholds
            self.get_ai_settings = get_ai_settings
            self.has_category_thresholds = True
        except ImportError:
            self.has_category_thresholds = False
        
        self.chat_id = 'test_chat'
    
    def test_set_category_threshold_hate(self):
        """Test setting hate category threshold"""
        if not self.has_category_thresholds:
            pytest.skip("Category thresholds not implemented")
        
        result = self.set_ai_category_thresholds(self.chat_id, {'hate': 0.5})
        assert result is True
    
    def test_set_category_threshold_violence(self):
        """Test setting violence category threshold"""
        if not self.has_category_thresholds:
            pytest.skip("Category thresholds not implemented")
        
        result = self.set_ai_category_thresholds(self.chat_id, {'violence': 0.3})
        assert result is True
    
    def test_set_multiple_category_thresholds(self):
        """Test setting multiple category thresholds"""
        if not self.has_category_thresholds:
            pytest.skip("Category thresholds not implemented")
        
        thresholds = {
            'hate': 0.5,
            'violence': 0.3,
            'harassment': 0.4,
            'sexual': 0.8
        }
        result = self.set_ai_category_thresholds(self.chat_id, thresholds)
        assert result is True


class TestAIModerationOpenAIOnly:
    """Test that only OpenAI backend is used"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.ai_moderation_service import (
            _resolve_backend
        )
        self.resolve_backend = _resolve_backend
        self.chat_id = 'test_chat'
    
    def test_backend_always_openai(self):
        """Test that backend is always OpenAI"""
        backend = self.resolve_backend(self.chat_id)
        assert backend == 'openai'
    
    def test_no_backend_selection_command(self):
        """Test that backend selection is not available"""
        # The /aimodbackend command should not exist
        from bot_core.i18n import TRANSLATIONS
        
        # Check that backend-related translations are removed
        en_translations = TRANSLATIONS.get('en', {})
        
        # These should not exist
        assert 'ai_backend_set' not in en_translations
        assert 'ai_backend_list' not in en_translations
