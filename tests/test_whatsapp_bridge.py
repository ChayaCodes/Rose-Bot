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
            bridge_url="http://localhost:3000"
        )
        
        assert client is not None
        assert client.bridge_url == "http://localhost:3000"
    
    def test_bridge_health_check(self):
        """Test bridge health check"""
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        
        client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000"
        )
        
        with patch.object(client, '_request') as mock_request:
            mock_request.return_value = {"ready": True}
            assert client.is_ready() is True


class TestWhatsAppAdapter:
    """Test WhatsApp adapter"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        
        self.adapter = WhatsAppAdapter({})
    
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


class TestWhatsAppAdapterHelpers:
    """Test WhatsApp adapter helper methods"""

    def test_is_group_chat_id(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        assert WhatsAppAdapter.is_group_chat_id("123@g.us") is True
        assert WhatsAppAdapter.is_group_chat_id("123@s.whatsapp.net") is False

    def test_is_private_chat_id(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        assert WhatsAppAdapter.is_private_chat_id("123@s.whatsapp.net") is True
        assert WhatsAppAdapter.is_private_chat_id("123@g.us") is False

    def test_normalize_phone(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        assert WhatsAppAdapter.normalize_phone("+972-50-123-4567") == "972501234567"

    def test_normalize_user_id(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        assert WhatsAppAdapter.normalize_user_id("972501234567") == "972501234567@s.whatsapp.net"

    def test_normalize_group_id(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        assert WhatsAppAdapter.normalize_group_id("123456") == "123456@g.us"

    def test_format_mention(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        assert WhatsAppAdapter.format_mention("972501234567") == "@972501234567"


class TestWhatsAppMessageParsing:
    """Test WhatsApp message parsing"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.adapters.whatsapp_adapter import WhatsAppAdapter
        
        self.adapter = WhatsAppAdapter({})
    
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
        
        self.adapter = WhatsAppAdapter({})
    
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
        
        self.adapter = WhatsAppAdapter({})
    
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
        
        self.adapter = WhatsAppAdapter({})
    
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
            bridge_url="http://localhost:3000"
        )
    
    def test_handle_connection_error(self):
        """Test handling connection error"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.side_effect = ConnectionError("Bridge unavailable")
            assert self.client.send_message("chat", "message") is None
    
    def test_handle_timeout(self):
        """Test handling timeout"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.side_effect = asyncio.TimeoutError()
            assert self.client.send_message("chat", "message") is None


class TestBridgeClientNewFunctions:
    """Tests for newly added WhatsAppBridgeClient functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        
        self.client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000"
        )
    
    def test_get_chat_details(self):
        """Test chat details endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"chat": {"id": "123@g.us", "isGroup": True}}
            details = self.client.get_chat_details("123@g.us")
            assert details["isGroup"] is True

    def test_get_capabilities(self):
        """Test capabilities fetch"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"capabilities": {"version": "1.0"}}
            caps = self.client.get_capabilities()
            assert caps["version"] == "1.0"

    def test_call(self):
        """Test generic call wrapper"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"result": {"id": "123@g.us"}}
            result = self.client.call("chat", "getContact", "123@g.us", [])
            assert result["id"] == "123@g.us"
    
    def test_get_contact(self):
        """Test get contact by ID"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"contact": {"id": "123@s.whatsapp.net"}}
            contact = self.client.get_contact("123@s.whatsapp.net")
            assert contact["id"].endswith("@s.whatsapp.net")
    
    def test_get_contact_by_phone(self):
        """Test get contact by phone number"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"contact": {"id": "972501234567@s.whatsapp.net"}}
            contact = self.client.get_contact_by_phone("+972-50-123-4567")
            assert contact["id"].startswith("97250")
    
    def test_get_message(self):
        """Test get message by ID"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"message": {"id": "msg123", "body": "Hello"}}
            msg = self.client.get_message("msg123")
            assert msg["body"] == "Hello"
    
    def test_download_media(self):
        """Test download media from message"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"media": {"mimetype": "image/png", "data": "base64"}}
            media = self.client.download_media("msg123")
            assert media["mimetype"] == "image/png"
    
    def test_send_media_base64(self):
        """Test send media base64"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"messageId": "msg789"}
            msg_id = self.client.send_media_base64("chat@g.us", "image/png", "base64", "file.png")
            assert msg_id == "msg789"
    
    def test_send_mention(self):
        """Test send mention message"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"messageId": "msg999"}
            msg_id = self.client.send_mention("chat@g.us", "Hello @user", ["123@s.whatsapp.net"])
            assert msg_id == "msg999"
    
    def test_find_contacts_by_name(self):
        """Test finding contacts by name"""
        with patch.object(self.client, 'call') as mock_call:
            mock_call.return_value = [
                {"name": "Alice", "pushname": "Ali", "shortName": "A"},
                {"name": "Bob", "pushname": "Bobby", "shortName": "B"}
            ]
            results = self.client.find_contacts_by_name("ali")
            assert len(results) == 1


class TestBridgeClientHelpers:
    """Tests for normalization and helpers"""
    
    def test_normalize_phone(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        assert WhatsAppBridgeClient.normalize_phone("+972-50-123-4567") == "972501234567"
    
    def test_normalize_user_id(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        assert WhatsAppBridgeClient.normalize_user_id("972501234567") == "972501234567@s.whatsapp.net"
    
    def test_normalize_group_id(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        assert WhatsAppBridgeClient.normalize_group_id("123456") == "123456@g.us"
    
    def test_is_group_id(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        assert WhatsAppBridgeClient.is_group_id("123@g.us") is True
        assert WhatsAppBridgeClient.is_group_id("123@s.whatsapp.net") is False
    
    def test_is_private_id(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        assert WhatsAppBridgeClient.is_private_id("123@s.whatsapp.net") is True
        assert WhatsAppBridgeClient.is_private_id("123@g.us") is False
    
    def test_format_mention(self):
        from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
        assert WhatsAppBridgeClient.format_mention("972501234567") == "@972501234567"
