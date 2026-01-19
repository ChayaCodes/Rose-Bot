"""
Tests for AI Moderation Service
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot_core.services.ai_moderation_service import (
    get_ai_settings,
    set_ai_enabled,
    set_ai_backend,
    set_ai_threshold,
    set_ai_action,
    check_content_toxicity,
    SUPPORTED_BACKENDS
)


class TestAIModerationService(unittest.TestCase):
    """Test AI Moderation service functions"""
    
    def test_supported_backends(self):
        """Test that supported backends are correct"""
        self.assertIn('detoxify', SUPPORTED_BACKENDS)
        self.assertIn('perspective', SUPPORTED_BACKENDS)
        self.assertIn('openai', SUPPORTED_BACKENDS)
        self.assertIn('azure', SUPPORTED_BACKENDS)
        self.assertNotIn('rules', SUPPORTED_BACKENDS)  # Rules should be removed
    
    def test_default_settings(self):
        """Test default AI settings"""
        settings = get_ai_settings('test_chat_123')
        
        self.assertEqual(settings['enabled'], False)
        self.assertEqual(settings['backend'], 'detoxify')
        self.assertEqual(settings['threshold'], 0.7)
        self.assertEqual(settings['action'], 'warn')
    
    def test_backend_validation(self):
        """Test backend validation"""
        # Valid backend
        result = set_ai_backend('test_chat_123', 'detoxify')
        self.assertTrue(result)
        
        # Invalid backend
        result = set_ai_backend('test_chat_123', 'invalid_backend')
        self.assertFalse(result)
    
    @patch('bot_core.services.ai_backends.detoxify_backend.Detoxify')
    def test_detoxify_backend(self, mock_detoxify):
        """Test Detoxify backend"""
        # Mock Detoxify response
        mock_model = Mock()
        mock_model.predict.return_value = {
            'toxicity': 0.8,
            'severe_toxicity': 0.1,
            'obscene': 0.2,
            'threat': 0.1,
            'insult': 0.7,
            'identity_attack': 0.1
        }
        mock_detoxify.return_value = mock_model
        
        result = check_content_toxicity("test toxic text", backend='detoxify', threshold=0.7)
        
        self.assertTrue(result['is_toxic'])
        self.assertEqual(result['backend'], 'detoxify')
        self.assertGreaterEqual(result['score'], 0.7)


class TestAIBackends(unittest.TestCase):
    """Test individual AI backends"""
    
    def test_detoxify_backend_import(self):
        """Test that Detoxify backend can be imported"""
        try:
            from bot_core.services.ai_backends import DetoxifyBackend
            backend = DetoxifyBackend()
            self.assertEqual(backend.name, 'detoxify')
            self.assertFalse(backend.requires_api_key)
        except ImportError as e:
            self.skipTest(f"Detoxify not installed: {e}")
    
    def test_perspective_backend_import(self):
        """Test that Perspective backend can be imported"""
        from bot_core.services.ai_backends import PerspectiveBackend
        backend = PerspectiveBackend()
        self.assertEqual(backend.name, 'perspective')
        self.assertTrue(backend.requires_api_key)
    
    def test_openai_backend_import(self):
        """Test that OpenAI backend can be imported"""
        from bot_core.services.ai_backends import OpenAIBackend
        backend = OpenAIBackend()
        self.assertEqual(backend.name, 'openai')
        self.assertTrue(backend.requires_api_key)
    
    def test_azure_backend_import(self):
        """Test that Azure backend can be imported"""
        from bot_core.services.ai_backends import AzureBackend
        backend = AzureBackend()
        self.assertEqual(backend.name, 'azure')
        self.assertTrue(backend.requires_api_key)


if __name__ == '__main__':
    unittest.main()
