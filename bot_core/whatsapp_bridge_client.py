"""
Python client for WhatsApp Bridge (Node.js)

This module provides a Python interface to communicate with the WhatsApp Bridge server.
"""

import requests
import logging
from typing import Optional, Dict, Any, Callable, List
import threading
import time
from flask import Flask, request as flask_request

logger = logging.getLogger(__name__)


class WhatsAppBridgeClient:
    """
    Client to communicate with WhatsApp Bridge Node.js server
    """
    
    def __init__(self, bridge_url: str = "http://localhost:3000", callback_port: int = 5000):
        self.bridge_url = bridge_url.rstrip('/')
        self.callback_port = callback_port
        self.message_handlers = []
        self.group_join_handlers = []
        self.group_leave_handlers = []
        self.event_handlers = {}
        self.flask_app = None
        self.flask_thread = None
        self._bridge_ready = threading.Event()  # Event to wait for bridge ready signal

    def _request(self, method: str, path: str, json: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Dict[str, Any]:
        url = f"{self.bridge_url}{path}"
        response = requests.request(method, url, json=json, timeout=timeout)
        response.raise_for_status()
        return response.json()
        
    def start_callback_server(self):
        """Start Flask server to receive callbacks from bridge"""
        self.flask_app = Flask(__name__)
        
        @self.flask_app.route('/webhook', methods=['POST'])
        def webhook():
            data = flask_request.json
            event_type = data.get('type', 'message')
            logger.info(f"Webhook received: {event_type}")
            logger.info(f"Registered handlers: {len(self.message_handlers)}")
            
            # Handle 'ready' event from bridge
            if event_type == 'ready':
                logger.info("🎉 Bridge sent ready signal!")
                self._bridge_ready.set()
                return {'status': 'ok'}
            
            if event_type == 'message':
                msg_data = data.get('data', {})
                logger.info(f"Message data: {msg_data.get('body', '')[:50]}")
                for handler in self.message_handlers:
                    try:
                        logger.info(f"Calling handler: {handler}")
                        handler(msg_data)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}", exc_info=True)
            elif event_type == 'group_join':
                for handler in self.group_join_handlers:
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"Error in group_join handler: {e}")
            elif event_type == 'group_leave':
                for handler in self.group_leave_handlers:
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"Error in group_leave handler: {e}")
            else:
                # Generic event handlers
                handlers = self.event_handlers.get(event_type, [])
                for handler in handlers:
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"Error in {event_type} handler: {e}")
            return {'status': 'ok'}
        
        # Run Flask in a separate thread
        self.flask_thread = threading.Thread(
            target=lambda: self.flask_app.run(port=self.callback_port, debug=False, use_reloader=False)
        )
        self.flask_thread.daemon = True
        self.flask_thread.start()
        
        # Give Flask time to start
        time.sleep(2)
        
        # Register callback with bridge
        callback_url = f"http://localhost:{self.callback_port}/webhook"
        try:
            response = requests.post(
                f"{self.bridge_url}/set-callback",
                json={'url': callback_url},
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Registered callback with bridge: {callback_url}")
        except Exception as e:
            logger.error(f"Failed to register callback: {e}")
    
    def is_ready(self) -> bool:
        """Check if bridge is ready (via HTTP or internal flag)"""
        # First check internal flag (set by ready event)
        if self._bridge_ready.is_set():
            return True
        # Fallback to HTTP check
        try:
            data = self._request('GET', '/health', timeout=5)
            ready = data.get('ready', False)
            if ready:
                self._bridge_ready.set()
            return ready
        except Exception as e:
            logger.debug(f"Bridge not ready yet: {e}")
            return False
    
    def wait_for_ready(self, timeout: float = 120.0) -> bool:
        """Wait for bridge to become ready.
        
        Args:
            timeout: Maximum seconds to wait for bridge ready signal
            
        Returns:
            True if bridge is ready, False if timeout reached
        """
        logger.info(f"⏳ Waiting for bridge to become ready (timeout: {timeout}s)...")
        
        # First, try polling the health endpoint while waiting for the event
        start_time = time.time()
        poll_interval = 2.0
        
        while time.time() - start_time < timeout:
            # Check if we got the ready event
            if self._bridge_ready.is_set():
                logger.info("✅ Bridge is ready (via event)!")
                return True
            
            # Try HTTP health check
            try:
                if self.is_ready():
                    logger.info("✅ Bridge is ready (via health check)!")
                    return True
            except Exception:
                pass
            
            # Wait a bit before next check, but also listen for event
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
            if remaining <= 0:
                break
            wait_time = min(poll_interval, remaining)
            if self._bridge_ready.wait(timeout=wait_time):
                logger.info("✅ Bridge is ready (via event)!")
                return True
        
        logger.error(f"❌ Bridge did not become ready within {timeout}s")
        return False
    
    def send_message(self, chat_id: str, message: str) -> Optional[str]:
        """Send a text message"""
        try:
            result = self._request('POST', '/send-message', json={'chatId': chat_id, 'message': message}, timeout=10)
            return result.get('messageId')
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None

    def send_mention(self, chat_id: str, message: str, mention_ids: list) -> Optional[str]:
        """Send a text message with mentions (proper @tagging)"""
        try:
            result = self._request('POST', '/send-mention', json={
                'chatId': chat_id,
                'message': message,
                'mentionIds': mention_ids
            }, timeout=10)
            return result.get('messageId')
        except Exception as e:
            logger.error(f"Failed to send mention message: {e}")
            return None
    
    def delete_message(self, chat_id: str, message_id: str) -> bool:
        """Delete a message for everyone"""
        try:
            self._request('POST', '/delete-message', json={'chatId': chat_id, 'messageId': message_id}, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False
    
    def send_media(self, chat_id: str, media_url: str, caption: Optional[str] = None) -> Optional[str]:
        """Send media (image, video, etc.)"""
        try:
            result = self._request('POST', '/send-media', json={'chatId': chat_id, 'mediaUrl': media_url, 'caption': caption}, timeout=30)
            return result.get('messageId')
        except Exception as e:
            logger.error(f"Failed to send media: {e}")
            return None
    
    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat information"""
        try:
            return self._request('GET', f"/chat/{chat_id}", timeout=10)
        except Exception as e:
            logger.error(f"Failed to get chat: {e}")
            return None

    def get_chat_details(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat details including group/private detection"""
        try:
            result = self._request('GET', f"/chat/{chat_id}/details", timeout=10)
            return result.get('chat')
        except Exception as e:
            logger.error(f"Failed to get chat details: {e}")
            return None
    
    def get_group_members(self, group_id: str) -> Optional[list]:
        """Get group members"""
        try:
            result = self._request('GET', f"/group/{group_id}/members", timeout=10)
            return result.get('participants', [])
        except Exception as e:
            logger.error(f"Failed to get group members: {e}")
            return None

    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact by WhatsApp ID"""
        try:
            result = self._request('GET', f"/contact/{contact_id}", timeout=10)
            return result.get('contact')
        except Exception as e:
            logger.error(f"Failed to get contact: {e}")
            return None

    def get_contact_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get contact by phone number in any format"""
        try:
            normalized = self.normalize_phone(phone_number)
            result = self._request('GET', f"/contact/by-number/{normalized}", timeout=10)
            return result.get('contact')
        except Exception as e:
            logger.error(f"Failed to get contact by phone: {e}")
            return None

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get message by ID"""
        try:
            result = self._request('GET', f"/message/{message_id}", timeout=10)
            return result.get('message')
        except Exception as e:
            logger.error(f"Failed to get message: {e}")
            return None

    def download_media(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Download media from a message"""
        try:
            result = self._request('GET', f"/message/{message_id}/media", timeout=30)
            return result.get('media')
        except Exception as e:
            logger.error(f"Failed to download media: {e}")
            return None

    def send_media_base64(self, chat_id: str, mimetype: str, data: str, filename: Optional[str] = None, caption: Optional[str] = None) -> Optional[str]:
        """Send media using base64 data"""
        try:
            payload = {
                'chatId': chat_id,
                'mimetype': mimetype,
                'data': data,
                'filename': filename,
                'caption': caption
            }
            result = self._request('POST', '/send-media-base64', json=payload, timeout=30)
            return result.get('messageId')
        except Exception as e:
            logger.error(f"Failed to send media base64: {e}")
            return None

    def send_mention(self, chat_id: str, message: str, mention_ids: List[str]) -> Optional[str]:
        """Send a message with user mentions"""
        try:
            payload = {
                'chatId': chat_id,
                'message': message,
                'mentionIds': mention_ids
            }
            result = self._request('POST', '/send-mention', json=payload, timeout=10)
            return result.get('messageId')
        except Exception as e:
            logger.error(f"Failed to send mention message: {e}")
            return None

    def find_contacts_by_name(self, name_query: str) -> List[Dict[str, Any]]:
        """Find contacts by name or pushname (best-effort)"""
        try:
            contacts = self.call('client', 'getContacts') or []
            query = name_query.strip().lower()
            results = []
            for contact in contacts:
                name = str(contact.get('name') or '').lower()
                pushname = str(contact.get('pushname') or '').lower()
                short_name = str(contact.get('shortName') or '').lower()
                if query in name or query in pushname or query in short_name:
                    results.append(contact)
            return results
        except Exception as e:
            logger.error(f"Failed to find contacts by name: {e}")
            return []
    
    def remove_participant(self, group_id: str, participant_id: str) -> bool:
        """Remove participant from group"""
        try:
            self._request('POST', f"/group/{group_id}/remove", json={'participantId': participant_id}, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Failed to remove participant: {e}")
            return False
    
    def promote_participant(self, group_id: str, participant_id: str) -> bool:
        """Promote participant to admin"""
        try:
            self._request('POST', f"/group/{group_id}/promote", json={'participantId': participant_id}, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Failed to promote participant: {e}")
            return False
    
    def demote_participant(self, group_id: str, participant_id: str) -> bool:
        """Demote participant from admin"""
        try:
            self._request('POST', f"/group/{group_id}/demote", json={'participantId': participant_id}, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Failed to demote participant: {e}")
            return False
    
    def get_membership_requests(self, group_id: str) -> Optional[list]:
        """Get pending membership requests for a group.
        
        Returns list of requests, each with:
        - id: User ID who requested to join
        - addedBy: Who created the request
        - requestMethod: How they requested (NonAdminAdd/InviteLink/LinkedGroupJoin)
        - timestamp: When the request was created
        """
        try:
            result = self._request('GET', f"/group/{group_id}/membership-requests", timeout=10)
            return result.get('requests', [])
        except Exception as e:
            logger.error(f"Failed to get membership requests: {e}")
            return None
    
    def approve_membership_requests(self, group_id: str, requester_ids: list = None) -> dict:
        """Approve membership requests.
        
        Args:
            group_id: Group ID
            requester_ids: List of user IDs to approve. If None, approves all pending requests.
            
        Returns:
            Dict with results for each request.
        """
        try:
            data = {}
            if requester_ids:
                data['requesterIds'] = requester_ids
            result = self._request('POST', f"/group/{group_id}/membership-requests/approve", json=data, timeout=15)
            return {'success': True, 'results': result.get('results', [])}
        except Exception as e:
            logger.error(f"Failed to approve membership requests: {e}")
            return {'success': False, 'error': str(e)}
    
    def reject_membership_requests(self, group_id: str, requester_ids: list = None) -> dict:
        """Reject membership requests.
        
        Args:
            group_id: Group ID
            requester_ids: List of user IDs to reject. If None, rejects all pending requests.
            
        Returns:
            Dict with results for each request.
        """
        try:
            data = {}
            if requester_ids:
                data['requesterIds'] = requester_ids
            result = self._request('POST', f"/group/{group_id}/membership-requests/reject", json=data, timeout=15)
            return {'success': True, 'results': result.get('results', [])}
        except Exception as e:
            logger.error(f"Failed to reject membership requests: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_participants(self, group_id: str, participants: list) -> bool:
        """Add participants to group"""
        try:
            url = f"{self.bridge_url}/group/{group_id}/add"
            response = requests.post(url, json={'participants': participants}, timeout=30)
            if response.ok:
                data = response.json()
                # Check if invite was sent vs actual add
                invite_sent = data.get('inviteSent', False)
                invite_link_sent = data.get('inviteLinkSent', False)
                invite_link_failed = data.get('inviteLinkFailed', False)
                message = data.get('message', '')
                result = data.get('result', [])
                return {
                    'success': True,
                    'result': result,
                    'inviteSent': invite_sent,
                    'inviteLinkSent': invite_link_sent,
                    'inviteLinkFailed': invite_link_failed,
                    'message': message
                }
            error_message = None
            try:
                error_data = response.json()
                error_message = error_data.get('error')
            except Exception:
                error_message = response.text
            logger.error(f"Failed to add participants: {error_message}")
            return {'success': False, 'error': error_message or 'Unknown error'}
        except Exception as e:
            logger.error(f"Failed to add participants: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_invite_link(self, group_id: str) -> Optional[str]:
        """Get group invite link"""
        try:
            result = self._request('GET', f"/group/{group_id}/invite", timeout=10)
            return result.get('inviteLink')
        except Exception as e:
            logger.error(f"Failed to get invite link: {e}")
            return None

    def get_capabilities(self) -> Optional[Dict[str, Any]]:
        """Fetch bridge capabilities (full future API surface)"""
        try:
            result = self._request('GET', '/capabilities', timeout=10)
            return result.get('capabilities')
        except Exception as e:
            logger.error(f"Failed to get capabilities: {e}")
            return None

    def call(self, scope: str, method: str, target_id: Optional[str] = None, args: Optional[list] = None) -> Any:
        """Generic call to whatsapp-web.js methods exposed by the bridge"""
        try:
            payload = {
                'scope': scope,
                'method': method,
                'id': target_id,
                'args': args or []
            }
            result = self._request('POST', '/call', json=payload, timeout=30)
            return result.get('result')
        except Exception as e:
            logger.error(f"Failed to call bridge method {scope}.{method}: {e}")
            return None
    
    def on_message(self, handler: Callable):
        """Register message handler"""
        self.message_handlers.append(handler)
    
    def on_group_join(self, handler: Callable):
        """Register group join handler"""
        self.group_join_handlers.append(handler)
    
    def on_group_leave(self, handler: Callable):
        """Register group leave handler"""
        self.group_leave_handlers.append(handler)

    def on_event(self, event_type: str, handler: Callable):
        """Register a generic event handler (e.g., message_reaction, message_edit, group_update)"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    @staticmethod
    def normalize_phone(phone_number: str) -> str:
        """Normalize phone number to digits only"""
        return ''.join(ch for ch in phone_number if ch.isdigit())

    @staticmethod
    def normalize_user_id(user: str) -> str:
        """Normalize to WhatsApp user ID format (xxx@s.whatsapp.net)"""
        if user.endswith('@s.whatsapp.net'):
            return user
        digits = WhatsAppBridgeClient.normalize_phone(user)
        return f"{digits}@s.whatsapp.net"

    @staticmethod
    def normalize_group_id(group: str) -> str:
        """Normalize to WhatsApp group ID format (xxx@g.us)"""
        if group.endswith('@g.us'):
            return group
        digits = WhatsAppBridgeClient.normalize_phone(group)
        return f"{digits}@g.us"

    @staticmethod
    def is_group_id(chat_id: str) -> bool:
        """Check if chat ID is a group"""
        return chat_id.endswith('@g.us')

    @staticmethod
    def is_private_id(chat_id: str) -> bool:
        """Check if chat ID is a private chat"""
        return chat_id.endswith('@s.whatsapp.net')

    @staticmethod
    def format_mention(user_id: str) -> str:
        """Format a WhatsApp mention string from user ID or phone"""
        normalized = WhatsAppBridgeClient.normalize_user_id(user_id)
        phone = normalized.split('@')[0]
        return f"@{phone}"
