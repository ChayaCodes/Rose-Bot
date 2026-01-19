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
from bot_core.db_models import Base, Warn, WarnSettings, Ban, Rules, Welcome, BlacklistWord, Lock, ChatLanguage, AIModeration
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

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

# Database setup
Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=engine))


# ============ DATABASE MODELS ============

class Warn(Base):
    __tablename__ = 'warns'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    chat_id = Column(String(100), nullable=False)
    reason = Column(Text)
    warned_by = Column(String(100))
    date = Column(DateTime, default=datetime.utcnow)


class WarnSettings(Base):
    __tablename__ = 'warn_settings'
    chat_id = Column(String(100), primary_key=True)
    warn_limit = Column(Integer, default=3)
    soft_warn = Column(Boolean, default=False)  # True=kick, False=ban


class Rules(Base):
    __tablename__ = 'rules'
    chat_id = Column(String(100), primary_key=True)
    rules = Column(Text)


class Welcome(Base):
    __tablename__ = 'welcome'
    chat_id = Column(String(100), primary_key=True)
    message = Column(Text)
    enabled = Column(Boolean, default=True)


class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(100), nullable=False)
    word = Column(String(255), nullable=False)


class Locks(Base):
    __tablename__ = 'locks'
    chat_id = Column(String(100), primary_key=True)
    lock_links = Column(Boolean, default=False)
    lock_stickers = Column(Boolean, default=False)
    lock_media = Column(Boolean, default=False)


class FloodControl(Base):
    __tablename__ = 'flood_control'
    chat_id = Column(String(100), primary_key=True)
    limit = Column(Integer, default=5)  # messages
    timeframe = Column(Integer, default=10)  # seconds


class AIModerationSettings(Base):
    __tablename__ = 'ai_moderation'
    chat_id = Column(String(100), primary_key=True)
    enabled = Column(Boolean, default=False)
    backend = Column(String(20), default='rules')  # perspective, azure, openai, detoxify, rules
    api_key = Column(String(255), nullable=True)  # Group's own API key
    toxicity_threshold = Column(Integer, default=70)  # 0-100
    spam_threshold = Column(Integer, default=70)
    sexual_threshold = Column(Integer, default=70)
    threat_threshold = Column(Integer, default=60)
    auto_delete = Column(Boolean, default=True)
    auto_warn = Column(Boolean, default=False)


class Language(Base):
    __tablename__ = 'language'
    chat_id = Column(String(100), primary_key=True)
    lang_code = Column(String(10), default='he')  # he, en, etc.
    

# Create tables
Base.metadata.create_all(engine)


# ============ TRANSLATIONS ============

TRANSLATIONS = {
    'he': {
        # General
        'start_msg': '''👋 *שלום! אני Rose Bot לווטסאפ*

אני עוזר לנהל קבוצות WhatsApp עם:
• אזהרות וניהול
• חוקים והודעות קבלת פנים
• רשימה שחורה למילים
• נעילות אנטי-ספאם
• ועוד הרבה!

שלח /help כדי לראות את כל הפקודות.''',
        'help_general': '📚 *פקודות זמינות*\n\n*כללי:*',
        'help_rules': '*חוקים:*',
        'help_warns': '*אזהרות:*',
        'help_moderation': '*ניהול:*',
        'help_welcome': '*קבלת פנים:*',
        'help_blacklist': '*רשימה שחורה:*',
        'help_locks': '*נעילות:*',
        'help_ai': '*AI Moderation:*',
        'help_note': '_הערה: פקודות מנהל דורשות הרשאות מנהל קבוצה_',
        'admin_only': '❌ פקודה זו זמינה רק למנהלי קבוצה',
        'owner_only': '❌ פקודה זו זמינה רק לבעלים של הבוט',
        'reply_to_user': '❌ השב להודעה של משתמש כדי להשתמש בפקודה זו',
        'unknown_command': '❓ פקודה לא מוכרת: /{command}\n\nשלח /help לרשימת פקודות',
        
        # Rules
        'rules_show': '📜 *חוקי הקבוצה:*\n\n{rules}',
        'rules_not_set': 'ℹ️ לא הוגדרו חוקים לקבוצה זו.\n\nמנהלים יכולים להגדיר חוקים עם /setrules',
        'rules_set': '✅ החוקים עודכנו!',
        'rules_cleared': '✅ החוקים נמחקו',
        
        # Warns
        'warn_issued': '⚠️ {user} קיבל אזהרה!\n*סיבה:* {reason}\n*אזהרות:* {count}/{limit}',
        'warn_limit_reached': '🚫 {user} הגיע למגבלת האזהרות!',
        'warn_reason_default': 'ללא סיבה',
        'warns_count': '⚠️ {user} יש לו {count} אזהרות מתוך {limit}',
        'warns_none': 'ℹ️ אין אזהרות ל-{user}',
        'warns_reset': '✅ האזהרות של {user} אופסו',
        'warn_limit_set': '✅ מגבלת האזהרות הוגדרה ל-{limit}',
        'warn_limit_invalid': '❌ מספר לא תקין. שימוש: /setwarn <מספר>\nלדוגמה: /setwarn 5',
        
        # Moderation
        'user_kicked': '👢 {user} נבעט מהקבוצה',
        'user_banned': '🚫 {user} נחסם מהקבוצה',
        'kick_failed': '❌ לא הצלחתי לבעוט את המשתמש',
        'ban_failed': '❌ לא הצלחתי לחסום את המשתמש',
        
        # Welcome
        'welcome_set': '✅ הודעת קבלת הפנים עודכנה!\nתשתמש ב-{mention} כדי לתייג משתמשים חדשים',
        'welcome_show': '👋 *הודעת קבלת פנים נוכחית:*\n\n{message}',
        'welcome_not_set': 'ℹ️ לא הוגדרה הודעת קבלת פנים\n\nמנהלים יכולים להגדיר עם /setwelcome',
        
        # Blacklist
        'blacklist_show': '🚫 *מילים חסומות:*\n{words}',
        'blacklist_empty': 'ℹ️ אין מילים חסומות בקבוצה זו',
        'blacklist_added': '✅ המילה "{word}" נוספה לרשימה השחורה',
        'blacklist_removed': '✅ המילה "{word}" הוסרה מהרשימה השחורה',
        'blacklist_not_found': '❌ המילה לא נמצאה ברשימה השחורה',
        'blacklist_detected': '🚫 הודעה מכילה מילה חסומה ונמחקה',
        
        # Locks
        'lock_enabled': '🔒 {lock_type} ננעל',
        'lock_disabled': '🔓 {lock_type} נפתח',
        'locks_show': '🔐 *נעילות נוכחיות:*\n\n{locks}',
        'locks_none': 'ℹ️ אין נעילות פעילות',
        'lock_invalid': '❌ סוג נעילה לא חוקי. זמין: links, stickers, media',
        'lock_triggered': '🔒 {lock_type} ננעל בקבוצה זו',
        
        # AI Moderation
        'aimod_enabled': '''✅ *AI Moderation הופעל!*

הבוט יזהה אוטומטית:
🤖 תוכן טוקסי/פוגעני
🚫 ספאם
🔞 תוכן מיני
⚠️ איומים

📋 *Backend נוכחי:* Rule-based (ללא צורך ב-API key)

*פקודות שימושיות:*
• /aimodstatus - בדיקת הגדרות
• /aimodset - כוונון רגישות
• /aimodbackend - החלפת מנוע AI
• /aimodkey - הגדרת API key

💡 *טיפ:* Backend ה-rules עובד מצוין לעברית ללא עלות!
לשיפור נוסף, תוכל להוסיף API key של Perspective או Azure.

📚 למידע נוסף: AI_MODERATION_SETUP.md''',
        'aimod_disabled': '❌ AI Moderation כבוי',
        'aimod_threshold_invalid': '❌ הסף חייב להיות מספר בין 0-100',
        
        # Language
        'lang_changed': '✅ השפה שונתה ל-{lang}!\n🌍 כל ההודעות יהיו עכשיו ב{lang_name}',
        'lang_current': 'ℹ️ השפה הנוכחית: {lang_name}\n\nזמין: עברית (he), English (en)',
        'lang_invalid': '❌ קוד שפה לא חוקי. זמין: he, en',
        
        # Ping
        'pong': '🏓 פונג!',
        
        # Usage messages
        'usage_setrules': '❌ שימוש: /setrules <טקסט חוקים>',
        'usage_setwarn': '❌ שימוש: /setwarn <מספר>\n\nדוגמה: /setwarn 3',
        'usage_setwelcome': '❌ שימוש: /setwelcome <הודעה>\n\nתוכל להשתמש ב-{mention} לתיוג משתמשים חדשים',
        'usage_addblacklist': '❌ שימוש: /addblacklist <מילה>',
        'usage_rmblacklist': '❌ שימוש: /rmblacklist <מילה>',
        'usage_lock': '❌ שימוש: /lock <סוג>\n\nסוגים זמינים: links, stickers, media',
        'usage_unlock': '❌ שימוש: /unlock <סוג>\n\nסוגים זמינים: links, stickers, media',
        'warn_limit_set': '✅ מגבלת אזהרות הוגדרה ל-{limit}',
        'locked': '🔒 {lock_type} ננעל',
        'unlocked': '🔓 {lock_type} נפתח',
        
        # AI Help
        'aihelp_full': '''🤖 *מדריך AI Moderation*

📝 *פקודות זמינות:*
• /aimod on|​off - הפעל/כבה (מנהל)
• /aimodstatus - בדוק הגדרות
• /aimodbackend <backend> - החלף מנוע (מנהל)
• /aimodkey <backend> <key> - הגדר API key (מנהל)
• /aimodset <קטגוריה> <מספר> - כוונן רגישות (מנהל)

🔧 *מנועות זמינים:*

📋 *rules* (ברירת מחדל)
   • שפות: עברית + אנגלית
   • עלות: חינם
   • API Key: לא נדרש

🌍 *perspective* (מומלץ לעברית!)
   • שפות: עברית + אנגלית
   • עלות: חינם (1 QPS)
   • קבל API Key: https://perspectiveapi.com
   • הגדרה: /aimodkey perspective <key>

☁️ *azure* (מדויק מאוד)
   • שפות: עברית + אנגלית
   • עלות: חינם עד 5,000/חודש
   • קבל API Key: Azure Portal
   • הגדרה: /aimodkey azure <key>

🤖 *openai*
   • שפות: אנגלית (בעיקר)
   • עלות: חינם (free tier)
   • קבל API Key: platform.openai.com
   • הגדרה: /aimodkey openai <key>

💻 *detoxify*
   • שפות: אנגלית
   • עלות: חינם (מקומי)
   • API Key: לא נדרש
   • דרישה: pip install detoxify

🎯 *קטגוריות לכיוון:*
• toxicity - תוכן פוגעני
• spam - ספאם
• sexual - תוכן מיני
• threat - איומים

💡 דוגמה: /aimodset toxicity 70''',
    },
    'en': {
        # General
        'start_msg': '''👋 *Hello! I'm Rose Bot for WhatsApp*

I help manage WhatsApp groups with:
• Warnings and moderation
• Rules and welcome messages
• Word blacklist
• Anti-spam locks
• And much more!

Send /help to see all commands.''',
        'help_general': '📚 *Available Commands*\n\n*General:*',
        'help_rules': '*Rules:*',
        'help_warns': '*Warns:*',
        'help_moderation': '*Moderation:*',
        'help_welcome': '*Welcome:*',
        'help_blacklist': '*Blacklist:*',
        'help_locks': '*Locks:*',
        'help_ai': '*AI Moderation:*',
        'help_note': '_Note: Admin commands require group admin rights_',
        'admin_only': '❌ This command is only available to group admins',
        'owner_only': '❌ This command is only available to bot owner',
        'reply_to_user': '❌ Reply to a user message to use this command',
        'unknown_command': '❓ Unknown command: /{command}\n\nSend /help for available commands',
        
        # Rules
        'rules_show': '📜 *Group Rules:*\n\n{rules}',
        'rules_not_set': 'ℹ️ No rules set for this group.\n\nAdmins can set rules with /setrules',
        'rules_set': '✅ Rules updated!',
        'rules_cleared': '✅ Rules cleared',
        
        # Warns
        'warn_issued': '⚠️ {user} has been warned!\n*Reason:* {reason}\n*Warns:* {count}/{limit}',
        'warn_limit_reached': '🚫 {user} reached the warn limit!',
        'warn_reason_default': 'No reason provided',
        'warns_count': '⚠️ {user} has {count} warns out of {limit}',
        'warns_none': 'ℹ️ {user} has no warns',
        'warns_reset': '✅ {user} warns have been reset',
        'warn_limit_set': '✅ Warn limit set to {limit}',
        'warn_limit_invalid': '❌ Invalid number. Usage: /setwarn <number>\nExample: /setwarn 5',
        
        # Moderation
        'user_kicked': '👢 {user} has been kicked',
        'user_banned': '🚫 {user} has been banned',
        'kick_failed': '❌ Failed to kick user',
        'ban_failed': '❌ Failed to ban user',
        
        # Welcome
        'welcome_set': '✅ Welcome message updated!\nUse {mention} to tag new users',
        'welcome_show': '👋 *Current welcome message:*\n\n{message}',
        'welcome_not_set': 'ℹ️ No welcome message set\n\nAdmins can set one with /setwelcome',
        
        # Blacklist
        'blacklist_show': '🚫 *Blacklisted words:*\n{words}',
        'blacklist_empty': 'ℹ️ No blacklisted words in this group',
        'blacklist_added': '✅ "{word}" added to blacklist',
        'blacklist_removed': '✅ "{word}" removed from blacklist',
        'blacklist_not_found': '❌ Word not found in blacklist',
        'blacklist_detected': '🚫 Message contains blacklisted word and was deleted',
        
        # Locks
        'lock_enabled': '🔒 {lock_type} locked',
        'lock_disabled': '🔓 {lock_type} unlocked',
        'locks_show': '🔐 *Current locks:*\n\n{locks}',
        'locks_none': 'ℹ️ No active locks',
        'lock_invalid': '❌ Invalid lock type. Available: links, stickers, media',
        'lock_triggered': '🔒 {lock_type} is locked in this group',
        
        # AI Moderation
        'aimod_enabled': '''✅ *AI Moderation Enabled!*

The bot will automatically detect:
🤖 Toxic/offensive content
🚫 Spam
🔞 Sexual content
⚠️ Threats

📋 *Current Backend:* Rule-based (no API key needed)

*Useful commands:*
• /aimodstatus - Check settings
• /aimodset - Adjust sensitivity
• /aimodbackend - Change AI engine
• /aimodkey - Set API key

💡 *Tip:* The rules backend works great for Hebrew at no cost!
For better results, add a Perspective or Azure API key.

📚 More info: AI_MODERATION_SETUP.md''',
        'aimod_disabled': '❌ AI Moderation disabled',
        'aimod_threshold_invalid': '❌ Threshold must be a number between 0-100',
        
        # Language
        'lang_changed': '✅ Language changed to {lang}!\n🌍 All messages will now be in {lang_name}',
        'lang_current': 'ℹ️ Current language: {lang_name}\n\nAvailable: עברית (he), English (en)',
        'lang_invalid': '❌ Invalid language code. Available: he, en',
        
        # Ping
        'pong': '🏓 Pong!',
        
        # Usage messages
        'usage_setrules': '❌ Usage: /setrules <rules text>',
        'usage_setwarn': '❌ Usage: /setwarn <number>\n\nExample: /setwarn 3',
        'usage_setwelcome': '❌ Usage: /setwelcome <message>\n\nYou can use {mention} to mention new users',
        'usage_addblacklist': '❌ Usage: /addblacklist <word>',
        'usage_rmblacklist': '❌ Usage: /rmblacklist <word>',
        'usage_lock': '❌ Usage: /lock <type>\n\nValid types: links, stickers, media',
        'usage_unlock': '❌ Usage: /unlock <type>\n\nValid types: links, stickers, media',
        'warn_limit_set': '✅ Warn limit set to {limit}',
        'locked': '🔒 {lock_type} locked',
        'unlocked': '🔓 {lock_type} unlocked',
        
        # AI Help
        'aihelp_full': '''🤖 *AI Moderation Guide*

📝 *Available Commands:*
• /aimod on|​off - Enable/disable (admin)
• /aimodstatus - Check settings
• /aimodbackend <backend> - Change engine (admin)
• /aimodkey <backend> <key> - Set API key (admin)
• /aimodset <category> <num> - Adjust sensitivity (admin)

🔧 *Available Backends:*

📋 *rules* (default)
   • Languages: Hebrew + English
   • Cost: Free
   • API Key: Not required

🌍 *perspective* (recommended for Hebrew!)
   • Languages: Hebrew + English
   • Cost: Free (1 QPS)
   • Get API Key: https://perspectiveapi.com
   • Setup: /aimodkey perspective <key>

☁️ *azure* (very accurate)
   • Languages: Hebrew + English
   • Cost: Free up to 5,000/month
   • Get API Key: Azure Portal
   • Setup: /aimodkey azure <key>

🤖 *openai*
   • Languages: English (mainly)
   • Cost: Free (free tier)
   • Get API Key: platform.openai.com
   • Setup: /aimodkey openai <key>

💻 *detoxify*
   • Languages: English
   • Cost: Free (local)
   • API Key: Not required
   • Requires: pip install detoxify

🎯 *Categories to adjust:*
• toxicity - Offensive content
• spam - Spam messages
• sexual - Adult content
• threat - Threats

💡 Example: /aimodset toxicity 70''',
    }
}

LANG_NAMES = {
    'he': 'עברית',
    'en': 'English'
}


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

def get_warn_settings(chat_id: str) -> tuple:
    """Get warn limit and action for chat"""
    settings = db_session.query(WarnSettings).filter_by(chat_id=chat_id).first()
    if not settings:
        settings = WarnSettings(chat_id=chat_id)
        db_session.add(settings)
        db_session.commit()
    return settings.warn_limit, settings.soft_warn


def set_warn_limit(chat_id: str, limit: int):
    """Set warn limit for chat"""
    settings = db_session.query(WarnSettings).filter_by(chat_id=chat_id).first()
    if not settings:
        settings = WarnSettings(chat_id=chat_id, warn_limit=limit)
        db_session.add(settings)
    else:
        settings.warn_limit = limit
    db_session.commit()


def warn_user(user_id: str, chat_id: str, reason: str, warner_id: str) -> tuple:
    """Add a warn to user, returns (warn_count, limit_reached)"""
    # Add warn
    warn = Warn(user_id=user_id, chat_id=chat_id, reason=reason, warned_by=warner_id)
    db_session.add(warn)
    db_session.commit()
    
    # Count warns
    count = db_session.query(Warn).filter_by(user_id=user_id, chat_id=chat_id).count()
    limit, _ = get_warn_settings(chat_id)
    
    return count, count >= limit


def get_warns(user_id: str, chat_id: str) -> List[Warn]:
    """Get all warns for user in chat"""
    return db_session.query(Warn).filter_by(user_id=user_id, chat_id=chat_id).all()


def reset_warns(user_id: str, chat_id: str):
    """Reset all warns for user in chat"""
    db_session.query(Warn).filter_by(user_id=user_id, chat_id=chat_id).delete()
    db_session.commit()


# ============ RULES SYSTEM ============

def set_rules(chat_id: str, rules_text: str):
    """Set rules for chat"""
    rules = db_session.query(Rules).filter_by(chat_id=chat_id).first()
    if not rules:
        rules = Rules(chat_id=chat_id, rules=rules_text)
        db_session.add(rules)
    else:
        rules.rules = rules_text
    db_session.commit()


def get_rules(chat_id: str) -> Optional[str]:
    """Get rules for chat"""
    rules = db_session.query(Rules).filter_by(chat_id=chat_id).first()
    return rules.rules if rules else None


# ============ WELCOME SYSTEM ============

def set_welcome(chat_id: str, message: str):
    """Set welcome message for chat"""
    welcome = db_session.query(Welcome).filter_by(chat_id=chat_id).first()
    if not welcome:
        welcome = Welcome(chat_id=chat_id, message=message)
        db_session.add(welcome)
    else:
        welcome.message = message
    db_session.commit()


def get_welcome(chat_id: str) -> Optional[str]:
    """Get welcome message for chat"""
    welcome = db_session.query(Welcome).filter_by(chat_id=chat_id).first()
    return welcome.message if welcome and welcome.enabled else None


# ============ LANGUAGE SYSTEM ============

def get_chat_lang(chat_id: str) -> str:
    """Get language for chat (default: he)"""
    lang = db_session.query(Language).filter_by(chat_id=chat_id).first()
    return lang.lang_code if lang else 'he'


def set_chat_lang(chat_id: str, lang_code: str):
    """Set language for chat"""
    lang = db_session.query(Language).filter_by(chat_id=chat_id).first()
    if not lang:
        lang = Language(chat_id=chat_id, lang_code=lang_code)
        db_session.add(lang)
    else:
        lang.lang_code = lang_code
    db_session.commit()


def get_text(chat_id: str, key: str, **kwargs) -> str:
    """Get translated text for chat"""
    lang = get_chat_lang(chat_id)
    text = TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS['en'].get(key, key))
    return text.format(**kwargs) if kwargs else text


# ============ BLACKLIST SYSTEM ============

def add_blacklist(chat_id: str, word: str):
    """Add word to blacklist"""
    existing = db_session.query(Blacklist).filter_by(
        chat_id=chat_id, word=word.lower()
    ).first()
    if not existing:
        blacklist = Blacklist(chat_id=chat_id, word=word.lower())
        db_session.add(blacklist)
        db_session.commit()


def remove_blacklist(chat_id: str, word: str):
    """Remove word from blacklist"""
    db_session.query(Blacklist).filter_by(
        chat_id=chat_id, word=word.lower()
    ).delete()
    db_session.commit()


def get_blacklist(chat_id: str) -> List[str]:
    """Get all blacklisted words for chat"""
    words = db_session.query(Blacklist).filter_by(chat_id=chat_id).all()
    return [w.word for w in words]


def check_blacklist(chat_id: str, text: str) -> Optional[str]:
    """Check if text contains blacklisted word"""
    words = get_blacklist(chat_id)
    text_lower = text.lower()
    for word in words:
        if word in text_lower:
            return word
    return None


# ============ LOCKS SYSTEM ============

def set_lock(chat_id: str, lock_type: str, enabled: bool):
    """Set lock for chat"""
    locks = db_session.query(Locks).filter_by(chat_id=chat_id).first()
    if not locks:
        locks = Locks(chat_id=chat_id)
        db_session.add(locks)
    
    if lock_type == 'links':
        locks.lock_links = enabled
    elif lock_type == 'stickers':
        locks.lock_stickers = enabled
    elif lock_type == 'media':
        locks.lock_media = enabled
    
    db_session.commit()


def get_locks(chat_id: str) -> Dict[str, bool]:
    """Get all locks for chat"""
    locks = db_session.query(Locks).filter_by(chat_id=chat_id).first()
    if not locks:
        return {'links': False, 'stickers': False, 'media': False}
    return {
        'links': locks.lock_links,
        'stickers': locks.lock_stickers,
        'media': locks.lock_media
    }


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

def get_ai_settings(chat_id: str) -> AIModerationSettings:
    """Get AI moderation settings for chat"""
    settings = db_session.query(AIModerationSettings).filter_by(chat_id=chat_id).first()
    if not settings:
        settings = AIModerationSettings(chat_id=chat_id, backend='rules')  # Default to rules backend
        db_session.add(settings)
        db_session.commit()
    # Ensure backend is never None
    if not settings.backend:
        settings.backend = 'rules'
        db_session.commit()
    return settings


def set_ai_moderation(chat_id: str, enabled: bool):
    """Enable/disable AI moderation"""
    settings = get_ai_settings(chat_id)
    settings.enabled = enabled
    db_session.commit()


def set_ai_threshold(chat_id: str, category: str, threshold: int):
    """Set threshold for AI moderation category"""
    settings = get_ai_settings(chat_id)
    if category == 'toxicity':
        settings.toxicity_threshold = threshold
    elif category == 'spam':
        settings.spam_threshold = threshold
    elif category == 'sexual':
        settings.sexual_threshold = threshold
    elif category == 'threat':
        settings.threat_threshold = threshold
    db_session.commit()


def set_ai_backend(chat_id: str, backend: str, api_key: Optional[str] = None):
    """Set AI backend and optional API key for group"""
    settings = get_ai_settings(chat_id)
    settings.backend = backend
    if api_key:
        settings.api_key = api_key
    db_session.commit()


def check_ai_moderation(chat_id: str, text: str, bot_moderator) -> Optional[ModerationResult]:
    """Check message with AI moderation using group's own settings"""
    settings = get_ai_settings(chat_id)
    
    if not settings.enabled:
        return None
    
    # Create moderator with group's backend and API key
    backend = settings.backend or 'rules'
    api_key = settings.api_key
    
    # Use group's API key, fallback to environment variable
    if not api_key:
        import os
        api_key = os.getenv(f'{backend.upper()}_API_KEY')
    
    # Create fresh moderator for this group (don't use cached one)
    from bot_core.content_filter import ContentModerator
    moderator = ContentModerator(backend=backend, api_key=api_key)
    
    # Build thresholds from settings (convert 0-100 to 0.0-1.0)
    thresholds = {
        'toxicity': settings.toxicity_threshold / 100.0,
        'spam': settings.spam_threshold / 100.0,
        'sexual': settings.sexual_threshold / 100.0,
        'threat': settings.threat_threshold / 100.0,
    }
    
    result = moderator.check_message(text, thresholds)
    return result if result.is_flagged else None


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
                    settings = get_ai_settings(chat_id)
                    msg = f"🤖 *AI Moderation*\n\n"
                    msg += f"❌ Message flagged: {ai_result.reason}\n"
                    msg += f"Confidence: {ai_result.confidence:.1%}\n\n"
                    
                    if settings.auto_delete:
                        msg += "_Message will be deleted_"
                    
                    self.client.send_message(chat_id, msg)
                    
                    if settings.auto_warn:
                        # TODO: Auto-warn user
                        pass
                    
                    # TODO: Delete message via bridge
                    return
                
                blacklisted = check_blacklist(chat_id, text)
                if blacklisted:
                    self.client.send_message(
                        chat_id,
                        f"⚠️ Message deleted: contains blacklisted word '{blacklisted}'"
                    )
                    # TODO: Delete message via bridge
                    return
                
                # Check locks
                lock_violation = check_locks(chat_id, message)
                if lock_violation:
                    self.client.send_message(chat_id, f"🔒 {lock_violation}")
                    # TODO: Delete message via bridge
                    return
            
            # Handle commands
            if text.startswith('/'):
                self.handle_command(text, from_id, chat_id, is_group, message)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    def handle_command(self, text: str, from_id: str, chat_id: str, is_group: bool, message: dict):
        """Handle bot commands"""
        parts = text.split(maxsplit=1)
        command = parts[0][1:].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # ===== GENERAL COMMANDS =====
        
        if command == 'start':
            self.cmd_start(chat_id)
        
        elif command == 'help':
            self.cmd_help(chat_id, is_owner(from_id))
        
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
        
        elif command == 'aihelp':
            self.cmd_aihelp(chat_id)
        
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
    
    def cmd_help(self, chat_id: str, is_owner: bool):
        """Help command"""
        lang = get_chat_lang(chat_id)
        msg = get_text(chat_id, 'help_general')
        msg += '''\n/start - Start the bot
/help - Show this message
/info - Bot information
/ping - Check bot status
/setlang <code> - Set language (he/en)\n\n'''
        
        msg += get_text(chat_id, 'help_rules')
        msg += '''\n/rules - Show group rules
/setrules <text> - Set group rules (admin)\n\n'''
        
        msg += get_text(chat_id, 'help_warns')
        msg += '''\n/warn - Warn a user (reply to message)
/warns - Check user warns
/resetwarns - Reset warns (reply to message)
/setwarn <number> - Set warn limit (admin)\n\n'''
        
        msg += get_text(chat_id, 'help_moderation')
        msg += '''\n/kick - Kick user (reply to message)
/ban - Ban user (reply to message)\n\n'''
        
        msg += get_text(chat_id, 'help_welcome')
        msg += '''\n/setwelcome <text> - Set welcome message (admin)
/welcome - Show current welcome\n\n'''
        
        msg += get_text(chat_id, 'help_blacklist')
        msg += '''\n/blacklist - Show blacklisted words
/addblacklist <word> - Add word to blacklist (admin)
/rmblacklist <word> - Remove from blacklist (admin)\n\n'''
        
        msg += get_text(chat_id, 'help_locks')
        msg += '''\n/lock <type> - Lock links/stickers/media (admin)
/unlock <type> - Unlock (admin)
/locks - Show current locks\n\n'''

        # Language section
        if lang == 'he':
            msg += '''🌍 *שפה:*
/lang - הצג שפה נוכחית
/lang he|en - שנה שפה (מנהל)\n\n'''
        else:
            msg += '''🌍 *Language:*
/lang - Show current language
/lang he|en - Change language (admin)\n\n'''
        
        msg += get_text(chat_id, 'help_ai')
        msg += '''
/aimod on|off - Enable/disable AI moderation (admin)
/aimodstatus - Check AI settings
/aihelp - Detailed AI moderation guide

'''
        
        msg += get_text(chat_id, 'help_note')
        self.client.send_message(chat_id, msg)
    
    def cmd_info(self, chat_id: str, from_id: str):
        """Info command"""
        msg = f"""ℹ️ *Bot Information*

*Name:* Rose Bot (WhatsApp)
*Version:* 2.0 Full
*Platform:* WhatsApp
*Status:* Running ✅

*Features:*
✅ Warns & Bans
✅ Rules & Welcome
✅ Blacklist Filter
✅ Link/Media Locks
✅ AI Moderation 🤖
✅ Anti-spam

*Your ID:* {from_id}
*Chat ID:* {chat_id}"""
        self.client.send_message(chat_id, msg)
    
    def cmd_rules(self, chat_id: str):
        """Show rules"""
        rules = get_rules(chat_id)
        if rules:
            msg = f"📜 *Group Rules:*\n\n{rules}"
        else:
            msg = "ℹ️ No rules set for this group.\n\nAdmins can set rules with /setrules"
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
        # TODO: Extract user from reply
        # For now, show usage
        self.client.send_message(
            chat_id,
            "⚠️ *Warn User*\n\nReply to a user's message with /warn [reason]"
        )
    
    def cmd_warns(self, chat_id: str, user_id: str, message: dict):
        """Check warns"""
        # TODO: Extract user from reply or check self
        warns = get_warns(user_id, chat_id)
        limit, soft = get_warn_settings(chat_id)
        
        if not warns:
            msg = f"✅ No warnings"
        else:
            msg = f"⚠️ *Warnings: {len(warns)}/{limit}*\n\n"
            for i, warn in enumerate(warns, 1):
                msg += f"{i}. {warn.reason or 'No reason'}\n"
        
        self.client.send_message(chat_id, msg)
    
    def cmd_resetwarns(self, chat_id: str, message: dict):
        """Reset warns"""
        # TODO: Extract user from reply
        self.client.send_message(
            chat_id,
            "Reply to a user's message with /resetwarns to reset their warnings"
        )
    
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
        self.client.send_message(
            chat_id,
            "👢 *Kick User*\n\nReply to a user's message with /kick\n\n_Note: Bot needs admin rights to kick users_"
        )
    
    def cmd_ban(self, chat_id: str, message: dict):
        """Ban user"""
        self.client.send_message(
            chat_id,
            "🚫 *Ban User*\n\nReply to a user's message with /ban\n\n_Note: Bot needs admin rights to ban users_"
        )
    
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
            msg = f"👋 *Current Welcome Message:*\n\n{welcome}"
        else:
            msg = "ℹ️ No welcome message set.\n\nAdmins can set one with /setwelcome"
        self.client.send_message(chat_id, msg)
    
    def cmd_blacklist(self, chat_id: str):
        """Show blacklist"""
        words = get_blacklist(chat_id)
        if words:
            msg = f"🚫 *Blacklisted Words ({len(words)}):*\n\n" + "\n".join(f"• {w}" for w in words)
        else:
            msg = "ℹ️ No blacklisted words in this chat.\n\nAdmins can add words with /addblacklist"
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
        msg = "🔒 *Current Locks:*\n\n"
        msg += f"Links: {'🔒 Locked' if locks['links'] else '🔓 Unlocked'}\n"
        msg += f"Stickers: {'🔒 Locked' if locks['stickers'] else '🔓 Unlocked'}\n"
        msg += f"Media: {'🔒 Locked' if locks['media'] else '🔓 Unlocked'}"
        self.client.send_message(chat_id, msg)
    
    def cmd_aimod(self, chat_id: str, args: str):
        """Enable/disable AI moderation"""
        if not args or args.lower() not in ['on', 'off']:
            self.client.send_message(
                chat_id,
                "❌ Usage: /aimod on|off\n\nExample: /aimod on"
            )
            return
        
        enabled = args.lower() == 'on'
        set_ai_moderation(chat_id, enabled)
        
        if enabled:
            msg = """✅ *AI Moderation Enabled!*

הבוט יזהה אוטומטית:
🤖 תוכן טוקסי/פוגעני
🚫 ספאם
🔞 תוכן מיני
⚠️ איומים

📋 *Backend נוכחי:* Rule-based (ללא צורך ב-API key)

*פקודות שימושיות:*
• /aimodstatus - בדיקת הגדרות
• /aimodset - כוונון רגישות
• /aimodbackend - החלפת מנוע AI
• /aimodkey - הגדרת API key

💡 *טיפ:* Backend ה-rules עובד מצוין לעברית ללא עלות!
לשיפור נוסף, תוכל להוסיף API key של Perspective או Azure.

📚 למידע נוסף: AI_MODERATION_SETUP.md"""
        else:
            msg = "❌ AI Moderation disabled"
        
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
    
    def cmd_aimodstatus(self, chat_id: str):
        """Show AI moderation status"""
        settings = get_ai_settings(chat_id)
        
        if not settings.enabled:
            msg = "❌ AI Moderation is *disabled*\n\nUse /aimod on to enable"
        else:
            backend_emoji = {
                'perspective': '🌍',
                'openai': '🤖',
                'azure': '☁️',
                'detoxify': '💻',
                'rules': '📋'
            }
            backend_name = {
                'perspective': 'Google Perspective (Hebrew+English)',
                'openai': 'OpenAI (English)',
                'azure': 'Azure (Hebrew+English)',
                'detoxify': 'Detoxify (English)',
                'rules': 'Rule-based (Hebrew+English)'
            }
            
            msg = "🤖 *AI Moderation Status*\n\n"
            msg += f"Status: {'✅ Enabled' if settings.enabled else '❌ Disabled'}\n"
            msg += f"Backend: {backend_emoji.get(settings.backend, '❓')} {backend_name.get(settings.backend, settings.backend)}\n"
            msg += f"API Key: {'✅ Set' if settings.api_key else '❌ Not set (using global)'}\n\n"
            msg += "*Thresholds:*\n"
            msg += f"• Toxicity: {settings.toxicity_threshold}%\n"
            msg += f"• Spam: {settings.spam_threshold}%\n"
            msg += f"• Sexual: {settings.sexual_threshold}%\n"
            msg += f"• Threat: {settings.threat_threshold}%\n\n"
            msg += f"Auto-delete: {'✅' if settings.auto_delete else '❌'}\n"
            msg += f"Auto-warn: {'✅' if settings.auto_warn else '❌'}"
        
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
                        f"⚠️ Warning: {backend} requires an API key.\n\n"
                        f"Set it with: /aimodkey {backend} YOUR_KEY\n\n"
                        f"Or set {backend.upper()}_API_KEY environment variable.\n\n"
                        f"Backend changed anyway, but it won't work without a key."
                    )
        
        set_ai_backend(chat_id, backend)
        self.client.send_message(
            chat_id,
            f"✅ Backend set to *{backend}*"
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
    
    def run(self):
        """Start the bot"""
        logger.info("Starting WhatsApp Bot...")
        logger.info(f"Owner: {Config.OWNER_ID}")
        
        # Register message handler
        self.client.on_message(self.handle_message)
        
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
