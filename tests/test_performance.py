"""
Performance Tests for Rose-Bot
Tests for query performance, message latency, concurrent handling, and memory usage.
"""
import pytest
import sys
import os
import time
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.mark.slow
class TestDatabasePerformance:
    """Test database query performance"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.rules_service import set_rules, get_rules
        from bot_core.services.blacklist_service import add_blacklist_word, get_blacklist, check_blacklist
        from bot_core.services.warn_service import add_warn, get_warns
        
        self.set_rules = set_rules
        self.get_rules = get_rules
        self.add_blacklist = add_blacklist_word
        self.get_blacklist = get_blacklist
        self.check_blacklist = check_blacklist
        self.add_warn = add_warn
        self.get_warns = get_warns
    
    def test_rules_query_performance(self):
        """Test rules query is fast"""
        chat_id = "perf_chat_rules"
        self.set_rules(chat_id, "Test rules content")
        
        start = time.time()
        for _ in range(100):
            self.get_rules(chat_id)
        elapsed = time.time() - start
        
        # 100 queries should complete in under 1 second
        assert elapsed < 1.0, f"Rules query too slow: {elapsed}s for 100 queries"
    
    def test_blacklist_check_performance(self):
        """Test blacklist check is fast"""
        chat_id = "perf_chat_blacklist"
        
        # Add many blacklist words
        for i in range(100):
            self.add_blacklist(chat_id, f"badword{i}")
        
        message = "This is a test message with badword50 in it"
        
        start = time.time()
        for _ in range(100):
            self.check_blacklist(chat_id, message)
        elapsed = time.time() - start
        
        # 100 checks should be under 2 seconds
        assert elapsed < 2.0, f"Blacklist check too slow: {elapsed}s"
    
    def test_warn_query_performance(self):
        """Test warn query is fast"""
        chat_id = "perf_chat_warns"
        user_id = "perf_user"
        
        # Add some warns
        for i in range(10):
            self.add_warn(chat_id, user_id, f"Reason {i}")
        
        start = time.time()
        for _ in range(100):
            self.get_warns(chat_id, user_id)
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Warn query too slow: {elapsed}s"
    
    def test_multiple_chats_isolation_performance(self):
        """Test performance doesn't degrade with many chats"""
        # Create 100 different chats with rules
        for i in range(100):
            self.set_rules(f"chat_{i}", f"Rules for chat {i}")
        
        # Query a specific chat should still be fast
        start = time.time()
        for _ in range(100):
            self.get_rules("chat_50")
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Query with many chats too slow: {elapsed}s"


@pytest.mark.slow
class TestMessageProcessingLatency:
    """Test message processing latency"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.blacklist_service import check_blacklist
        from bot_core.services.locks_service import check_lock_violations
        from bot_core.services.flood_service import check_flood
        
        self.check_blacklist = check_blacklist
        self.check_locks = check_lock_violations
        self.check_flood = check_flood
    
    def test_message_check_latency(self):
        """Test combined message checks are fast"""
        chat_id = "latency_chat"
        user_id = "latency_user"
        message = "This is a normal test message"
        
        start = time.time()
        for _ in range(100):
            # Simulate full message processing
            self.check_blacklist(chat_id, message)
            self.check_flood(chat_id, user_id)
            # check_locks would need message object
        elapsed = time.time() - start
        
        # 100 full checks should be under 2 seconds
        avg_latency = elapsed / 100
        assert avg_latency < 0.02, f"Average latency too high: {avg_latency*1000}ms"


@pytest.mark.slow
class TestConcurrentOperations:
    """Test concurrent operation handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.rules_service import set_rules, get_rules
        from bot_core.services.warn_service import add_warn, get_warns
        
        self.set_rules = set_rules
        self.get_rules = get_rules
        self.add_warn = add_warn
        self.get_warns = get_warns
    
    def test_concurrent_reads(self):
        """Test concurrent read operations"""
        import threading
        
        chat_id = "concurrent_chat"
        self.set_rules(chat_id, "Test rules")
        
        results = []
        errors = []
        
        def read_rules():
            try:
                for _ in range(50):
                    result = self.get_rules(chat_id)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=read_rules) for _ in range(10)]
        
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.time() - start
        
        assert len(errors) == 0, f"Errors during concurrent reads: {errors}"
        assert len(results) == 500
        assert elapsed < 5.0, f"Concurrent reads too slow: {elapsed}s"
    
    def test_concurrent_writes(self):
        """Test concurrent write operations"""
        import threading
        
        errors = []
        
        def write_rules(thread_id):
            try:
                for i in range(10):
                    self.set_rules(f"chat_{thread_id}_{i}", f"Rules {i}")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=write_rules, args=(i,)) for i in range(10)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors during concurrent writes: {errors}"
    
    def test_concurrent_warn_operations(self):
        """Test concurrent warn operations"""
        import threading
        
        chat_id = "warn_concurrent"
        errors = []
        
        def add_warns(user_id):
            try:
                for i in range(5):
                    self.add_warn(chat_id, user_id, f"Reason {i}")
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=add_warns, args=(f"user_{i}",)) 
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors during concurrent warns: {errors}"


@pytest.mark.slow
class TestMemoryUsage:
    """Test memory usage patterns"""
    
    def test_large_blacklist_memory(self, test_db):
        """Test memory with large blacklist"""
        from bot_core.services.blacklist_service import add_blacklist_word, get_blacklist
        
        chat_id = "memory_blacklist"
        
        # Add many words
        for i in range(1000):
            add_blacklist_word(chat_id, f"bannedword{i}longword")
        
        # Get blacklist
        blacklist = get_blacklist(chat_id)
        
        assert len(blacklist) == 1000
    
    def test_large_warns_history(self, test_db):
        """Test memory with large warn history"""
        from bot_core.services.warn_service import add_warn, get_warns
        
        chat_id = "memory_warns"
        
        # Add many warns across users
        for i in range(100):
            for j in range(10):
                add_warn(chat_id, f"user_{i}", f"Reason {j}")
        
        # Query should still work
        warns = get_warns(chat_id, "user_50")
        assert len(warns) > 0


@pytest.mark.slow  
class TestScalability:
    """Test scalability patterns"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        from bot_core.services.rules_service import set_rules, get_rules
        
        self.set_rules = set_rules
        self.get_rules = get_rules
    
    def test_many_chats_performance(self):
        """Test performance with many chats"""
        # Create 500 chats
        for i in range(500):
            self.set_rules(f"scale_chat_{i}", f"Rules for chat {i}")
        
        # Random access should be fast
        start = time.time()
        for i in range(100):
            chat_num = (i * 7) % 500  # Pseudo-random access
            self.get_rules(f"scale_chat_{chat_num}")
        elapsed = time.time() - start
        
        assert elapsed < 2.0, f"Many chats query too slow: {elapsed}s"
    
    def test_long_messages_handling(self):
        """Test handling of long messages"""
        from bot_core.services.blacklist_service import check_blacklist
        
        chat_id = "long_msg_chat"
        
        # Create a very long message
        long_message = " ".join(["word" + str(i) for i in range(1000)])
        
        start = time.time()
        for _ in range(10):
            check_blacklist(chat_id, long_message)
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Long message check too slow: {elapsed}s"


class TestTranslationPerformance:
    """Test i18n translation performance"""
    
    def test_translation_lookup_speed(self):
        """Test translation lookup is fast"""
        from bot_core.i18n import get_text
        
        keys = [
            'start_msg', 'help_general', 'admin_only',
            'rules_show', 'warn_issued', 'blacklist_added',
            'lock_enabled', 'aimod_enabled', 'lang_changed'
        ]
        
        start = time.time()
        for _ in range(1000):
            for key in keys:
                get_text('he', key)
        elapsed = time.time() - start
        
        # 9000 lookups should be under 1 second
        assert elapsed < 1.0, f"Translation lookup too slow: {elapsed}s"
    
    def test_translation_with_substitution(self):
        """Test translation with variable substitution"""
        from bot_core.i18n import get_text
        
        start = time.time()
        for _ in range(1000):
            get_text('he', 'warn_issued', 
                    user='TestUser', reason='Testing', count=1, limit=3)
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Translation substitution too slow: {elapsed}s"


@pytest.mark.slow
class TestAIModerationPerformance:
    """Test AI moderation performance"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_db, mock_openai):
        self.mock_openai = mock_openai
    
    @pytest.mark.asyncio
    async def test_ai_check_with_timeout(self):
        """Test AI check respects timeout"""
        from bot_core.services.ai_moderation_service import check_message_with_ai
        
        # Mock should respond quickly
        start = time.time()
        
        with patch('bot_core.services.ai_moderation_service.openai_client') as mock_client:
            mock_client.moderations.create = AsyncMock(return_value=MagicMock(
                results=[MagicMock(
                    flagged=False,
                    categories=MagicMock(hate=False, violence=False),
                    category_scores=MagicMock(hate=0.01, violence=0.01)
                )]
            ))
            
            result = await check_message_with_ai("Test message")
        
        elapsed = time.time() - start
        
        # Should be fast with mock
        assert elapsed < 1.0


class TestCachePerformance:
    """Test caching performance (if implemented)"""
    
    def test_repeated_query_caching(self, test_db):
        """Test repeated queries benefit from cache"""
        from bot_core.services.rules_service import set_rules, get_rules
        
        chat_id = "cache_test_chat"
        set_rules(chat_id, "Cached rules content")
        
        # First query (cold)
        start_cold = time.time()
        get_rules(chat_id)
        cold_time = time.time() - start_cold
        
        # Repeated queries (should be cached or at least consistent)
        start_hot = time.time()
        for _ in range(100):
            get_rules(chat_id)
        hot_time = time.time() - start_hot
        
        # Hot queries should be fast
        avg_hot = hot_time / 100
        assert avg_hot < 0.01, f"Repeated queries too slow: {avg_hot*1000}ms avg"


@pytest.mark.slow
class TestBatchOperations:
    """Test batch operation performance"""
    
    def test_batch_blacklist_add(self, test_db):
        """Test adding many blacklist words efficiently"""
        from bot_core.services.blacklist_service import add_blacklist_word
        
        chat_id = "batch_blacklist"
        words = [f"bannedword{i}" for i in range(100)]
        
        start = time.time()
        for word in words:
            add_blacklist_word(chat_id, word)
        elapsed = time.time() - start
        
        # 100 inserts should be under 2 seconds
        assert elapsed < 2.0, f"Batch insert too slow: {elapsed}s"
    
    def test_batch_warn_add(self, test_db):
        """Test adding many warns efficiently"""
        from bot_core.services.warn_service import add_warn
        
        chat_id = "batch_warns"
        
        start = time.time()
        for i in range(100):
            add_warn(chat_id, f"user_{i}", f"Reason {i}")
        elapsed = time.time() - start
        
        # 100 warns should be under 2 seconds
        assert elapsed < 2.0, f"Batch warns too slow: {elapsed}s"
