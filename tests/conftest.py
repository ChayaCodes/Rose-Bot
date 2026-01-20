"""
Pytest configuration and fixtures for Rose Bot tests
"""
import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use in-memory SQLite for tests
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['TESTING'] = 'true'
os.environ['AI_FORCE_BACKEND'] = 'openai'


@pytest.fixture(scope='function')
def test_db():
    """Create a fresh in-memory database for each test"""
    from bot_core.database import init_db, get_session, Base, engine
    
    # Create all tables
    init_db()
    
    yield get_session()
    
    # Cleanup - drop all tables
    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_actions():
    """Mock bot actions for testing commands"""
    
    class MockActions:
        def __init__(self):
            self.messages_sent = []
            self.messages_deleted = []
            self.users_removed = []
            self.users_banned = []
            self.users_warned = []
        
        def send_message(self, chat_id, text, **kwargs):
            self.messages_sent.append({'chat_id': chat_id, 'text': text, **kwargs})
            return True
        
        def delete_message(self, chat_id, message_id):
            self.messages_deleted.append({'chat_id': chat_id, 'message_id': message_id})
            return True
        
        def remove_participant(self, chat_id, user_id):
            self.users_removed.append({'chat_id': chat_id, 'user_id': user_id})
            return True
        
        def ban_user(self, chat_id, user_id):
            self.users_banned.append({'chat_id': chat_id, 'user_id': user_id})
            return True
        
        def is_admin(self, chat_id, user_id):
            return user_id.startswith('admin')
        
        def is_owner(self, chat_id, user_id):
            return user_id == 'owner'
        
        def get_participant_info(self, chat_id, user_id):
            return {'name': 'Test User', 'id': user_id}
        
        def execute_command(self, command, chat_id, user_id, target_user_id=None, is_admin=False):
            """Execute a command and return result"""
            cmd = command.split()[0].lstrip('/')
            args = command.split()[1:] if len(command.split()) > 1 else []
            
            result = {
                'command': cmd,
                'args': args,
                'chat_id': chat_id,
                'user_id': user_id,
                'is_admin': is_admin,
                'target_user_id': target_user_id
            }
            
            # Simulate permission check
            admin_commands = ['warn', 'ban', 'mute', 'kick', 'setrules', 'setwelcome', 'lock', 'unlock']
            if cmd in admin_commands and not is_admin:
                result['success'] = False
                result['error'] = 'permission_denied'
                return result
            
            result['success'] = True
            
            # Simulate command execution
            if cmd == 'ping':
                result['text'] = 'pong!'
            elif cmd == 'help':
                result['text'] = 'Available commands: /ping, /help, /rules, /warns'
            elif cmd == 'warn' and target_user_id:
                self.users_warned.append({'chat_id': chat_id, 'user_id': target_user_id})
                result['text'] = f'User {target_user_id} has been warned'
            elif cmd == 'ban' and target_user_id:
                self.ban_user(chat_id, target_user_id)
                result['text'] = f'User {target_user_id} has been banned'
            
            return result
    
    return MockActions()


@pytest.fixture
def sample_message():
    """Create a sample message for testing"""
    return {
        'id': 'test_msg_123',
        'body': 'Hello world',
        'from': '1234567890@c.us',
        'chat_id': 'test_group@g.us',
        'author': '1234567890@c.us',
        'isGroupMsg': True,
        'quotedMsg': None,
        'timestamp': 1234567890
    }


@pytest.fixture
def command_message():
    """Create a sample command message"""
    return {
        'id': 'cmd_msg_123',
        'body': '/help',
        'from': '1234567890@c.us',
        'chat_id': 'test_group@g.us',
        'author': '1234567890@c.us',
        'isGroupMsg': True,
        'quotedMsg': None
    }


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return {
        'id': '1234567890@c.us',
        'name': 'Test User',
        'phone': '1234567890',
        'is_admin': False
    }


@pytest.fixture
def admin_user():
    """Create a sample admin user"""
    return {
        'id': 'admin_9876543210@c.us',
        'name': 'Admin User',
        'phone': '9876543210',
        'is_admin': True
    }


@pytest.fixture
def owner_user():
    """Create a sample owner/superadmin user"""
    return {
        'id': 'owner',
        'name': 'Owner User',
        'phone': '1111111111',
        'is_admin': True,
        'is_owner': True
    }


@pytest.fixture
def sample_chat():
    """Create a sample chat/group"""
    return {
        'id': 'test_group@g.us',
        'name': 'Test Group',
        'is_group': True,
        'admins': ['admin_9876543210@c.us'],
        'owner': 'owner'
    }


@pytest.fixture
def mock_openai():
    """Mock OpenAI API for testing"""
    with patch('openai.OpenAI') as mock:
        client = MagicMock()
        mock.return_value = client
        
        # Mock moderation endpoint
        moderation_result = MagicMock()
        moderation_result.results = [MagicMock(
            flagged=False,
            categories=MagicMock(
                hate=False,
                violence=False,
                harassment=False,
                sexual=False
            ),
            category_scores=MagicMock(
                hate=0.01,
                violence=0.01,
                harassment=0.01,
                sexual=0.01
            )
        )]
        client.moderations.create.return_value = moderation_result
        
        yield client


@pytest.fixture
def toxic_message():
    """Create a toxic message for AI moderation testing"""
    return {
        'id': 'toxic_msg_123',
        'body': 'I hate you and want to hurt you',
        'from': '1234567890@c.us',
        'chat_id': 'test_group@g.us',
        'author': '1234567890@c.us',
        'isGroupMsg': True
    }


# Markers for different test categories
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API calls"
    )
    config.addinivalue_line(
        "markers", "whatsapp: marks tests for WhatsApp-specific functionality"
    )
    config.addinivalue_line(
        "markers", "telegram: marks tests for Telegram-specific functionality"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on file location"""
    for item in items:
        # Mark async tests
        if 'async' in item.name or item.get_closest_marker('asyncio'):
            item.add_marker(pytest.mark.asyncio)
        
        # Mark API tests
        if 'api' in item.fspath.basename or 'openai' in item.name.lower():
            item.add_marker(pytest.mark.api)


# Skip tests that require real API connections in CI
def pytest_runtest_setup(item):
    """Skip tests that require external services when not available"""
    if 'api' in item.keywords:
        if not os.environ.get('OPENAI_API_KEY'):
            pytest.skip("OPENAI_API_KEY not set, skipping API test")
    
    if 'integration' in item.keywords:
        if os.environ.get('CI') and not os.environ.get('RUN_INTEGRATION_TESTS'):
            pytest.skip("Integration tests disabled in CI")
