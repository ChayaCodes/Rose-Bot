"""
Test suite for bot core functionality
Run with: python -m pytest tests/
"""

import unittest
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot_core.models import BotMessage, BotUser, BotChat
from bot_core.models.chat import ChatType


class TestBotUser(unittest.TestCase):
    """Test BotUser model"""
    
    def test_create_user(self):
        """Test creating a user"""
        user = BotUser("123", "John", "Doe", "johndoe")
        self.assertEqual(user.id, "123")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.username, "johndoe")
    
    def test_full_name(self):
        """Test full name property"""
        user = BotUser("123", "John", "Doe")
        self.assertEqual(user.full_name, "John Doe")
        
        user_no_last = BotUser("123", "John")
        self.assertEqual(user_no_last.full_name, "John")
    
    def test_mention(self):
        """Test mention property"""
        user_with_username = BotUser("123", "John", username="johndoe")
        self.assertEqual(user_with_username.mention, "@johndoe")
        
        user_no_username = BotUser("123", "John", "Doe")
        self.assertEqual(user_no_username.mention, "John Doe")


class TestBotChat(unittest.TestCase):
    """Test BotChat model"""
    
    def test_create_chat(self):
        """Test creating a chat"""
        chat = BotChat("456", ChatType.PRIVATE, first_name="John")
        self.assertEqual(chat.id, "456")
        self.assertEqual(chat.type, ChatType.PRIVATE)
        self.assertTrue(chat.is_private)
        self.assertFalse(chat.is_group)
    
    def test_group_chat(self):
        """Test group chat"""
        chat = BotChat("789", ChatType.GROUP, title="Test Group")
        self.assertTrue(chat.is_group)
        self.assertFalse(chat.is_private)
        self.assertEqual(chat.display_name, "Test Group")
    
    def test_display_name(self):
        """Test display name property"""
        chat_with_title = BotChat("1", ChatType.GROUP, title="My Group")
        self.assertEqual(chat_with_title.display_name, "My Group")
        
        chat_with_name = BotChat("2", ChatType.PRIVATE, first_name="John", last_name="Doe")
        self.assertEqual(chat_with_name.display_name, "John Doe")
        
        chat_with_username = BotChat("3", ChatType.PRIVATE, username="john123")
        self.assertEqual(chat_with_username.display_name, "@john123")


class TestBotMessage(unittest.TestCase):
    """Test BotMessage model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = BotUser("123", "John")
        self.chat = BotChat("456", ChatType.PRIVATE)
    
    def test_create_message(self):
        """Test creating a message"""
        msg = BotMessage("789", self.chat, self.user, text="Hello")
        self.assertEqual(msg.message_id, "789")
        self.assertEqual(msg.text, "Hello")
        self.assertTrue(msg.has_text)
        self.assertFalse(msg.has_media)
    
    def test_get_command(self):
        """Test command extraction"""
        msg = BotMessage("1", self.chat, self.user, text="/start")
        command_data = msg.get_command()
        self.assertIsNotNone(command_data)
        command, args = command_data
        self.assertEqual(command, "start")
        self.assertEqual(args, "")
        
        msg_with_args = BotMessage("2", self.chat, self.user, text="/echo hello world")
        command_data = msg_with_args.get_command()
        command, args = command_data
        self.assertEqual(command, "echo")
        self.assertEqual(args, "hello world")
        
        # Test with ! prefix
        msg_excl = BotMessage("3", self.chat, self.user, text="!help")
        command_data = msg_excl.get_command()
        command, args = command_data
        self.assertEqual(command, "help")
        
        # Test non-command
        msg_no_cmd = BotMessage("4", self.chat, self.user, text="hello")
        self.assertIsNone(msg_no_cmd.get_command())
    
    def test_reply_to_message(self):
        """Test reply functionality"""
        original = BotMessage("1", self.chat, self.user, text="Original")
        reply = BotMessage("2", self.chat, self.user, text="Reply", reply_to_message=original)
        
        self.assertIsNotNone(reply.reply_to_message)
        self.assertEqual(reply.reply_to_message.text, "Original")


class TestWhatsAppBridgeClient(unittest.TestCase):
    """Test WhatsApp Bridge Client"""
    
    def test_import(self):
        """Test that bridge client can be imported"""
        try:
            from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import WhatsAppBridgeClient: {e}")
    
    def test_create_client(self):
        """Test creating bridge client"""
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        
        client = WhatsAppBridgeClient("http://localhost:3000", 5001)
        self.assertEqual(client.bridge_url, "http://localhost:3000")
        self.assertEqual(client.callback_port, 5001)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBotUser))
    suite.addTests(loader.loadTestsFromTestCase(TestBotChat))
    suite.addTests(loader.loadTestsFromTestCase(TestBotMessage))
    suite.addTests(loader.loadTestsFromTestCase(TestWhatsAppBridgeClient))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
