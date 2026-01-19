"""
Full-Featured WhatsApp Bot with Group Management
Includes: Warns, Bans, Rules, Welcome, Blacklist, Locks, Anti-flood
"""

import logging
import sys
import os
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bot_core.whatsapp_bridge_client import WhatsAppBridgeClient
from bot_core.content_filter import get_moderator, ModerationResult
from bot_core.i18n import get_chat_text as get_text, TRANSLATIONS, LANG_NAMES, COMMAND_HELP

# Import services
from bot_core.services.warn_service import (
    warn_user, get_user_warns, reset_user_warns, set_warn_limit, get_warn_limit, get_warns, get_warn_settings
)
from bot_core.services.rules_service import get_rules, set_rules, clear_rules
from bot_core.services.welcome_service import (
    get_welcome_message as get_welcome,
    set_welcome_message as set_welcome,
    format_welcome_message
)
from bot_core.services.blacklist_service import (
    add_blacklist_word as add_blacklist,
    remove_blacklist_word as remove_blacklist,
    get_blacklist_words as get_blacklist,
    check_blacklist
)
from bot_core.services.locks_service import set_lock, get_locks, is_locked, check_message_locks
from bot_core.services.language_service import get_chat_language as get_chat_lang, set_chat_language as set_chat_lang
from bot_core.services.ban_service import add_ban, remove_ban, is_banned, get_banned_users
from bot_core.services.chat_config_service import should_delete_commands, set_delete_commands
from bot_core.services.ai_moderation_service import (
    get_ai_settings, set_ai_enabled, set_ai_backend, set_ai_threshold, set_ai_action,
    check_content_toxicity, SUPPORTED_BACKENDS
)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration
try:
    from wa_config import Development as Config
except ImportError:
    logger.error("Copy sample_wa_config.py to wa_config.py and configure it first!")
    sys.exit(1)


# ============ HELPER FUNCTIONS ============

def is_owner(user_id: str) -> bool:
    """Check if user is bot owner"""
    return user_id == Config.OWNER_ID


def is_admin(chat_id: str, user_id: str, client: WhatsAppBridgeClient) -> bool:
    """Check if user is group admin"""
    # Bot owner is always admin
    if is_owner(user_id):
        return True
    
    # For now, in groups, assume all users can use admin commands
    # WhatsApp will handle the actual permissions (only real admins can kick/ban)
    # In private chats, only owner can use admin commands
    if chat_id.endswith('@g.us'):  # Group chat
        return True
    
    return False


def extract_user_from_reply(message: dict) -> Optional[str]:
    """Extract user ID from replied message"""
    # This would need to be implemented based on how whatsapp-web.js sends reply info
    # For now, return None
    return None


def mention_user(user_id: str, name: str = "User") -> str:
    """Create a mention for a user"""
    return f"@{name}"


# ============ WARN SYSTEM ============
# All warn helpers are provided by bot_core.services.warn_service

# ============ LANGUAGE SYSTEM ============
# All language helpers are provided by bot_core.services.language_service

# ============ CHAT CONFIG SYSTEM ============
# All chat config helpers are provided by bot_core.services.chat_config_service

# Note: All other database functions moved to bot_core/services/
# - warn_service: warn_user, get_warns, reset_user_warns, set_warn_limit, get_warn_limit, get_warn_settings
# - rules_service: set_rules, get_rules
# - welcome_service: set_welcome, get_welcome
# - blacklist_service: add_blacklist, remove_blacklist, get_blacklist, check_blacklist
# - locks_service: set_lock, get_locks, check_locks
# - ban_service: add_ban, remove_ban, is_banned, get_banned_users
# - language_service: get_chat_lang, set_chat_lang
# - chat_config_service: should_delete_commands, set_delete_commands
def check_locks(chat_id: str, message: dict) -> Optional[str]:
    """Check if message violates locks"""
    locks = get_locks(chat_id)
    text = message.get('body', '')
    
    # Check links
    if locks['links']:
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        if re.search(url_pattern, text):
            return 'Links are not allowed in this chat'
    
    # Check media and stickers would require message type info from bridge
    # TODO: Implement when bridge provides message type
    
    return None


# ============ AI MODERATION SYSTEM ============

def check_ai_moderation(chat_id: str, text: str, bot_moderator) -> Optional[Dict]:
    """Check message with AI moderation using chat's own settings"""
    from bot_core.services.ai_moderation_service import get_ai_settings, check_content_toxicity
    
    settings = get_ai_settings(chat_id)
    
    if not settings['enabled']:
        return None
    
    # Get settings
    backend = settings['backend']
    api_key = settings['api_key']
    threshold = settings['threshold'] / 100.0  # Convert 0-100 to 0.0-1.0
    action = settings['action']
    
    # Check content toxicity
    result = check_content_toxicity(text, backend=backend, api_key=api_key, threshold=threshold)
    
    # Return result with action if toxic
    if result.get('is_toxic'):
        result['action'] = action  # Add configured action
        return result
    
    return None


# ============ BOT CLASS ============

class WhatsAppBot:
    def __init__(self):
        self.client = WhatsAppBridgeClient(
            bridge_url="http://localhost:3000",
            callback_port=5000
        )
        self.flood_tracker: Dict[str, List[float]] = {}
        self.moderator = None  # Lazy load
        
    def handle_message(self, message: dict):
        """Main message handler"""
        try:
            text = message.get('body', '').strip()
            from_id = message.get('from')
            chat_id = message.get('chatId', from_id)
            is_group = message.get('isGroup', False)
            
            logger.info(f"Message from {from_id} in {chat_id}: {text[:50]}")
            
            # Check blacklist first (if group)
            if is_group:
                # AI Moderation Check
                ai_result = check_ai_moderation(chat_id, text, self.moderator)
                if ai_result:
                    lang = get_chat_lang(chat_id)
                    action = ai_result.get('action', 'warn')
                    score = ai_result.get('score', 0.0)
                    backend = ai_result.get('backend', 'unknown')
                    msg_id = message.get('id')
                    
                    # Parse action (can be combined like warn_delete)
                    do_warn = 'warn' in action
                    do_delete = 'delete' in action
                    do_kick = 'kick' in action
                    do_ban = 'ban' in action
                    
                    # Build action descriptions
                    action_parts = []
                    if do_warn:
                        action_parts.append('⚠️ אזהרה' if lang == 'he' else '⚠️ Warn')
                    if do_delete:
                        action_parts.append('🗑️ מחיקה' if lang == 'he' else '🗑️ Delete')
                    if do_kick:
                        action_parts.append('👋 הסרה' if lang == 'he' else '👋 Kick')
                    if do_ban:
                        action_parts.append('🚫 חסימה' if lang == 'he' else '🚫 Ban')
                    
                    actions_text = ' + '.join(action_parts)
                    
                    if lang == 'he':
                        msg = f"🤖 *מודרציית AI ({backend})*\n\n"
                        msg += f"❌ תוכן רעיל זוהה\n"
                        msg += f"ציון: {score:.1%}\n"
                        msg += f"פעולות: {actions_text}"
                    else:
                        msg = f"🤖 *AI Moderation ({backend})*\n\n"
                        msg += f"❌ Toxic content detected\n"
                        msg += f"Score: {score:.1%}\n"
                        msg += f"Actions: {actions_text}"
                    
                    self.client.send_message(chat_id, msg)
                    
                    # Execute actions in order
                    if do_delete and msg_id:
                        self.client.delete_message(chat_id, msg_id)
                    
                    if do_warn:
                        user_display = from_id.split('@')[0]
                        warn_count, warn_limit = warn_user(chat_id, from_id, user_display, "תוכן רעיל" if lang == 'he' else "Toxic content")
                        
                        if warn_count >= warn_limit:
                            _, soft = get_warn_settings(chat_id)
                            if soft:
                                self.client.remove_participant(chat_id, from_id)
                            else:
                                add_ban(chat_id, from_id, user_display, reason="Too many warns")
                                self.client.remove_participant(chat_id, from_id)
                    
                    if do_ban:
                        user_display = from_id.split('@')[0]
                        add_ban(chat_id, from_id, user_display, reason="AI detected toxic content")
                        self.client.remove_participant(chat_id, from_id)
                    elif do_kick:
                        self.client.remove_participant(chat_id, from_id)
                    
                    return
                
                blacklisted = check_blacklist(chat_id, text)
                if blacklisted:
                    self.client.send_message(chat_id, get_text(chat_id, 'blacklist_detected'))
                    # TODO: Delete message via bridge
                    return
                
                # Check locks
                lock_violation = check_locks(chat_id, message)
                if lock_violation:
                    self.client.send_message(chat_id, get_text(chat_id, 'lock_triggered', lock_type=lock_violation))
                    # TODO: Delete message via bridge
                    return
            
            # Handle commands
            if text.startswith('/'):
                self.handle_command(text, from_id, chat_id, is_group, message)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    def handle_command(self, text: str, from_id: str, chat_id: str, is_group: bool, message: dict):
        """Handle bot commands with error protection"""
        try:
            parts = text.split(maxsplit=1)
            command = parts[0][1:].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            self._process_command(command, args, from_id, chat_id, is_group, message)
            
            # Delete command message if enabled for this group
            if is_group and should_delete_commands(chat_id):
                message_id = message.get('id')
                if message_id:
                    self.client.delete_message(chat_id, message_id)
            
        except Exception as e:
            logger.error(f"Error handling command '{text}': {e}", exc_info=True)
            try:
                self.client.send_message(chat_id, get_text(chat_id, 'error_occurred'))
            except Exception:
                pass  # Don't fail if we can't send error message
    
    def _process_command(self, command: str, args: str, from_id: str, chat_id: str, is_group: bool, message: dict):
        """Process the actual command"""
        # Extract quoted message if exists
        quoted_msg = message.get('quotedMsg')
        quoted_participant = message.get('quotedParticipant')
        
        # ===== GENERAL COMMANDS =====
        
        if command == 'start':
            self.cmd_start(chat_id)
        
        elif command == 'help':
            self.cmd_help(chat_id, from_id, is_owner(from_id), args)
        
        elif command == 'info':
            self.cmd_info(chat_id, from_id)
        
        elif command == 'ping':
            self.client.send_message(chat_id, get_text(chat_id, 'pong'))
        
        # ===== RULES COMMANDS =====
        
        elif command == 'rules':
            self.cmd_rules(chat_id)
        
        elif command == 'setrules':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_setrules(chat_id, args)
        
        # ===== WARN COMMANDS =====
        
        elif command == 'warn':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_warn(chat_id, from_id, args, message)
        
        elif command == 'warns':
            self.cmd_warns(chat_id, from_id, message)
        
        elif command == 'resetwarns':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_resetwarns(chat_id, message)
        
        elif command == 'setwarn':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_setwarn(chat_id, args)
        
        # ===== BAN/KICK COMMANDS =====
        
        elif command == 'kick':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_kick(chat_id, message)
        
        elif command == 'ban':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_ban(chat_id, message)
        
        elif command == 'unban':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_unban(chat_id, args)
        
        elif command == 'add':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_add(chat_id, args)
        
        elif command == 'invite':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_invite(chat_id)

        elif command == 'delcmds':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_delcmds(chat_id, args)
        
        # ===== WELCOME COMMANDS =====
        
        elif command == 'setwelcome':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_setwelcome(chat_id, args)
        
        elif command == 'welcome':
            self.cmd_welcome(chat_id)
        
        # ===== BLACKLIST COMMANDS =====
        
        elif command == 'blacklist':
            self.cmd_blacklist(chat_id)
        
        elif command == 'addblacklist':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_addblacklist(chat_id, args)
        
        elif command == 'rmblacklist':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_rmblacklist(chat_id, args)
        
        # ===== LOCK COMMANDS =====
        
        elif command == 'lock':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_lock(chat_id, args)
        
        elif command == 'unlock':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_unlock(chat_id, args)
        
        elif command == 'locks':
            self.cmd_locks(chat_id)
        
        # ===== AI MODERATION COMMANDS =====
        
        elif command == 'aimod':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimod(chat_id, args)
        
        elif command == 'aimodset':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodset(chat_id, args)
        
        elif command == 'aimodstatus':
            self.cmd_aimodstatus(chat_id)
        
        elif command == 'aimodkey':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodkey(chat_id, args)
        
        elif command == 'aimodbackend':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodbackend(chat_id, args)
        
        elif command == 'aimodaction':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodaction(chat_id, args)
        
        elif command == 'aimodthreshold':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodthreshold(chat_id, args)
        
        elif command == 'aihelp':
            self.cmd_aihelp(chat_id)
        
        elif command == 'aitest':
            if not is_admin(chat_id, from_id, self.client):
                self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aitest(chat_id, args, quoted_msg)
        
        # ===== LANGUAGE COMMAND =====
        
        elif command == 'setlang' or command == 'lang':
            if not is_admin(chat_id, from_id, self.client):
                msg = get_text(chat_id, 'admin_only')
                self.client.send_message(chat_id, msg)
                return
            self.cmd_setlang(chat_id, args)
        
        else:
            msg = get_text(chat_id, 'unknown_command', command=command)
            self.client.send_message(chat_id, msg)
    
    # ===== COMMAND IMPLEMENTATIONS =====
    
    def cmd_start(self, chat_id: str):
        """Start command"""
        msg = get_text(chat_id, 'start_msg')
        self.client.send_message(chat_id, msg)
    
    def cmd_help(self, chat_id: str, from_id: str, is_owner: bool, args: str = ''):
        """Help command - show general help or specific command help"""
        lang = get_chat_lang(chat_id)
        is_admin_user = is_admin(chat_id, from_id, self.client) or is_owner
        
        # If a specific command was requested
        if args:
            cmd_name = args.lower().strip().lstrip('/')
            cmd_data = COMMAND_HELP.get(lang, {}).get(cmd_name)
            
            if cmd_data:
                if cmd_data['admin'] and not is_admin_user:
                    self.client.send_message(chat_id, get_text(chat_id, 'admin_only'))
                    return
                msg = get_text(chat_id, 'help_cmd_header', cmd=cmd_name)
                msg += get_text(chat_id, 'help_cmd_usage', usage=cmd_data['usage'])
                msg += get_text(chat_id, 'help_cmd_desc', desc=cmd_data['desc'])
                msg += get_text(chat_id, 'help_cmd_example', example=cmd_data['example'])
                if cmd_data['admin']:
                    msg += get_text(chat_id, 'help_cmd_admin')
                self.client.send_message(chat_id, msg)
                return
            else:
                self.client.send_message(chat_id, get_text(chat_id, 'help_cmd_not_found', cmd=cmd_name))
                return
        
        # General help
        msg = get_text(chat_id, 'help_general')
        if lang == 'he':
            msg += '''\n/start - הפעל את הבוט
/help - הצג הודעה זו
/info - מידע על הבוט
/ping - בדוק סטטוס'''
            if is_admin_user:
                msg += '\n/setlang <he|en> - שנה שפה'
            msg += '\n\n'
        else:
            msg += '''\n/start - Start the bot
/help - Show this message
/info - Bot information
/ping - Check bot status'''
            if is_admin_user:
                msg += '\n/setlang <code> - Set language (he/en)'
            msg += '\n\n'
        
        msg += get_text(chat_id, 'help_rules')
        if lang == 'he':
            msg += '\n/rules - הצג חוקי קבוצה'
            if is_admin_user:
                msg += '\n/setrules <טקסט> - הגדר חוקים (מנהל)'
            msg += '\n\n'
        else:
            msg += '\n/rules - Show group rules'
            if is_admin_user:
                msg += '\n/setrules <text> - Set group rules (admin)'
            msg += '\n\n'
        
        msg += get_text(chat_id, 'help_warns')
        if lang == 'he':
            msg += '\n/warns - בדוק אזהרות'
            if is_admin_user:
                msg += '\n/warn - אזהרה למשתמש (השב להודעה)'
                msg += '\n/resetwarns - אפס אזהרות (השב להודעה)'
                msg += '\n/setwarn <מספר> - הגדר מגבלת אזהרות (מנהל)'
            msg += '\n\n'
        else:
            msg += '\n/warns - Check user warns'
            if is_admin_user:
                msg += '\n/warn - Warn a user (reply to message)'
                msg += '\n/resetwarns - Reset warns (reply to message)'
                msg += '\n/setwarn <number> - Set warn limit (admin)'
            msg += '\n\n'
        
        if is_admin_user:
            msg += get_text(chat_id, 'help_moderation')
            if lang == 'he':
                msg += '''\n/kick - בעט משתמש (השב להודעה)
/ban - חסום משתמש (השב להודעה)
/unban <טלפון> - בטל חסימה של משתמש
/add <טלפון> - הוסף משתמש לקבוצה
/invite - קבל קישור הזמנה לקבוצה
/delcmds <on|off|status> - מחיקת פקודות\n\n'''
            else:
                msg += '''\n/kick - Kick user (reply to message)
/ban - Ban user (reply to message)
/unban <phone> - Unban a user
/add <phone> - Add user to group
/invite - Get group invite link
/delcmds <on|off|status> - Command deletion\n\n'''
        
        msg += get_text(chat_id, 'help_welcome')
        if lang == 'he':
            msg += '\n/welcome - הצג הודעה נוכחית'
            if is_admin_user:
                msg += '\n/setwelcome <טקסט> - הגדר הודעת קבלת פנים (מנהל)'
            msg += '\n\n'
        else:
            msg += '\n/welcome - Show current welcome'
            if is_admin_user:
                msg += '\n/setwelcome <text> - Set welcome message (admin)'
            msg += '\n\n'
        
        msg += get_text(chat_id, 'help_blacklist')
        if lang == 'he':
            msg += '\n/blacklist - הצג מילים חסומות'
            if is_admin_user:
                msg += '\n/addblacklist <מילה> - הוסף לרשימה (מנהל)'
                msg += '\n/rmblacklist <מילה> - הסר מהרשימה (מנהל)'
            msg += '\n\n'
        else:
            msg += '\n/blacklist - Show blacklisted words'
            if is_admin_user:
                msg += '\n/addblacklist <word> - Add word to blacklist (admin)'
                msg += '\n/rmblacklist <word> - Remove from blacklist (admin)'
            msg += '\n\n'
        
        msg += get_text(chat_id, 'help_locks')
        if lang == 'he':
            msg += '\n/locks - הצג נעילות נוכחיות'
            if is_admin_user:
                msg += '\n/lock <סוג> - נעל links/stickers/media (מנהל)'
                msg += '\n/unlock <סוג> - בטל נעילה (מנהל)'
            msg += '\n\n'
        else:
            msg += '\n/locks - Show current locks'
            if is_admin_user:
                msg += '\n/lock <type> - Lock links/stickers/media (admin)'
                msg += '\n/unlock <type> - Unlock (admin)'
            msg += '\n\n'

        # Language section
        if is_admin_user:
            if lang == 'he':
                msg += '''🌍 *שפה:*
/lang - הצג שפה נוכחית
/lang he|en - שנה שפה (מנהל)\n\n'''
            else:
                msg += '''🌍 *Language:*
/lang - Show current language
/lang he|en - Change language (admin)\n\n'''
        
        msg += get_text(chat_id, 'help_ai')
        if lang == 'he':
            msg += '\n/aimodstatus - בדוק הגדרות AI\n/aihelp - מדריך מלא'
            if is_admin_user:
                msg += '\n/aimod on|off - הפעל/כבה מודרציית AI (מנהל)'
                msg += '\n/aitest - בדיקת הודעה עם AI (מנהל)'
            msg += '\n\n'
        else:
            msg += '\n/aimodstatus - Check AI settings\n/aihelp - Detailed AI moderation guide'
            if is_admin_user:
                msg += '\n/aimod on|off - Enable/disable AI moderation (admin)'
                msg += '\n/aitest - Test message with AI (admin)'
            msg += '\n\n'
        
        msg += get_text(chat_id, 'help_note')
        msg += get_text(chat_id, 'help_use_cmd')
        self.client.send_message(chat_id, msg)
    
    def cmd_info(self, chat_id: str, from_id: str):
        """Info command"""
        msg = get_text(chat_id, 'bot_info', from_id=from_id, chat_id=chat_id)
        self.client.send_message(chat_id, msg)
    
    def cmd_rules(self, chat_id: str):
        """Show rules"""
        rules = get_rules(chat_id)
        if rules:
            msg = get_text(chat_id, 'rules_show', rules=rules)
        else:
            msg = get_text(chat_id, 'rules_not_set')
        self.client.send_message(chat_id, msg)
    
    def cmd_setrules(self, chat_id: str, rules_text: str):
        """Set rules"""
        if not rules_text:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_setrules'))
            return
        
        set_rules(chat_id, rules_text)
        self.client.send_message(chat_id, get_text(chat_id, 'rules_set'))
    
    def cmd_warn(self, chat_id: str, warner_id: str, reason: str, message: dict):
        """Warn a user"""
        # Check if this is a reply to another message
        quoted_msg = message.get('quotedMsg')
        quoted_participant = message.get('quotedParticipant')
        
        if not quoted_msg or not quoted_participant:
            self.client.send_message(chat_id, get_text(chat_id, 'warn_usage'))
            return
        
        # Get target user ID
        target_user = quoted_participant
        
        # Get user name for display
        user_display = target_user.split('@')[0]
        
        # Add warning and get count
        reason = reason or get_text(chat_id, 'no_reason')
        count, limit = warn_user(chat_id, target_user, user_display, reason)
        
        # Get warn settings
        _, soft = get_warn_settings(chat_id)
        
        # Check if user reached limit
        limit_reached = count >= limit
        if limit_reached:
            msg = get_text(chat_id, 'warn_limit_reached', user=user_display)
            self.client.send_message(chat_id, msg)
            
            # Kick or ban based on soft setting
            if not soft:
                # Ban (remove from group)
                success = self.client.remove_participant(chat_id, target_user)
                if success:
                    self.client.send_message(chat_id, get_text(chat_id, 'user_banned', user=user_display))
        else:
            msg = get_text(chat_id, 'warn_issued', user=user_display, reason=reason, count=count, limit=limit)
            self.client.send_message(chat_id, msg)
    
    def cmd_warns(self, chat_id: str, user_id: str, message: dict):
        """Check warns"""
        # Check if replying to someone
        quoted_participant = message.get('quotedParticipant')
        target_user = quoted_participant if quoted_participant else user_id
        
        warns = get_warns(chat_id, target_user)
        limit, soft = get_warn_settings(chat_id)
        
        user_display = target_user.split('@')[0]
        
        if not warns:
            msg = get_text(chat_id, 'warns_none', user=user_display)
        else:
            msg = get_text(chat_id, 'warns_list', count=len(warns), limit=limit)
            for i, warn in enumerate(warns, 1):
                reason = warn.reason or get_text(chat_id, 'no_reason')
                msg += f"{i}. {reason}\n"
        
        self.client.send_message(chat_id, msg)
    
    def cmd_resetwarns(self, chat_id: str, message: dict):
        """Reset warns"""
        # Check if replying to someone
        quoted_participant = message.get('quotedParticipant')
        
        if not quoted_participant:
            self.client.send_message(chat_id, get_text(chat_id, 'resetwarns_usage'))
            return
        
        # Reset warns
        reset_user_warns(chat_id, quoted_participant)
        user_display = quoted_participant.split('@')[0]
        self.client.send_message(chat_id, get_text(chat_id, 'warns_reset', user=user_display))
    
    def cmd_setwarn(self, chat_id: str, limit_str: str):
        """Set warn limit"""
        try:
            limit = int(limit_str)
            if limit < 1:
                raise ValueError
            set_warn_limit(chat_id, limit)
            self.client.send_message(chat_id, get_text(chat_id, 'warn_limit_set', limit=limit))
        except:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_setwarn'))
    
    def cmd_kick(self, chat_id: str, message: dict):
        """Kick user"""
        # Check if replying to someone
        quoted_participant = message.get('quotedParticipant')
        
        if not quoted_participant:
            self.client.send_message(chat_id, get_text(chat_id, 'kick_usage'))
            return
        
        # Kick the user
        user_display = quoted_participant.split('@')[0]
        success = self.client.remove_participant(chat_id, quoted_participant)
        
        if success:
            self.client.send_message(chat_id, get_text(chat_id, 'user_kicked', user=user_display))
        else:
            self.client.send_message(chat_id, get_text(chat_id, 'kick_failed'))
    
    def cmd_ban(self, chat_id: str, message: dict):
        """Ban user"""
        # Check if replying to someone
        quoted_participant = message.get('quotedParticipant')
        
        if not quoted_participant:
            self.client.send_message(chat_id, get_text(chat_id, 'ban_usage'))
            return
        
        # Ban = kick + add to ban list
        user_display = quoted_participant.split('@')[0]
        
        # Add to ban list in DB
        add_ban(chat_id, quoted_participant)
        
        # Remove from group
        success = self.client.remove_participant(chat_id, quoted_participant)
        
        if success:
            self.client.send_message(chat_id, get_text(chat_id, 'user_banned', user=user_display))
        else:
            self.client.send_message(chat_id, get_text(chat_id, 'ban_failed'))
    
    def cmd_unban(self, chat_id: str, phone: str):
        """Unban a user"""
        if not phone:
            self.client.send_message(chat_id, get_text(chat_id, 'unban_usage'))
            return
        
        # Clean phone number
        phone = phone.strip().replace('+', '').replace('-', '').replace(' ', '')
        
        # Validate phone format
        if not phone.isdigit() or len(phone) < 10:
            self.client.send_message(chat_id, get_text(chat_id, 'invalid_phone', phone=phone))
            return
        
        user_id = f"{phone}@c.us"
        
        # Remove from ban list
        if remove_ban(chat_id, user_id):
            self.client.send_message(chat_id, get_text(chat_id, 'user_unbanned', user=phone))
        else:
            self.client.send_message(chat_id, get_text(chat_id, 'user_not_banned'))
    
    def cmd_add(self, chat_id: str, phones: str):
        """Add users to group"""
        if not phones:
            self.client.send_message(chat_id, get_text(chat_id, 'add_usage'))
            return
        
        # Parse phone numbers (comma or space separated)
        phone_list = [p.strip().replace('+', '').replace('-', '').replace(' ', '') 
                      for p in phones.replace(',', ' ').split()]
        
        # Validate and convert to user IDs
        participants = []
        for phone in phone_list:
            if phone.isdigit() and len(phone) >= 10:
                # Convert local Israeli number (0...) to international (972...)
                if phone.startswith('0'):
                    phone = '972' + phone[1:]
                participants.append(f"{phone}@c.us")
            else:
                self.client.send_message(chat_id, get_text(chat_id, 'invalid_phone', phone=phone))
                return
        
        # Add to group
        success = self.client.add_participants(chat_id, participants)
        
        if success:
            if len(participants) == 1:
                self.client.send_message(chat_id, get_text(chat_id, 'user_added', user=phone_list[0]))
            else:
                self.client.send_message(chat_id, get_text(chat_id, 'users_added', count=len(participants)))
        else:
            self.client.send_message(chat_id, get_text(chat_id, 'user_add_failed', user=phones))
    
    def cmd_invite(self, chat_id: str):
        """Get group invite link"""
        link = self.client.get_invite_link(chat_id)
        
        if link:
            self.client.send_message(chat_id, get_text(chat_id, 'invite_link', link=link))
        else:
            self.client.send_message(chat_id, get_text(chat_id, 'invite_failed'))

    def cmd_delcmds(self, chat_id: str, args: str):
        """Enable/disable command deletion"""
        action = (args or '').strip().lower()
        if action in ('on', 'enable', 'enabled'):
            set_delete_commands(chat_id, True)
            self.client.send_message(chat_id, get_text(chat_id, 'delete_commands_on'))
        elif action in ('off', 'disable', 'disabled'):
            set_delete_commands(chat_id, False)
            self.client.send_message(chat_id, get_text(chat_id, 'delete_commands_off'))
        else:
            status = 'ON' if should_delete_commands(chat_id) else 'OFF'
            self.client.send_message(chat_id, get_text(chat_id, 'delete_commands_status', status=status))
    
    def cmd_setwelcome(self, chat_id: str, welcome_text: str):
        """Set welcome message"""
        if not welcome_text:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_setwelcome'))
            return
        
        set_welcome(chat_id, welcome_text)
        self.client.send_message(chat_id, get_text(chat_id, 'welcome_set'))
    
    def cmd_welcome(self, chat_id: str):
        """Show welcome message"""
        welcome = get_welcome(chat_id)
        if welcome:
            msg = get_text(chat_id, 'welcome_current', message=welcome)
        else:
            msg = get_text(chat_id, 'welcome_not_set_admin')
        self.client.send_message(chat_id, msg)
    
    def cmd_blacklist(self, chat_id: str):
        """Show blacklist"""
        words = get_blacklist(chat_id)
        if words:
            msg = get_text(chat_id, 'blacklist_list', count=len(words)) + "\n".join(f"• {w}" for w in words)
        else:
            msg = get_text(chat_id, 'blacklist_empty_admin')
        self.client.send_message(chat_id, msg)
    
    def cmd_addblacklist(self, chat_id: str, word: str):
        """Add word to blacklist"""
        if not word:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_addblacklist'))
            return
        
        add_blacklist(chat_id, word)
        self.client.send_message(chat_id, get_text(chat_id, 'blacklist_added', word=word))
    
    def cmd_rmblacklist(self, chat_id: str, word: str):
        """Remove word from blacklist"""
        if not word:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_rmblacklist'))
            return
        
        remove_blacklist(chat_id, word)
        self.client.send_message(chat_id, get_text(chat_id, 'blacklist_removed', word=word))
    
    def cmd_lock(self, chat_id: str, lock_type: str):
        """Lock a type"""
        valid_types = ['links', 'stickers', 'media']
        if lock_type.lower() not in valid_types:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_lock'))
            return
        
        set_lock(chat_id, lock_type.lower(), True)
        self.client.send_message(chat_id, get_text(chat_id, 'locked', lock_type=lock_type))
    
    def cmd_unlock(self, chat_id: str, lock_type: str):
        """Unlock a type"""
        valid_types = ['links', 'stickers', 'media']
        if lock_type.lower() not in valid_types:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_unlock'))
            return
        
        set_lock(chat_id, lock_type.lower(), False)
        self.client.send_message(chat_id, get_text(chat_id, 'unlocked', lock_type=lock_type))
    
    def cmd_locks(self, chat_id: str):
        """Show current locks"""
        locks = get_locks(chat_id)
        msg = get_text(chat_id, 'locks_status')
        links_status = get_text(chat_id, 'lock_locked') if locks['links'] else get_text(chat_id, 'lock_unlocked')
        stickers_status = get_text(chat_id, 'lock_locked') if locks['stickers'] else get_text(chat_id, 'lock_unlocked')
        media_status = get_text(chat_id, 'lock_locked') if locks['media'] else get_text(chat_id, 'lock_unlocked')
        msg += f"{get_text(chat_id, 'links_label')}: {links_status}\n"
        msg += f"{get_text(chat_id, 'stickers_label')}: {stickers_status}\n"
        msg += f"{get_text(chat_id, 'media_label')}: {media_status}"
        self.client.send_message(chat_id, msg)
    
    def cmd_aimod(self, chat_id: str, args: str):
        """Enable/disable AI moderation"""
        from bot_core.services.ai_moderation_service import set_ai_enabled
        
        if not args:
            # Show current status (like /aimodstatus)
            self.cmd_aimodstatus(chat_id)
            return
        
        if args.lower() not in ['on', 'off']:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_aimod'))
            return
        
        enabled = args.lower() == 'on'
        set_ai_enabled(chat_id, enabled)
        
        if enabled:
            msg = get_text(chat_id, 'aimod_on')
        else:
            msg = get_text(chat_id, 'aimod_off')
        
        self.client.send_message(chat_id, msg)
    
    def cmd_aimodset(self, chat_id: str, args: str):
        """Set AI moderation thresholds"""
        parts = args.split()
        if len(parts) != 2:
            msg = """❌ Usage: /aimodset <category> <threshold>

*Categories:*
• toxicity - Toxic/hateful content
• spam - Spam messages
• sexual - Sexual content
• threat - Threatening messages

*Threshold:* 0-100 (higher = more strict)
Example: /aimodset spam 70"""
            self.client.send_message(chat_id, msg)
            return
        
        category = parts[0].lower()
        try:
            threshold = int(parts[1])
            if threshold < 0 or threshold > 100:
                raise ValueError
        except:
            self.client.send_message(chat_id, get_text(chat_id, 'aimod_threshold_invalid'))
            return
        
        valid_categories = ['toxicity', 'spam', 'sexual', 'threat']
        if category not in valid_categories:
            self.client.send_message(
                chat_id,
                f"❌ Invalid category. Choose from: {', '.join(valid_categories)}"
            )
            return
        
        set_ai_threshold(chat_id, category, threshold)
        self.client.send_message(
            chat_id,
            f"✅ {category.title()} threshold set to {threshold}%"
        )
    
    def cmd_aihelp(self, chat_id: str):
        """Show detailed AI moderation help"""
        lang = get_chat_lang(chat_id)
        msg = get_text(chat_id, 'aihelp_full')
        self.client.send_message(chat_id, msg)
    
    def cmd_aitest(self, chat_id: str, args: str, quoted_msg: Optional[str] = None):
        """Test message with AI moderation and show detailed scores"""
        # Get text to test
        test_text = None
        if quoted_msg:
            # quoted_msg is a dict with 'body' field
            if isinstance(quoted_msg, dict):
                test_text = quoted_msg.get('body', '')
            else:
                test_text = quoted_msg
        elif args:
            test_text = args
        else:
            msg = "❌ *שימוש:* /aitest\n\nהשב להודעה או כתוב טקסט:\n/aitest בדוק את הטקסט הזה"
            self.client.send_message(chat_id, msg)
            return

        if not isinstance(test_text, str):
            test_text = str(test_text)
        if not test_text.strip():
            msg = "❌ *שימוש:* /aitest\n\nהשב להודעה או כתוב טקסט:\n/aitest בדוק את הטקסט הזה"
            self.client.send_message(chat_id, msg)
            return
        
        # Get AI settings
        settings = get_ai_settings(chat_id)
        
        # Check with AI
        from bot_core.content_filter import ContentModerator
        moderator = ContentModerator(
            backend=settings.backend,
            api_key=settings.api_key
        )

        requested_backend = settings.backend
        used_backend = moderator.backend
        
        # Convert percentage thresholds to 0-1 scale
        thresholds = {
            'toxicity': settings.toxicity_threshold / 100.0,
            'spam': settings.spam_threshold / 100.0,
            'sexual': settings.sexual_threshold / 100.0,
            'threat': settings.threat_threshold / 100.0,
        }
        
        result = moderator.check_message(test_text, thresholds)
        
        # Format response
        backend_emoji = {
            'perspective': '🌍',
            'openai': '🤖',
            'azure': '☁️',
            'detoxify': '💻',
            'rules': '📋'
        }
        
        msg = f"🔍 *AI Moderation Test*\n\n"
        msg += f"Backend: {backend_emoji.get(requested_backend, '❓')} {requested_backend}\n"
        if used_backend != requested_backend:
            import os
            missing_key = requested_backend in ['perspective', 'openai', 'azure'] and not (
                settings.api_key or os.getenv(f'{requested_backend.upper()}_API_KEY')
            )
            if missing_key:
                msg += f"Backend used: {backend_emoji.get(used_backend, '❓')} {used_backend} (אין API key)\n"
            else:
                msg += f"Backend used: {backend_emoji.get(used_backend, '❓')} {used_backend} (fallback)\n"
        msg += "\n"
        msg += f"📝 *Text:* {test_text[:100]}{'...' if len(test_text) > 100 else ''}\n\n"
        msg += f"*Scores:*\n"
        
        if result.scores:
            for category, score in sorted(result.scores.items()):
                percentage = score * 100
                if category == 'promotion':
                    threshold_value = thresholds.get('spam', 0.7)
                else:
                    threshold_value = thresholds.get(category, 0.7)
                threshold = threshold_value * 100
                emoji = '🔴' if score >= threshold_value else '🟢'
                msg += f"{emoji} {category.title()}: {percentage:.1f}% (סף: {threshold:.0f}%)\n"
        else:
            msg += "_No scores available_\n"
        
        msg += f"\n*Result:* "
        if result.is_flagged:
            msg += f"❌ *FLAGGED*\n"
            msg += f"Type: {result.violation_type}\n"
            msg += f"Confidence: {result.confidence*100:.1f}%\n"
            msg += f"Reason: {result.reason}"
        else:
            msg += f"✅ *PASSED*\n"
            msg += f"Reason: {result.reason}"
        
        self.client.send_message(chat_id, msg)
    
    def cmd_aimodstatus(self, chat_id: str):
        """Show AI moderation status"""
        from bot_core.services.ai_moderation_service import get_ai_settings
        settings = get_ai_settings(chat_id)
        
        if not settings['enabled']:
            msg = "❌ AI Moderation is *disabled*\n\nUse /aimod on to enable"
        else:
            backend_emoji = {
                'perspective': '🌍',
                'openai': '🤖',
                'azure': '☁️',
                'detoxify': '💻'
            }
            backend_name = {
                'perspective': 'Google Perspective (Hebrew+English)',
                'openai': 'OpenAI (English)',
                'azure': 'Azure (Hebrew+English)',
                'detoxify': 'Detoxify (Multilingual - Hebrew+English)'
            }
            action_emoji = {
                'warn': '⚠️',
                'delete': '🗑️',
                'kick': '👋',
                'ban': '🚫',
                'warn_delete': '⚠️🗑️',
                'delete_kick': '🗑️👋',
                'delete_ban': '🗑️🚫'
            }
            
            action_desc = {
                'warn': 'אזהרה',
                'delete': 'מחיקה',
                'kick': 'הסרה',
                'ban': 'חסימה',
                'warn_delete': 'אזהרה + מחיקה',
                'delete_kick': 'מחיקה + הסרה',
                'delete_ban': 'מחיקה + חסימה'
            }
            
            backend = settings['backend']
            action = settings['action']
            action_display = f"{action_emoji.get(action, '❓')} {action_desc.get(action, action)}"
            
            msg = "🤖 *AI Moderation Status*\n\n"
            msg += f"Status: ✅ Enabled\n"
            msg += f"Backend: {backend_emoji.get(backend, '❓')} {backend_name.get(backend, backend)}\n"
            msg += f"API Key: {'✅ Set' if settings['api_key'] else '❌ Not set'}\n"
            msg += f"Threshold: {settings['threshold']}%\n"
            msg += f"Action: {action_display}\n\n"
            
            msg += "*Available actions:*\n"
            msg += "• warn - אזהרה למשתמש\n"
            msg += "• delete - מחיקת הודעה\n"
            msg += "• kick - הסרה מהקבוצה\n"
            msg += "• ban - חסימה והסרה\n\n"
            
            msg += "*Commands:*\n"
            msg += "/aimodbackend <backend> - החלף מנוע\n"
            msg += "/aimodthreshold <0-100> - שנה רגישות\n"
            msg += "/aimodaction <action> - שנה פעולה"
        
        self.client.send_message(chat_id, msg)
    
    def cmd_aimodkey(self, chat_id: str, args: str):
        """Set API key for this group"""
        parts = args.split(maxsplit=1)
        if len(parts) != 2:
            msg = """❌ *שימוש:* /aimodkey <backend> <api_key>

🤖 *Backends זמינים:*

🌍 *perspective* (Google Perspective API)
   • תומך: עברית + אנגלית
   • מומלץ: ✅ מצוין לעברית!
   • API Key: חינם עד 1M בדיקות/חודש
   • איך להשיג: https://perspectiveapi.com

☁️ *azure* (Azure Content Safety)
   • תומך: עברית + אנגלית + 100 שפות
   • מומלץ: ✅ הכי מדויק!
   • API Key: חינם עד 5K בדיקות/חודש
   • איך להשיג: https://azure.microsoft.com/products/ai-services/ai-content-safety

🤖 *openai* (OpenAI Moderation)
   • תומך: אנגלית בלבד
   • API Key: דרוש חשבון OpenAI
   • איך להשיג: https://platform.openai.com

💻 *detoxify* (מודל מקומי)
   • תומך: אנגלית בלבד
   • ללא צורך ב-API key ✅
   • דורש התקנה: pip install detoxify

📋 *rules* (זיהוי דפוסים)
   • תומך: עברית + אנגלית ✅
   • ללא צורך ב-API key ✅
   • מומלץ להתחלה!
   • מהיר ויעיל

*דוגמאות שימוש:*
/aimodkey perspective AIzaSyA...
/aimodkey azure a1b2c3d4e5...
/aimodkey rules (אין צורך במפתח)

🔒 *אבטחה:* המפתח נשמר רק עבור הקבוצה הזו
💰 *עלות:* כל קבוצה יכולה להשתמש במפתח משלה

📚 *מדריך מלא:* AI_MODERATION_SETUP.md"""
            self.client.send_message(chat_id, msg)
            return
        
        backend = parts[0].lower()
        api_key = parts[1]
        
        valid_backends = ['perspective', 'openai', 'azure', 'detoxify', 'rules']
        if backend not in valid_backends:
            self.client.send_message(
                chat_id,
                f"❌ Invalid backend. Choose from: {', '.join(valid_backends)}"
            )
            return
        
        # No key needed for detoxify and rules
        if backend in ['detoxify', 'rules']:
            set_ai_backend(chat_id, backend, None)
            self.client.send_message(
                chat_id,
                f"✅ Backend set to *{backend}*\n\nNo API key needed for this backend."
            )
        else:
            set_ai_backend(chat_id, backend, api_key)
            self.client.send_message(
                chat_id,
                f"✅ API key saved for *{backend}* backend!\n\n"
                f"🔒 Your key is stored securely and used only for this group.\n\n"
                f"Use /aimod on to enable AI moderation."
            )
    
    def cmd_aimodbackend(self, chat_id: str, backend: str):
        """Set AI backend without changing API key"""
        if not backend:
            msg = """❌ *שימוש:* /aimodbackend <backend>

🔄 *החלפת מנוע AI* (ללא שינוי API key)

🤖 *Backends זמינים:*

🌍 *perspective* - Google Perspective
   • תומך: עברית + אנגלית + 30 שפות
   • חינם (1M בקשות/יום)
   • מדויק ביותר לעברית ✅

☁️ *azure* - Azure Content Safety
   • תומך: עברית + אנגלית + 100 שפות
   • חינם עד 5K/חודש
   • רמה ארגונית ✅

🤖 *openai* - OpenAI Moderation
   • תומך: אנגלית בלבד
   • חינם
   • מדויק מאוד

💻 *detoxify* - מודל מקומי
   • תומך: אנגלית בלבד
   • חינם, רץ מקומי
   • ללא צורך ב-API key ✅

📋 *rules* - זיהוי דפוסים
   • תומך: עברית + אנגלית ✅
   • חינם
   • ללא צורך בהתקנה ✅
   • מומלץ להתחלה!

*דוגמה:*
/aimodbackend perspective

💡 *טיפ:* השתמש ב-/aimodkey להגדרת API key לפני."""
            self.client.send_message(chat_id, msg)
            return
        
        backend = backend.lower()
        valid_backends = ['perspective', 'openai', 'azure', 'detoxify', 'rules']
        
        if backend not in valid_backends:
            self.client.send_message(
                chat_id,
                f"❌ Invalid backend. Choose from: {', '.join(valid_backends)}"
            )
            return
        
        settings = get_ai_settings(chat_id)
        
        # Check if API key is needed and set
        if backend in ['perspective', 'openai', 'azure']:
            if not settings.api_key:
                import os
                if not os.getenv(f'{backend.upper()}_API_KEY'):
                    self.client.send_message(
                        chat_id,
                        f"❌ *{backend}* דורש API key!\n\n"
                        f"🔑 הגדר מפתח תחילה:\n"
                        f"/aimodkey {backend} YOUR_KEY\n\n"
                        f"או הגדר משתנה סביבה:\n"
                        f"{backend.upper()}_API_KEY\n\n"
                        f"⚠️ ה-backend לא שונה. תחילה הגדר API key."
                    )
                    return  # Don't change backend without API key
        
        set_ai_backend(chat_id, backend)
        self.client.send_message(
            chat_id,
            f"✅ Backend set to *{backend}*"
        )
    
    def cmd_aimodaction(self, chat_id: str, action: str):
        """Set AI moderation action(s)"""
        from bot_core.services.ai_moderation_service import set_ai_action
        
        if not action:
            msg = """❌ *שימוש:* /aimodaction <action>

⚡ *פעולות זמינות:*

⚠️ *warn* - אזהרה בלבד
   • הוספת אזהרה למשתמש
   • אם מגיע למקסימום אזהרות - kick/ban

🗑️ *delete* - מחיקה בלבד
   • מחיקה אוטומטית של ההודעה הרעילה

👋 *kick* - הסרה בלבד
   • הסרת המשתמש מהקבוצה
   • יכול לחזור דרך קישור

🚫 *ban* - חסימה והסרה
   • חסימת המשתמש והסרתו
   • לא יכול לחזור

💡 *פעולות משולבות:*

⚠️🗑️ *warn_delete* - אזהרה + מחיקה
   • גם מזהיר וגם מוחק את ההודעה

🗑️👋 *delete_kick* - מחיקה + הסרה
   • מוחק הודעה ומסיר מהקבוצה

🗑️🚫 *delete_ban* - מחיקה + חסימה
   • מוחק הודעה וחוסם לצמיתות

*דוגמאות:*
/aimodaction delete
/aimodaction warn_delete
/aimodaction delete_ban"""
            self.client.send_message(chat_id, msg)
            return
        
        action = action.lower()
        valid_actions = ['warn', 'delete', 'kick', 'ban', 'warn_delete', 'delete_kick', 'delete_ban']
        
        if action not in valid_actions:
            self.client.send_message(
                chat_id,
                f"❌ פעולה לא תקינה: {action}\nבחר מ: {', '.join(valid_actions)}"
            )
            return
        
        set_ai_action(chat_id, action)
        
        action_desc = {
            'warn': '⚠️ אזהרה',
            'delete': '🗑️ מחיקה',
            'kick': '👋 הסרה',
            'ban': '🚫 חסימה',
            'warn_delete': '⚠️ אזהרה + 🗑️ מחיקה',
            'delete_kick': '🗑️ מחיקה + 👋 הסרה',
            'delete_ban': '🗑️ מחיקה + 🚫 חסימה'
        }
        
        self.client.send_message(
            chat_id,
            f"✅ פעולת AI moderation שונתה ל:\n{action_desc[action]}"
        )
    
    def cmd_aimodthreshold(self, chat_id: str, threshold_str: str):
        """Set AI moderation threshold"""
        from bot_core.services.ai_moderation_service import set_ai_threshold
        
        if not threshold_str:
            msg = """❌ *שימוש:* /aimodthreshold <0-100>

🎯 *רגישות זיהוי תוכן רעיל*

הסף קובע כמה רגיש הבוט:
• 0-40: רגיש מעט (רק תוכן ממש רעיל)
• 40-70: רגישות בינונית ✅ (מומלץ)
• 70-100: רגיש מאוד (עלול לזהות גם תוכן תקין)

*דוגמאות:*
/aimodthreshold 60 - רגישות בינונית
/aimodthreshold 80 - רגיש מאוד

💡 *טיפ:* התחל עם 60 והתאם לפי הצורך"""
            self.client.send_message(chat_id, msg)
            return
        
        try:
            threshold = int(threshold_str)
            if threshold < 0 or threshold > 100:
                raise ValueError
        except:
            self.client.send_message(
                chat_id,
                "❌ הסף חייב להיות מספר בין 0 ל-100"
            )
            return
        
        set_ai_threshold(chat_id, threshold)
        
        sensitivity = "נמוכה" if threshold < 40 else "בינונית" if threshold < 70 else "גבוהה"
        
        self.client.send_message(
            chat_id,
            f"✅ סף הזיהוי שונה ל-{threshold}%\n"
            f"רגישות: {sensitivity}"
        )
    
    def cmd_setlang(self, chat_id: str, args: str):
        """Set group language"""
        if not args:
            # Show current language
            current_lang = get_chat_lang(chat_id)
            lang_name = LANG_NAMES.get(current_lang, current_lang)
            msg = get_text(chat_id, 'lang_current', lang_name=lang_name)
            self.client.send_message(chat_id, msg)
            return
        
        lang_code = args.lower().strip()
        
        # Validate language code
        if lang_code not in TRANSLATIONS:
            msg = get_text(chat_id, 'lang_invalid')
            self.client.send_message(chat_id, msg)
            return
        
        # Set language
        set_chat_lang(chat_id, lang_code)
        lang_name = LANG_NAMES.get(lang_code, lang_code)
        msg = get_text(chat_id, 'lang_changed', lang=lang_code, lang_name=lang_name)
        self.client.send_message(chat_id, msg)
    
    def handle_group_join(self, event: dict):
        """Handle group join event - send welcome message"""
        try:
            chat_id = event.get('chatId')
            participants = event.get('participants', [])
            
            if not chat_id or not participants:
                return
            
            logger.info(f"Group join event in {chat_id}: {participants}")
            
            # Get welcome message for this chat
            welcome_msg = get_welcome(chat_id)
            if not welcome_msg:
                return
            
            # Send welcome for each participant
            for participant_id in participants:
                # Extract phone number for mention
                phone = participant_id.replace('@c.us', '').replace('@lid', '')
                
                # Replace {mention} with the participant mention
                message = welcome_msg.replace('{mention}', f'@{phone}')
                
                self.client.send_message(chat_id, message)
                logger.info(f"Sent welcome message to {participant_id}")
        except Exception as e:
            logger.error(f"Error handling group join: {e}")
    
    def run(self):
        """Start the bot"""
        logger.info("Starting WhatsApp Bot...")
        logger.info(f"Owner: {Config.OWNER_ID}")
        
        # Register message handler
        self.client.on_message(self.handle_message)
        
        # Register group join handler for welcome messages
        self.client.on_group_join(self.handle_group_join)
        
        # Start callback server
        logger.info("Starting callback server on port 5000...")
        self.client.start_callback_server()
        
        # Check bridge status
        if self.client.is_ready():
            logger.info("✅ WhatsApp Bridge is ready!")
            logger.info("Bot is running! Send /start to test")
        else:
            logger.error("❌ WhatsApp Bridge is not ready!")
            return
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nBot stopped by user")


def main():
    """Main entry point"""
    try:
        bot = WhatsAppBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
