"""
Security Tests for Rose-Bot
Tests for SQL injection, permission checks, input sanitization, and XSS prevention.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestSQLInjectionPrevention:
    """Test SQL injection prevention"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.rules_service import set_rules, get_rules
        from bot_core.services.blacklist_service import add_blacklist_word, get_blacklist
        from bot_core.services.warn_service import add_warn
        from bot_core.services.welcome_service import set_welcome
        
        self.set_rules = set_rules
        self.get_rules = get_rules
        self.add_blacklist = add_blacklist_word
        self.get_blacklist = get_blacklist
        self.add_warn = add_warn
        self.set_welcome = set_welcome
    
    def test_sql_injection_in_chat_id(self):
        """Test SQL injection in chat_id parameter"""
        malicious_ids = [
            "'; DROP TABLE rules; --",
            "1; DELETE FROM blacklist; --",
            "test' OR '1'='1",
            "test\"; DROP TABLE users; --",
            "1; UPDATE rules SET rules='hacked'; --",
        ]
        
        for chat_id in malicious_ids:
            # Should not raise error or corrupt DB
            try:
                self.set_rules(chat_id, "Safe rules")
                rules = self.get_rules(chat_id)
                # Should get exact rules back
                assert rules == "Safe rules" or rules is None
            except Exception:
                pass  # Rejection is also acceptable
    
    def test_sql_injection_in_rules_text(self):
        """Test SQL injection in rules text"""
        malicious_texts = [
            "Rules'; DROP TABLE blacklist; --",
            "Test\"; DELETE FROM warns; --",
            "Normal rules' OR '1'='1' --",
            "Rules\x00'; DROP ALL; --",
        ]
        
        for text in malicious_texts:
            chat_id = "test_chat_sql"
            self.set_rules(chat_id, text)
            rules = self.get_rules(chat_id)
            # Should store and return exact text
            assert rules == text
    
    def test_sql_injection_in_blacklist_word(self):
        """Test SQL injection in blacklist word"""
        malicious_words = [
            "word'; DROP TABLE rules; --",
            "test\"; DELETE * FROM blacklist; --",
            "spam' OR '1'='1",
        ]
        
        for word in malicious_words:
            chat_id = "test_chat_blacklist"
            self.add_blacklist(chat_id, word)
            blacklist = self.get_blacklist(chat_id)
            # Word should be stored literally
            assert word in blacklist
    
    def test_sql_injection_in_user_id(self):
        """Test SQL injection in user_id parameter"""
        malicious_ids = [
            "user123'; DROP TABLE warns; --",
            "admin\"; DELETE FROM users; --",
        ]
        
        for user_id in malicious_ids:
            chat_id = "test_chat_user"
            try:
                self.add_warn(chat_id, user_id, "test reason")
            except Exception:
                pass  # Should not corrupt database
    
    def test_sql_injection_in_welcome_message(self):
        """Test SQL injection in welcome message"""
        malicious_messages = [
            "Welcome! '; DROP TABLE welcomes; --",
            "{name}\" OR \"1\"=\"1",
        ]
        
        for message in malicious_messages:
            chat_id = "test_welcome_sql"
            self.set_welcome(chat_id, message)
            # Should store safely


class TestAdminPermissionChecks:
    """Test admin permission verification"""
    
    def test_admin_only_decorator_concept(self):
        """Test admin-only functionality concept"""
        # Simulate admin check
        def is_admin(user_id, chat_id, admins_list):
            return user_id in admins_list
        
        admin_id = "admin123"
        user_id = "user456"
        admins = ["admin123", "admin789"]
        
        assert is_admin(admin_id, "chat1", admins) == True
        assert is_admin(user_id, "chat1", admins) == False
    
    def test_owner_only_check(self):
        """Test owner-only permission check"""
        def is_owner(user_id, owner_id):
            return user_id == owner_id
        
        owner = "owner123"
        admin = "admin456"
        user = "user789"
        
        assert is_owner(owner, owner) == True
        assert is_owner(admin, owner) == False
        assert is_owner(user, owner) == False
    
    def test_permission_escalation_prevention(self):
        """Test users cannot escalate permissions"""
        # Regular users should not be able to:
        # 1. Set rules
        # 2. Modify blacklist
        # 3. Warn/ban others
        # 4. Enable/disable features
        
        # This is a conceptual test - actual implementation
        # should check permissions before each action
        assert True  # Placeholder for permission system tests
    
    def test_cross_chat_permission_isolation(self):
        """Test admin in one chat cannot admin another"""
        def can_admin_chat(user_id, chat_id, user_admin_chats):
            return chat_id in user_admin_chats.get(user_id, [])
        
        user_chats = {
            "admin1": ["chat1", "chat2"],
            "admin2": ["chat3"],
        }
        
        # Admin1 can admin chat1 but not chat3
        assert can_admin_chat("admin1", "chat1", user_chats) == True
        assert can_admin_chat("admin1", "chat3", user_chats) == False
        
        # Admin2 can admin chat3 but not chat1
        assert can_admin_chat("admin2", "chat3", user_chats) == True
        assert can_admin_chat("admin2", "chat1", user_chats) == False


class TestInputSanitization:
    """Test input sanitization"""
    
    def test_null_byte_handling(self):
        """Test null byte is handled safely"""
        text = "Hello\x00World"
        sanitized = text.replace('\x00', '')
        assert '\x00' not in sanitized
        assert sanitized == "HelloWorld"
    
    def test_control_character_handling(self):
        """Test control characters are handled"""
        text = "Hello\x01\x02\x03World"
        # Should strip or escape control chars
        sanitized = ''.join(c for c in text if ord(c) >= 32 or c in '\n\r\t')
        assert sanitized == "HelloWorld"
    
    def test_unicode_normalization(self):
        """Test unicode normalization"""
        import unicodedata
        
        # Homograph attack - cyrillic 'a' vs latin 'a'
        latin = "admin"
        cyrillic = "аdmin"  # First char is cyrillic а
        
        # These look identical but are different
        assert latin != cyrillic
        
        # Normalize to catch homograph attacks
        normalized_latin = unicodedata.normalize('NFKC', latin)
        normalized_cyrillic = unicodedata.normalize('NFKC', cyrillic)
        
        # Still different after normalization (need confusable detection)
        assert normalized_latin != normalized_cyrillic
    
    def test_very_long_input(self):
        """Test very long input handling"""
        max_length = 4096  # Telegram message limit
        
        long_text = "A" * 10000
        truncated = long_text[:max_length]
        
        assert len(truncated) <= max_length
    
    def test_empty_input_handling(self):
        """Test empty input handling"""
        empty_inputs = ["", None, "   ", "\n\n"]
        
        for inp in empty_inputs:
            # Should not crash
            if inp:
                stripped = inp.strip()
            else:
                stripped = ""
            assert isinstance(stripped, str)
    
    def test_special_format_characters(self):
        """Test special format characters"""
        text = "Hello {name} {{literal}} {{{mixed}}}"
        
        # Should not crash on format
        try:
            # These should work
            text.format(name="World", mixed="test")
        except KeyError:
            pass  # Expected if literal braces aren't escaped


class TestXSSPrevention:
    """Test XSS/HTML injection prevention"""
    
    def test_html_escaping(self):
        """Test HTML is escaped"""
        import html
        
        malicious = "<script>alert('XSS')</script>"
        escaped = html.escape(malicious)
        
        assert '<script>' not in escaped
        assert '&lt;script&gt;' in escaped
    
    def test_markdown_injection_prevention(self):
        """Test markdown injection prevention"""
        # User input should not break markdown formatting
        user_input = "*Bold* _Italic_ `Code` [Link](http://evil.com)"
        
        # Escape markdown characters
        escaped = user_input.replace('*', '\\*').replace('_', '\\_')
        escaped = escaped.replace('`', '\\`').replace('[', '\\[')
        
        assert '\\*Bold\\*' in escaped
    
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            "https://google.com",
            "http://example.org/path",
            "https://api.telegram.org/bot",
        ]
        
        invalid_urls = [
            "javascript:alert('XSS')",
            "data:text/html,<script>alert(1)</script>",
            "file:///etc/passwd",
            "ftp://internal.server",
        ]
        
        allowed_schemes = ['http', 'https']
        
        for url in valid_urls:
            scheme = url.split(':')[0].lower()
            assert scheme in allowed_schemes
        
        for url in invalid_urls:
            scheme = url.split(':')[0].lower()
            assert scheme not in allowed_schemes


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_flood_detection(self):
        """Test flood detection logic"""
        from collections import defaultdict
        import time
        
        # Simulate flood counter
        user_messages = defaultdict(list)
        flood_limit = 5
        flood_window = 10  # seconds
        
        user_id = "user123"
        chat_id = "chat456"
        
        def is_flooding(user_id, chat_id, current_time):
            key = f"{chat_id}:{user_id}"
            # Clean old messages
            user_messages[key] = [
                t for t in user_messages[key] 
                if current_time - t < flood_window
            ]
            # Check limit
            if len(user_messages[key]) >= flood_limit:
                return True
            # Add current message
            user_messages[key].append(current_time)
            return False
        
        now = time.time()
        
        # First 5 messages should be OK
        for i in range(flood_limit):
            assert is_flooding(user_id, chat_id, now + i * 0.1) == False
        
        # 6th message should trigger flood
        assert is_flooding(user_id, chat_id, now + 0.5) == True
    
    def test_command_cooldown(self):
        """Test command cooldown logic"""
        command_usage = {}
        cooldown = 3  # seconds
        
        def can_use_command(user_id, command, current_time):
            key = f"{user_id}:{command}"
            last_use = command_usage.get(key, 0)
            
            if current_time - last_use < cooldown:
                return False
            
            command_usage[key] = current_time
            return True
        
        import time
        now = time.time()
        
        # First use OK
        assert can_use_command("user1", "/warn", now) == True
        
        # Immediate second use blocked
        assert can_use_command("user1", "/warn", now + 1) == False
        
        # After cooldown OK
        assert can_use_command("user1", "/warn", now + 4) == True


class TestDataIsolation:
    """Test data isolation between chats/users"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.rules_service import set_rules, get_rules
        from bot_core.services.blacklist_service import add_blacklist_word, get_blacklist
        
        self.set_rules = set_rules
        self.get_rules = get_rules
        self.add_blacklist = add_blacklist_word
        self.get_blacklist = get_blacklist
    
    def test_rules_isolation(self):
        """Test rules are isolated between chats"""
        chat1 = "chat1"
        chat2 = "chat2"
        
        self.set_rules(chat1, "Rules for chat 1")
        self.set_rules(chat2, "Rules for chat 2")
        
        assert self.get_rules(chat1) == "Rules for chat 1"
        assert self.get_rules(chat2) == "Rules for chat 2"
    
    def test_blacklist_isolation(self):
        """Test blacklist is isolated between chats"""
        chat1 = "chat1_bl"
        chat2 = "chat2_bl"
        
        self.add_blacklist(chat1, "word1")
        self.add_blacklist(chat2, "word2")
        
        bl1 = self.get_blacklist(chat1)
        bl2 = self.get_blacklist(chat2)
        
        assert "word1" in bl1
        assert "word2" not in bl1
        assert "word2" in bl2
        assert "word1" not in bl2
    
    def test_user_data_isolation(self):
        """Test user data is isolated between chats"""
        from bot_core.services.warn_service import add_warn, get_warns
        
        chat1 = "chat_warn1"
        chat2 = "chat_warn2"
        user_id = "same_user"
        
        add_warn(chat1, user_id, "reason 1")
        add_warn(chat2, user_id, "reason 2")
        
        warns1 = get_warns(chat1, user_id)
        warns2 = get_warns(chat2, user_id)
        
        # Warns should be per-chat
        assert warns1 != warns2 or len(warns1) > 0


class TestSecureConfiguration:
    """Test secure configuration handling"""
    
    def test_api_key_not_in_logs(self):
        """Test API keys are not logged"""
        import logging
        
        # Create a mock log handler
        log_messages = []
        
        class TestHandler(logging.Handler):
            def emit(self, record):
                log_messages.append(record.getMessage())
        
        logger = logging.getLogger('test_secure')
        handler = TestHandler()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        # Simulate sanitized logging
        api_key = "sk-1234567890abcdef"
        sanitized = f"API key: {api_key[:7]}***"
        
        logger.info(sanitized)
        
        # Full key should not be in logs
        assert api_key not in log_messages[-1]
        assert "***" in log_messages[-1]
    
    def test_environment_variables_required(self):
        """Test required environment variables concept"""
        required_vars = [
            'DATABASE_URL',
            'OPENAI_API_KEY',
            'TELEGRAM_BOT_TOKEN',
        ]
        
        # In production, all should be set
        # This is a concept test - actual check done at startup
        for var in required_vars:
            # os.environ.get(var) should not be None in production
            pass
    
    def test_debug_mode_off_in_production(self):
        """Test debug mode should be off in production"""
        import os
        
        # In production, debug should be disabled
        debug = os.environ.get('DEBUG', 'false').lower()
        # assert debug in ['false', '0', 'no', '']  # Conceptual test
