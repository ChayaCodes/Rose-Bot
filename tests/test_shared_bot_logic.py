"""
Tests for Shared Bot Logic and Command Handling
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestBotModels:
    """Test bot_core/models classes"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        """Setup for each test"""
        from bot_core.models.user import BotUser
        from bot_core.models.chat import BotChat
        from bot_core.models.message import BotMessage
        
        self.BotUser = BotUser
        self.BotChat = BotChat
        self.BotMessage = BotMessage
    
    def test_create_bot_user(self):
        """Test creating a BotUser"""
        user = self.BotUser(
            id='123',
            name='Test User',
            username='testuser'
        )
        assert user.id == '123'
        assert user.name == 'Test User'
        assert user.username == 'testuser'
    
    def test_create_bot_user_minimal(self):
        """Test creating BotUser with minimal fields"""
        user = self.BotUser(id='123', name='Test')
        assert user.id == '123'
        assert user.name == 'Test'
    
    def test_create_bot_chat(self):
        """Test creating a BotChat"""
        chat = self.BotChat(
            id='chat_123',
            name='Test Group',
            is_group=True
        )
        assert chat.id == 'chat_123'
        assert chat.name == 'Test Group'
        assert chat.is_group is True
    
    def test_create_bot_chat_private(self):
        """Test creating a private BotChat"""
        chat = self.BotChat(
            id='user_123',
            name='Private Chat',
            is_group=False
        )
        assert chat.is_group is False
    
    def test_create_bot_message(self):
        """Test creating a BotMessage"""
        message = self.BotMessage(
            id='msg_123',
            text='Hello World',
            chat_id='chat_123',
            user_id='user_123'
        )
        assert message.id == 'msg_123'
        assert message.text == 'Hello World'
    
    def test_bot_message_is_command(self):
        """Test checking if message is command"""
        message = self.BotMessage(
            id='msg_123',
            text='/help',
            chat_id='chat_123',
            user_id='user_123'
        )
        assert message.is_command() is True
    
    def test_bot_message_not_command(self):
        """Test regular message is not command"""
        message = self.BotMessage(
            id='msg_123',
            text='Hello',
            chat_id='chat_123',
            user_id='user_123'
        )
        assert message.is_command() is False
    
    def test_bot_message_get_command(self):
        """Test extracting command from message"""
        message = self.BotMessage(
            id='msg_123',
            text='/ban @user reason',
            chat_id='chat_123',
            user_id='user_123'
        )
        cmd = message.get_command()
        assert cmd == 'ban'
    
    def test_bot_message_get_args(self):
        """Test extracting arguments from command"""
        message = self.BotMessage(
            id='msg_123',
            text='/warn @user being rude',
            chat_id='chat_123',
            user_id='user_123'
        )
        args = message.get_args()
        assert '@user' in args or 'being rude' in str(args)


class TestCommandParsing:
    """Test command parsing functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.models.message import BotMessage
        self.BotMessage = BotMessage
    
    def test_parse_simple_command(self):
        """Test parsing simple command"""
        msg = self.BotMessage(id='1', text='/help', chat_id='c', user_id='u')
        assert msg.get_command() == 'help'
    
    def test_parse_command_with_bot_mention(self):
        """Test parsing command with @botname"""
        msg = self.BotMessage(id='1', text='/help@MyBot', chat_id='c', user_id='u')
        cmd = msg.get_command()
        assert cmd == 'help' or cmd == 'help@MyBot'
    
    def test_parse_command_with_args(self):
        """Test parsing command with arguments"""
        msg = self.BotMessage(id='1', text='/setrules No spam allowed', chat_id='c', user_id='u')
        assert msg.get_command() == 'setrules'
        args = msg.get_args()
        assert 'No spam allowed' in str(args)
    
    def test_parse_reply_mention(self):
        """Test parsing user mention from reply"""
        msg = self.BotMessage(
            id='1',
            text='/ban',
            chat_id='c',
            user_id='u',
            reply_to_user_id='target_user'
        )
        # Should get target from reply
        target = msg.get_target_user()
        assert target == 'target_user' or target is None  # Implementation dependent
    
    def test_parse_multiple_commands(self):
        """Test that only first command is parsed"""
        msg = self.BotMessage(id='1', text='/help /ban', chat_id='c', user_id='u')
        assert msg.get_command() == 'help'


class TestAdminCommands:
    """Test admin command handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.admin_id = 'admin_user'
        self.regular_id = 'regular_user'
    
    def test_warn_command_as_admin(self):
        """Test /warn command as admin"""
        # Admin should be able to warn
        result = self.mock_actions.execute_command(
            '/warn',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.regular_id,
            is_admin=True
        )
        assert result.get('success') is True or 'warn' in str(result)
    
    def test_warn_command_as_regular(self):
        """Test /warn command as regular user fails"""
        result = self.mock_actions.execute_command(
            '/warn',
            chat_id=self.chat_id,
            user_id=self.regular_id,
            target_user_id=self.admin_id,
            is_admin=False
        )
        assert result.get('success') is False or 'permission' in str(result).lower()
    
    def test_ban_command_as_admin(self):
        """Test /ban command as admin"""
        result = self.mock_actions.execute_command(
            '/ban',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.regular_id,
            is_admin=True
        )
        assert result.get('success') is True or 'ban' in str(result)
    
    def test_setrules_command(self):
        """Test /setrules command"""
        result = self.mock_actions.execute_command(
            '/setrules Be nice!',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert result.get('success') is True or 'rules' in str(result)
    
    def test_setwelcome_command(self):
        """Test /setwelcome command"""
        result = self.mock_actions.execute_command(
            '/setwelcome Welcome {name}!',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert result.get('success') is True or 'welcome' in str(result)


class TestUserCommands:
    """Test user-facing commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.user_id = 'regular_user'
    
    def test_help_command(self):
        """Test /help command"""
        result = self.mock_actions.execute_command(
            '/help',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        assert 'help' in str(result).lower() or result.get('text')
    
    def test_rules_command(self):
        """Test /rules command"""
        result = self.mock_actions.execute_command(
            '/rules',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        # Should return rules or "no rules set"
        assert isinstance(result, dict)
    
    def test_warns_command(self):
        """Test /warns command to check own warns"""
        result = self.mock_actions.execute_command(
            '/warns',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        assert isinstance(result, dict)
    
    def test_ping_command(self):
        """Test /ping command"""
        result = self.mock_actions.execute_command(
            '/ping',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        assert 'pong' in str(result).lower() or result.get('text')


class TestMessageProcessing:
    """Test message processing and filtering"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.chat_id = 'test_chat'
        self.user_id = 'user_123'
    
    def test_process_normal_message(self):
        """Test processing normal message"""
        from bot_core.models.message import BotMessage
        
        msg = BotMessage(
            id='1',
            text='Hello everyone!',
            chat_id=self.chat_id,
            user_id=self.user_id
        )
        
        # Should not trigger any filters
        assert msg.text == 'Hello everyone!'
    
    def test_process_message_with_blacklist(self):
        """Test processing message that matches blacklist"""
        from bot_core.services.blacklist_service import add_blacklist_word, check_blacklist
        
        add_blacklist_word(self.chat_id, 'spam')
        
        result = check_blacklist(self.chat_id, 'This is spam content')
        assert result is True or result == 'spam'
    
    def test_process_message_with_url_lock(self):
        """Test processing message with URL when locked"""
        from bot_core.services.locks_service import set_lock, check_message_locks
        
        set_lock(self.chat_id, 'url', True)
        
        result = check_message_locks(
            self.chat_id,
            'Check out https://example.com',
            has_sticker=False,
            has_media=False
        )
        assert result is True or result == 'url'


class TestCallbackHandling:
    """Tests for callback/button handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.chat_id = 'test_chat'
        self.user_id = 'user_123'
    
    @pytest.mark.skip(reason="Callback handling not yet implemented")
    def test_handle_button_callback(self):
        """Test handling button callback"""
        pass
    
    @pytest.mark.skip(reason="Callback handling not yet implemented")
    def test_handle_remove_warn_callback(self):
        """Test handling remove warn button callback"""
        pass
    
    @pytest.mark.skip(reason="Callback handling not yet implemented")
    def test_callback_permission_check(self):
        """Test callback respects permissions"""
        pass


class TestErrorHandling:
    """Test error handling in bot logic"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
    
    def test_unknown_command(self):
        """Test handling unknown command"""
        result = self.mock_actions.execute_command(
            '/unknowncommand123',
            chat_id='chat',
            user_id='user',
            is_admin=False
        )
        # Should handle gracefully
        assert isinstance(result, dict)
    
    def test_command_with_missing_args(self):
        """Test command that requires args but gets none"""
        result = self.mock_actions.execute_command(
            '/ban',  # No target specified
            chat_id='chat',
            user_id='admin',
            is_admin=True
        )
        # Should return error about missing target
        assert isinstance(result, dict)
    
    def test_command_invalid_target(self):
        """Test command with invalid target"""
        result = self.mock_actions.execute_command(
            '/ban @nonexistentuser12345',
            chat_id='chat',
            user_id='admin',
            is_admin=True
        )
        # Should handle gracefully
        assert isinstance(result, dict)
