"""
Python client for WhatsApp Bridge (Node.js)

This module provides a Python interface to communicate with the WhatsApp Bridge server.
"""

import requests
import logging
from typing import Optional, Dict, Any, Callable
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
        self.flask_app = None
        self.flask_thread = None
        
    def start_callback_server(self):
        """Start Flask server to receive callbacks from bridge"""
        self.flask_app = Flask(__name__)
        
        @self.flask_app.route('/webhook', methods=['POST'])
        def webhook():
            data = flask_request.json
            if data.get('type') == 'message':
                msg_data = data.get('data', {})
                for handler in self.message_handlers:
                    try:
                        handler(msg_data)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
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
        """Check if bridge is ready"""
        try:
            response = requests.get(f"{self.bridge_url}/health", timeout=5)
            data = response.json()
            return data.get('ready', False)
        except Exception as e:
            logger.error(f"Failed to check bridge health: {e}")
            return False
    
    def send_message(self, chat_id: str, message: str) -> Optional[str]:
        """Send a text message"""
        try:
            response = requests.post(
                f"{self.bridge_url}/send-message",
                json={'chatId': chat_id, 'message': message},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('messageId')
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
    
    def send_media(self, chat_id: str, media_url: str, caption: Optional[str] = None) -> Optional[str]:
        """Send media (image, video, etc.)"""
        try:
            response = requests.post(
                f"{self.bridge_url}/send-media",
                json={'chatId': chat_id, 'mediaUrl': media_url, 'caption': caption},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get('messageId')
        except Exception as e:
            logger.error(f"Failed to send media: {e}")
            return None
    
    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat information"""
        try:
            response = requests.get(f"{self.bridge_url}/chat/{chat_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get chat: {e}")
            return None
    
    def get_group_members(self, group_id: str) -> Optional[list]:
        """Get group members"""
        try:
            response = requests.get(f"{self.bridge_url}/group/{group_id}/members", timeout=10)
            response.raise_for_status()
            result = response.json()
            return result.get('participants', [])
        except Exception as e:
            logger.error(f"Failed to get group members: {e}")
            return None
    
    def remove_participant(self, group_id: str, participant_id: str) -> bool:
        """Remove participant from group"""
        try:
            response = requests.post(
                f"{self.bridge_url}/group/{group_id}/remove",
                json={'participantId': participant_id},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to remove participant: {e}")
            return False
    
    def promote_participant(self, group_id: str, participant_id: str) -> bool:
        """Promote participant to admin"""
        try:
            response = requests.post(
                f"{self.bridge_url}/group/{group_id}/promote",
                json={'participantId': participant_id},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to promote participant: {e}")
            return False
    
    def demote_participant(self, group_id: str, participant_id: str) -> bool:
        """Demote participant from admin"""
        try:
            response = requests.post(
                f"{self.bridge_url}/group/{group_id}/demote",
                json={'participantId': participant_id},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to demote participant: {e}")
            return False
    
    def on_message(self, handler: Callable):
        """Register message handler"""
        self.message_handlers.append(handler)
