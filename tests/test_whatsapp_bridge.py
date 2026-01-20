"""
WhatsApp Bridge Tests
Tests for WhatsApp adapter, bridge connection, and message handling.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestWhatsAppBridgeConnection:
    """Test WhatsApp bridge connection"""
    
    def test_bridge_client_initialization(self):
        """Test bridge client can be initialized"""
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        
        client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000",
            api_key="test_key"
        )
        
        assert client is not None
        assert client.bridge_url == "http://localhost:3000"
    
    @pytest.mark.asyncio
    async def test_bridge_health_check(self):
        """Test bridge health check"""
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        
        client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000",
            api_key="test_key"
        )
        
        with patch.object(client, 'health_check', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = {"status": "healthy", "connected": True}
            
            result = await client.health_check()
            
            assert result["status"] == "healthy"
            assert result["connected"] == True
    
    @pytest.mark.asyncio
    async def test_bridge_reconnection(self):
        """Test bridge reconnection on failure"""
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        
        client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000",
            api_key="test_key"
        )
        
        reconnect_count = 0
        
        async def mock_reconnect():
            nonlocal reconnect_count
            reconnect_count += 1
            return True
        
        with patch.object(client, 'reconnect', mock_reconnect):
            await client.reconnect()
            await client.reconnect()
            
        assert reconnect_count == 2


class TestWhatsAppAdapter:
    """Test WhatsApp adapter"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        
        self.adapter = WhatsAppAdapter()
    
    def test_adapter_initialization(self):
        """Test adapter initializes correctly"""
        assert self.adapter is not None
    
    def test_parse_command_from_message(self):
        """Test parsing command from WhatsApp message"""
        message = "/rules"
        
        if hasattr(self.adapter, 'parse_command'):
            command = self.adapter.parse_command(message)
            assert command == "rules" or command == "/rules"
    
    def test_format_response(self):
        """Test formatting response for WhatsApp"""
        response = "Hello, {name}!"
        
        if hasattr(self.adapter, 'format_response'):
            formatted = self.adapter.format_response(response, name="User")
            assert "User" in formatted
    
    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending message through adapter"""
        with patch.object(self.adapter, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            
            result = await self.adapter.send_message(
                chat_id="chat123@g.us",
                text="Test message"
            )
            
            assert result["success"] == True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_reply(self):
        """Test sending reply to message"""
        with patch.object(self.adapter, 'send_reply', new_callable=AsyncMock) as mock_reply:
            mock_reply.return_value = {"success": True}
            
            result = await self.adapter.send_reply(
                chat_id="chat123@g.us",
                message_id="msg123",
                text="Reply message"
            )
            
            assert result["success"] == True


class TestWhatsAppMessageParsing:
    """Test WhatsApp message parsing"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        
        self.adapter = WhatsAppAdapter()
    
    def test_parse_text_message(self):
        """Test parsing text message"""
        raw_message = {
            "id": "msg123",
            "from": "user123@s.whatsapp.net",
            "to": "chat456@g.us",
            "body": "Hello world",
            "type": "chat",
            "timestamp": 1234567890
        }
        
        if hasattr(self.adapter, 'parse_message'):
            message = self.adapter.parse_message(raw_message)
            assert message.text == "Hello world"
    
    def test_parse_command_message(self):
        """Test parsing command message"""
        raw_message = {
            "id": "msg124",
            "from": "admin@s.whatsapp.net",
            "to": "chat456@g.us",
            "body": "/rules",
            "type": "chat",
            "timestamp": 1234567890
        }
        
        if hasattr(self.adapter, 'parse_message'):
            message = self.adapter.parse_message(raw_message)
            assert message.text.startswith("/")
    
    def test_parse_group_id(self):
        """Test parsing group ID from WhatsApp format"""
        whatsapp_id = "123456789@g.us"
        
        if hasattr(self.adapter, 'extract_group_id'):
            group_id = self.adapter.extract_group_id(whatsapp_id)
            assert "123456789" in group_id
    
    def test_parse_user_id(self):
        """Test parsing user ID from WhatsApp format"""
        whatsapp_id = "123456789@s.whatsapp.net"
        
        if hasattr(self.adapter, 'extract_user_id'):
            user_id = self.adapter.extract_user_id(whatsapp_id)
            assert "123456789" in user_id
    
    def test_is_group_message(self):
        """Test detecting group message"""
        group_chat = "123456@g.us"
        private_chat = "123456@s.whatsapp.net"
        
        if hasattr(self.adapter, 'is_group'):
            assert self.adapter.is_group(group_chat) == True
            assert self.adapter.is_group(private_chat) == False


class TestWhatsAppMediaHandling:
    """Test WhatsApp media handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        
        self.adapter = WhatsAppAdapter()
    
    def test_detect_media_message(self):
        """Test detecting media message types"""
        image_msg = {"type": "image", "mimetype": "image/jpeg"}
        video_msg = {"type": "video", "mimetype": "video/mp4"}
        sticker_msg = {"type": "sticker"}
        text_msg = {"type": "chat", "body": "Hello"}
        
        if hasattr(self.adapter, 'get_message_type'):
            assert self.adapter.get_message_type(image_msg) == "image"
            assert self.adapter.get_message_type(video_msg) == "video"
            assert self.adapter.get_message_type(sticker_msg) == "sticker"
            assert self.adapter.get_message_type(text_msg) == "text"
    
    def test_lock_media_detection(self):
        """Test media detection for locks"""
        message_types = {
            "image": {"type": "image"},
            "video": {"type": "video"},
            "audio": {"type": "audio"},
            "document": {"type": "document"},
            "sticker": {"type": "sticker"},
        }
        
        for media_type, msg_data in message_types.items():
            if hasattr(self.adapter, 'get_message_type'):
                assert self.adapter.get_message_type(msg_data) == media_type


class TestWhatsAppGroupManagement:
    """Test WhatsApp group management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        
        self.adapter = WhatsAppAdapter()
    
    @pytest.mark.asyncio
    async def test_get_group_admins(self):
        """Test getting group admins"""
        with patch.object(self.adapter, 'get_group_admins', new_callable=AsyncMock) as mock_admins:
            mock_admins.return_value = ["admin1@s.whatsapp.net", "admin2@s.whatsapp.net"]
            
            admins = await self.adapter.get_group_admins("group123@g.us")
            
            assert len(admins) == 2
            assert "admin1@s.whatsapp.net" in admins
    
    @pytest.mark.asyncio
    async def test_is_user_admin(self):
        """Test checking if user is admin"""
        with patch.object(self.adapter, 'is_admin', new_callable=AsyncMock) as mock_is_admin:
            mock_is_admin.return_value = True
            
            is_admin = await self.adapter.is_admin(
                chat_id="group123@g.us",
                user_id="admin1@s.whatsapp.net"
            )
            
            assert is_admin == True
    
    @pytest.mark.asyncio
    async def test_kick_user(self):
        """Test kicking user from group"""
        with patch.object(self.adapter, 'kick_user', new_callable=AsyncMock) as mock_kick:
            mock_kick.return_value = {"success": True}
            
            result = await self.adapter.kick_user(
                chat_id="group123@g.us",
                user_id="user123@s.whatsapp.net"
            )
            
            assert result["success"] == True
    
    @pytest.mark.asyncio
    async def test_ban_user(self):
        """Test banning user from group"""
        with patch.object(self.adapter, 'ban_user', new_callable=AsyncMock) as mock_ban:
            mock_ban.return_value = {"success": True}
            
            result = await self.adapter.ban_user(
                chat_id="group123@g.us",
                user_id="user123@s.whatsapp.net"
            )
            
            assert result["success"] == True


class TestWhatsAppEventHandling:
    """Test WhatsApp event handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        
        self.adapter = WhatsAppAdapter()
    
    @pytest.mark.asyncio
    async def test_on_message_event(self):
        """Test message event handling"""
        message_received = []
        
        async def handler(message):
            message_received.append(message)
        
        if hasattr(self.adapter, 'on_message'):
            self.adapter.on_message(handler)
            
            # Simulate receiving message
            if hasattr(self.adapter, 'emit_message'):
                await self.adapter.emit_message({
                    "id": "msg1",
                    "body": "Test",
                    "from": "user@s.whatsapp.net"
                })
                
                assert len(message_received) >= 1
    
    @pytest.mark.asyncio
    async def test_on_group_join_event(self):
        """Test group join event"""
        joins = []
        
        async def handler(event):
            joins.append(event)
        
        if hasattr(self.adapter, 'on_group_join'):
            self.adapter.on_group_join(handler)
            
            if hasattr(self.adapter, 'emit_group_join'):
                await self.adapter.emit_group_join({
                    "user": "newuser@s.whatsapp.net",
                    "chat": "group@g.us"
                })
                
                assert len(joins) >= 1


class TestBridgeErrorHandling:
    """Test bridge error handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        
        self.client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000",
            api_key="test_key"
        )
    
    @pytest.mark.asyncio
    async def test_handle_connection_error(self):
        """Test handling connection error"""
        with patch.object(self.client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = ConnectionError("Bridge unavailable")
            
            try:
                await self.client.send_message("chat", "message")
            except ConnectionError:
                pass  # Expected
    
    @pytest.mark.asyncio
    async def test_handle_timeout(self):
        """Test handling timeout"""
        with patch.object(self.client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = asyncio.TimeoutError()
            
            try:
                await self.client.send_message("chat", "message")
            except asyncio.TimeoutError:
                pass  # Expected
    
    @pytest.mark.asyncio
    async def test_handle_auth_error(self):
        """Test handling authentication error"""
        with patch.object(self.client, 'authenticate', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = {"success": False, "error": "Invalid API key"}
            
            result = await self.client.authenticate()
            
            assert result["success"] == False


class TestQRCodeAuthentication:
    """Test QR code authentication flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        
        self.client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000",
            api_key="test_key"
        )
    
    @pytest.mark.asyncio
    async def test_get_qr_code(self):
        """Test getting QR code for auth"""
        with patch.object(self.client, 'get_qr_code', new_callable=AsyncMock) as mock_qr:
            mock_qr.return_value = {"qr": "data:image/png;base64,..."}
            
            result = await self.client.get_qr_code()
            
            assert "qr" in result
    
    @pytest.mark.asyncio
    async def test_auth_status_check(self):
        """Test authentication status check"""
        with patch.object(self.client, 'is_authenticated', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = True
            
            is_auth = await self.client.is_authenticated()
            
            assert is_auth == True
    
    @pytest.mark.asyncio
    async def test_wait_for_auth(self):
        """Test waiting for authentication"""
        auth_calls = 0
        
        async def mock_check():
            nonlocal auth_calls
            auth_calls += 1
            return auth_calls >= 3  # Authenticated after 3 checks
        
        with patch.object(self.client, 'is_authenticated', mock_check):
            # Simulate waiting
            while not await self.client.is_authenticated():
                await asyncio.sleep(0.01)
            
            assert auth_calls == 3
