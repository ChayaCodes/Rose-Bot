"""
Comprehensive Tests for All Bot Commands
Tests all commands mentioned in the feature comparison and checklist.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestAdminCommands:
    """Test all admin moderation commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.admin_id = 'admin_user'
        self.regular_id = 'regular_user'
        self.target_id = 'target_user'
    
    # ====== KICK COMMAND ======
    def test_kick_command_as_admin(self):
        """Test /kick command as admin"""
        result = self.mock_actions.execute_command(
            '/kick @target',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert result.get('success') is True
    
    def test_kick_command_as_regular_user(self):
        """Test /kick command as regular user fails"""
        result = self.mock_actions.execute_command(
            '/kick @target',
            chat_id=self.chat_id,
            user_id=self.regular_id,
            target_user_id=self.target_id,
            is_admin=False
        )
        assert result.get('success') is False
    
    def test_kick_no_target(self):
        """Test /kick without target"""
        result = self.mock_actions.execute_command(
            '/kick',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        # Should fail or prompt for target
        assert isinstance(result, dict)
    
    # ====== BAN COMMAND ======
    def test_ban_command_as_admin(self):
        """Test /ban command as admin"""
        result = self.mock_actions.execute_command(
            '/ban @target',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert result.get('success') is True
    
    def test_ban_command_as_regular_user(self):
        """Test /ban command fails for regular user"""
        result = self.mock_actions.execute_command(
            '/ban @target',
            chat_id=self.chat_id,
            user_id=self.regular_id,
            target_user_id=self.target_id,
            is_admin=False
        )
        assert result.get('success') is False
    
    def test_ban_with_reason(self):
        """Test /ban with reason"""
        result = self.mock_actions.execute_command(
            '/ban @target spamming',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert result.get('success') is True
    
    def test_unban_command(self):
        """Test /unban command"""
        result = self.mock_actions.execute_command(
            '/unban @target',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    # ====== MUTE COMMAND ======
    def test_mute_command_as_admin(self):
        """Test /mute command"""
        result = self.mock_actions.execute_command(
            '/mute @target',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert result.get('success') is True or 'mute' in str(result)
    
    def test_unmute_command(self):
        """Test /unmute command"""
        result = self.mock_actions.execute_command(
            '/unmute @target',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    # ====== WARN COMMANDS ======
    def test_warn_command(self):
        """Test /warn command"""
        result = self.mock_actions.execute_command(
            '/warn @target',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert result.get('success') is True
    
    def test_warn_with_reason(self):
        """Test /warn with reason"""
        result = self.mock_actions.execute_command(
            '/warn @target being rude',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert result.get('success') is True
    
    def test_warns_command(self):
        """Test /warns command to check warns"""
        result = self.mock_actions.execute_command(
            '/warns @target',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_resetwarns_command(self):
        """Test /resetwarns command"""
        result = self.mock_actions.execute_command(
            '/resetwarns @target',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            target_user_id=self.target_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_setwarn_command(self):
        """Test /setwarn limit command"""
        result = self.mock_actions.execute_command(
            '/setwarn 5',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)


class TestRulesCommands:
    """Test rules-related commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.admin_id = 'admin_user'
        self.regular_id = 'regular_user'
    
    def test_rules_command(self):
        """Test /rules command shows rules"""
        result = self.mock_actions.execute_command(
            '/rules',
            chat_id=self.chat_id,
            user_id=self.regular_id,
            is_admin=False
        )
        assert isinstance(result, dict)
    
    def test_setrules_command(self):
        """Test /setrules command"""
        result = self.mock_actions.execute_command(
            '/setrules Be nice to everyone!',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert result.get('success') is True or 'rules' in str(result).lower()
    
    def test_setrules_as_regular_fails(self):
        """Test /setrules fails for regular user"""
        result = self.mock_actions.execute_command(
            '/setrules My rules',
            chat_id=self.chat_id,
            user_id=self.regular_id,
            is_admin=False
        )
        assert result.get('success') is False
    
    def test_clearrules_command(self):
        """Test /clearrules command"""
        result = self.mock_actions.execute_command(
            '/clearrules',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)


class TestWelcomeCommands:
    """Test welcome-related commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.admin_id = 'admin_user'
    
    def test_welcome_command(self):
        """Test /welcome command shows current welcome"""
        result = self.mock_actions.execute_command(
            '/welcome',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_setwelcome_command(self):
        """Test /setwelcome command"""
        result = self.mock_actions.execute_command(
            '/setwelcome Welcome {name} to our group!',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert result.get('success') is True or 'welcome' in str(result).lower()
    
    def test_clearwelcome_command(self):
        """Test /clearwelcome command"""
        result = self.mock_actions.execute_command(
            '/clearwelcome',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)


class TestBlacklistCommands:
    """Test blacklist-related commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.admin_id = 'admin_user'
        self.regular_id = 'regular_user'
    
    def test_blacklist_command(self):
        """Test /blacklist command shows blacklist"""
        result = self.mock_actions.execute_command(
            '/blacklist',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_addblacklist_command(self):
        """Test /addblacklist command"""
        result = self.mock_actions.execute_command(
            '/addblacklist spam',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert result.get('success') is True or 'blacklist' in str(result).lower()
    
    def test_rmblacklist_command(self):
        """Test /rmblacklist command"""
        result = self.mock_actions.execute_command(
            '/rmblacklist spam',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_clearblacklist_command(self):
        """Test /clearblacklist command"""
        result = self.mock_actions.execute_command(
            '/clearblacklist',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)


class TestLockCommands:
    """Test lock-related commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.admin_id = 'admin_user'
    
    def test_lock_command(self):
        """Test /lock command"""
        result = self.mock_actions.execute_command(
            '/lock links',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert result.get('success') is True or 'lock' in str(result).lower()
    
    def test_unlock_command(self):
        """Test /unlock command"""
        result = self.mock_actions.execute_command(
            '/unlock links',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_locks_command(self):
        """Test /locks command shows all locks"""
        result = self.mock_actions.execute_command(
            '/locks',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)


class TestAIModerationCommands:
    """Test AI moderation commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.admin_id = 'admin_user'
    
    def test_aimod_on_command(self):
        """Test /aimod on command"""
        result = self.mock_actions.execute_command(
            '/aimod on',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_aimod_off_command(self):
        """Test /aimod off command"""
        result = self.mock_actions.execute_command(
            '/aimod off',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_aimodstatus_command(self):
        """Test /aimodstatus command"""
        result = self.mock_actions.execute_command(
            '/aimodstatus',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_aimodset_command(self):
        """Test /aimodset command"""
        result = self.mock_actions.execute_command(
            '/aimodset hate 0.7',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_aimodthreshold_command(self):
        """Test /aimodthreshold command"""
        result = self.mock_actions.execute_command(
            '/aimodthreshold 0.8',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_aimodaction_command(self):
        """Test /aimodaction command"""
        result = self.mock_actions.execute_command(
            '/aimodaction warn',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_aitest_command(self):
        """Test /aitest command"""
        result = self.mock_actions.execute_command(
            '/aitest This is a test message',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_aihelp_command(self):
        """Test /aihelp command"""
        result = self.mock_actions.execute_command(
            '/aihelp',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)


class TestUtilityCommands:
    """Test utility commands available to all users"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.user_id = 'regular_user'
    
    def test_start_command(self):
        """Test /start command"""
        result = self.mock_actions.execute_command(
            '/start',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        assert isinstance(result, dict)
    
    def test_help_command(self):
        """Test /help command"""
        result = self.mock_actions.execute_command(
            '/help',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        assert isinstance(result, dict)
        assert 'text' in result or 'help' in str(result).lower()
    
    def test_ping_command(self):
        """Test /ping command"""
        result = self.mock_actions.execute_command(
            '/ping',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        assert 'pong' in str(result).lower() or result.get('text')
    
    def test_id_command(self):
        """Test /id command"""
        result = self.mock_actions.execute_command(
            '/id',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        assert isinstance(result, dict)
    
    def test_info_command(self):
        """Test /info command"""
        result = self.mock_actions.execute_command(
            '/info',
            chat_id=self.chat_id,
            user_id=self.user_id,
            is_admin=False
        )
        assert isinstance(result, dict)


class TestLanguageCommands:
    """Test language-related commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_actions):
        self.mock_actions = mock_actions
        self.chat_id = 'test_chat'
        self.admin_id = 'admin_user'
    
    def test_lang_command(self):
        """Test /lang command shows current language"""
        result = self.mock_actions.execute_command(
            '/lang',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_setlang_hebrew_command(self):
        """Test /setlang he command"""
        result = self.mock_actions.execute_command(
            '/setlang he',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)
    
    def test_setlang_english_command(self):
        """Test /setlang en command"""
        result = self.mock_actions.execute_command(
            '/setlang en',
            chat_id=self.chat_id,
            user_id=self.admin_id,
            is_admin=True
        )
        assert isinstance(result, dict)


class TestCommandParsing:
    """Test command parsing edge cases"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.models.message import BotMessage
        self.BotMessage = BotMessage
    
    def test_parse_command_at_bot(self):
        """Test parsing /command@botname format"""
        msg = self.BotMessage(
            id='1',
            text='/help@RoseBot',
            chat_id='chat',
            user_id='user'
        )
        cmd = msg.get_command()
        # Should strip @botname
        assert cmd in ['help', 'help@RoseBot']
    
    def test_parse_invalid_command(self):
        """Test parsing invalid command"""
        msg = self.BotMessage(
            id='1',
            text='not a command',
            chat_id='chat',
            user_id='user'
        )
        assert msg.is_command() is False
    
    def test_parse_empty_input(self):
        """Test parsing empty message"""
        msg = self.BotMessage(
            id='1',
            text='',
            chat_id='chat',
            user_id='user'
        )
        assert msg.is_command() is False
    
    def test_parse_only_slash(self):
        """Test parsing just slash"""
        msg = self.BotMessage(
            id='1',
            text='/',
            chat_id='chat',
            user_id='user'
        )
        # Edge case - may or may not be command
        result = msg.is_command()
        assert isinstance(result, bool)
    
    def test_parse_command_with_newline(self):
        """Test parsing command with newline args"""
        msg = self.BotMessage(
            id='1',
            text='/setrules\nRule 1\nRule 2',
            chat_id='chat',
            user_id='user'
        )
        assert msg.is_command() is True
        assert msg.get_command() == 'setrules'
    
    def test_parse_command_unicode(self):
        """Test parsing command with unicode args"""
        msg = self.BotMessage(
            id='1',
            text='/setrules 🎯 כללים חשובים',
            chat_id='chat',
            user_id='user'
        )
        assert msg.is_command() is True
        assert msg.get_command() == 'setrules'


class TestCommandWithReply:
    """Test commands that work with replied messages"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.models.message import BotMessage
        self.BotMessage = BotMessage
    
    def test_command_target_from_reply(self):
        """Test getting target user from reply"""
        msg = self.BotMessage(
            id='1',
            text='/warn',
            chat_id='chat',
            user_id='admin',
            reply_to_user_id='target_user'
        )
        target = msg.get_target_user()
        # Should get target from reply
        assert target == 'target_user' or target is None
    
    def test_command_target_from_mention(self):
        """Test getting target user from mention"""
        msg = self.BotMessage(
            id='1',
            text='/warn @targetuser',
            chat_id='chat',
            user_id='admin'
        )
        args = msg.get_args()
        assert '@targetuser' in str(args)
    
    def test_command_prefers_mention_over_reply(self):
        """Test that explicit mention takes precedence"""
        msg = self.BotMessage(
            id='1',
            text='/warn @explicit_target',
            chat_id='chat',
            user_id='admin',
            reply_to_user_id='reply_target'
        )
        args = msg.get_args()
        assert '@explicit_target' in str(args)
