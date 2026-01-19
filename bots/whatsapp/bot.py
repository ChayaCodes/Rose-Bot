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


class BannedUser(Base):
    __tablename__ = 'banned_users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False)
    banned_at = Column(DateTime, default=datetime.utcnow)
    banned_by = Column(String(100))


class ChatConfig(Base):
    __tablename__ = 'chat_config'
    chat_id = Column(String(100), primary_key=True)
    delete_commands = Column(Boolean, default=False)  # Delete command messages after processing
    

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
        'error_occurred': '❌ אירעה שגיאה. נסה שוב מאוחר יותר.',
        
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
        
        # Info
        'bot_info': '''ℹ️ *מידע על הבוט*

*שם:* Rose Bot (WhatsApp)
*גרסה:* 2.0 Full
*פלטפורמה:* WhatsApp
*סטטוס:* פועל ✅

*תכונות:*
✅ אזהרות וחסימות
✅ חוקים וקבלת פנים
✅ סינון מילים
✅ נעילת לינקים/מדיה
✅ מודרציית AI 🤖
✅ אנטי-ספאם

*המזהה שלך:* {from_id}
*מזהה צ'אט:* {chat_id}''',
        
        # Usage messages
        'usage_setrules': '❌ שימוש: /setrules <טקסט חוקים>',
        'usage_setwarn': '❌ שימוש: /setwarn <מספר>\n\nדוגמה: /setwarn 3',
        'usage_setwelcome': '❌ שימוש: /setwelcome <הודעה>\n\nתוכל להשתמש ב-{mention} לתיוג משתמשים חדשים',
        'usage_addblacklist': '❌ שימוש: /addblacklist <מילה>',
        'usage_rmblacklist': '❌ שימוש: /rmblacklist <מילה>',
        'usage_lock': '❌ שימוש: /lock <סוג>\n\nסוגים זמינים: links, stickers, media',
        'usage_unlock': '❌ שימוש: /unlock <סוג>\n\nסוגים זמינים: links, stickers, media',
        'usage_aimod': '❌ שימוש: /aimod on|off\n\nדוגמה: /aimod on',
        'usage_aimodset': '''❌ שימוש: /aimodset <קטגוריה> <סף>

*קטגוריות:*
• toxicity - תוכן פוגעני
• spam - ספאם
• sexual - תוכן מיני
• threat - איומים

*סף:* 0-100 (גבוה יותר = מחמיר יותר)
דוגמה: /aimodset spam 70''',
        'warn_limit_set': '✅ מגבלת אזהרות הוגדרה ל-{limit}',
        'locked': '🔒 {lock_type} ננעל',
        'unlocked': '🔓 {lock_type} נפתח',
        
        # Blacklist & moderation
        'blacklist_detected': '⚠️ ההודעה נמחקה: מכילה מילה אסורה',
        'lock_triggered': '🔒 {lock_type} ננעל בקבוצה זו',
        
        # Warns
        'warn_usage': '⚠️ *אזהרת משתמש*\n\nהשב להודעה של משתמש עם /warn [סיבה]',
        'no_warns': '✅ אין אזהרות',
        'warns_list': '⚠️ *אזהרות: {count}/{limit}*\n\n',
        'no_reason': 'ללא סיבה',
        'resetwarns_usage': '❌ השב להודעה של משתמש כדי לאפס אזהרות',
        'warns_reset_success': '✅ האזהרות אופסו',
        
        # Kick/Ban/Unban/Add
        'kick_usage': '👢 *בעיטת משתמש*\n\nהשב להודעה של משתמש עם /kick\n\n_הערה: הבוט צריך הרשאות מנהל_',
        'ban_usage': '🚫 *חסימת משתמש*\n\nהשב להודעה של משתמש עם /ban\n\n_הערה: הבוט צריך הרשאות מנהל_',
        'unban_usage': '✅ *ביטול חסימה*\n\nשימוש: /unban <מספר טלפון>\n\nדוגמה: /unban 972501234567',
        'user_unbanned': '✅ {user} הוסר מרשימת החסומים',
        'user_not_banned': 'ℹ️ המשתמש לא נמצא ברשימת החסומים',
        'add_usage': '➕ *הוספת משתמש לקבוצה*\n\nשימוש: /add <מספר טלפון>\n\nדוגמה: /add 972501234567\nאו: /add 972501234567,972509876543',
        'user_added': '✅ {user} נוסף לקבוצה',
        'user_add_failed': '❌ לא הצלחתי להוסיף את {user}\n\nסיבות אפשריות:\n• המשתמש חסם את הבוט\n• הגדרות פרטיות של המשתמש\n• הבוט לא מנהל',
        'users_added': '✅ {count} משתמשים נוספו לקבוצה',
        'invite_link': '🔗 *לינק הזמנה לקבוצה:*\n\n{link}',
        'invite_failed': '❌ לא הצלחתי ליצור לינק הזמנה',
        'invalid_phone': '❌ מספר טלפון לא תקין: {phone}\n\nפורמט נכון: 972501234567 (ללא +, -, רווחים)',
        
        # Delete Commands
        'delete_commands_on': '✅ מחיקת פקודות הופעלה\n\nמעכשיו פקודות שנשלחות לבוט יימחקו אוטומטית',
        'delete_commands_off': '❌ מחיקת פקודות כובתה\n\nפקודות יישארו בצ\'אט',
        'delete_commands_status': '🗑️ *מחיקת פקודות:* {status}',
        
        # Welcome
        'welcome_current': '👋 *הודעת קבלת פנים נוכחית:*\n\n{message}',
        'welcome_not_set_admin': 'ℹ️ לא הוגדרה הודעת קבלת פנים.\n\nמנהלים יכולים להגדיר עם /setwelcome',
        
        # Blacklist
        'blacklist_list': '🚫 *מילים ברשימה שחורה ({count}):*\n\n',
        'blacklist_empty_admin': 'ℹ️ אין מילים ברשימה השחורה.\n\nמנהלים יכולים להוסיף עם /addblacklist',
        
        # Locks
        'locks_status': '🔒 *נעילות נוכחיות:*\n\n',
        'links_label': 'לינקים',
        'stickers_label': 'מדבקות',
        'media_label': 'מדיה',
        'lock_locked': '🔒 נעול',
        'lock_unlocked': '🔓 פתוח',
        
        # AI Moderation
        'aimod_on': '''✅ *AI Moderation הופעל!*

הבוט יזהה אוטומטית:
🤖 תוכן טוקסי/פוגעני
🚫 ספאם
🔞 תוכן מיני
⚠️ איומים

*פקודות שימושיות:*
• /aimodstatus - בדיקת הגדרות
• /aihelp - מדריך מלא

💡 שלח /aihelp למידע נוסף''',
        'aimod_off': '❌ AI Moderation כבוי',
        'aimod_status_disabled': '❌ AI Moderation *כבוי*\n\nשלח /aimod on להפעלה',
        'aimod_status_header': '🤖 *סטטוס AI Moderation*\n\n',
        'status_enabled': '✅ פעיל',
        'status_disabled': '❌ כבוי',
        'api_key_set': '✅ מוגדר',
        'api_key_not_set': '❌ לא מוגדר (משתמש בגלובלי)',
        'thresholds_label': '*ספים:*',
        'auto_delete_label': 'מחיקה אוטומטית',
        'auto_warn_label': 'אזהרה אוטומטית',
        'category_invalid': '❌ קטגוריה לא חוקית. בחר מתוך: {categories}',
        'threshold_set': '✅ סף {category} הוגדר ל-{threshold}%',
        
        # Help for specific commands
        'help_cmd_not_found': '❓ פקודה לא נמצאה: /{cmd}\n\nשלח /help לרשימת פקודות',
        'help_cmd_header': '📖 *עזרה ל-/{cmd}*\n\n',
        'help_cmd_usage': '*שימוש:* {usage}\n',
        'help_cmd_desc': '*תיאור:* {desc}\n',
        'help_cmd_example': '*דוגמה:* {example}',
        'help_cmd_admin': '\n\n_🔐 פקודה זו דורשת הרשאות מנהל_',
        'help_use_cmd': '\n\n💡 שלח `/help <פקודה>` למידע מפורט על פקודה',
        
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
        'error_occurred': '❌ An error occurred. Please try again later.',
        
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
        
        # Info
        'bot_info': '''ℹ️ *Bot Information*

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
*Chat ID:* {chat_id}''',
        
        # Usage messages
        'usage_setrules': '❌ Usage: /setrules <rules text>',
        'usage_setwarn': '❌ Usage: /setwarn <number>\n\nExample: /setwarn 3',
        'usage_setwelcome': '❌ Usage: /setwelcome <message>\n\nYou can use {mention} to mention new users',
        'usage_addblacklist': '❌ Usage: /addblacklist <word>',
        'usage_rmblacklist': '❌ Usage: /rmblacklist <word>',
        'usage_lock': '❌ Usage: /lock <type>\n\nValid types: links, stickers, media',
        'usage_unlock': '❌ Usage: /unlock <type>\n\nValid types: links, stickers, media',
        'usage_aimod': '❌ Usage: /aimod [on|off]\n\n‼️ בלי פרמטר: מציג סטטוס נוכחי\nExample: /aimod on',
        'usage_aimodset': '''❌ Usage: /aimodset <category> <threshold>

*Categories:*
• toxicity - Toxic/hateful content
• spam - Spam messages
• sexual - Sexual content
• threat - Threatening messages

*Threshold:* 0-100 (higher = more strict)
Example: /aimodset spam 70''',
        'warn_limit_set': '✅ Warn limit set to {limit}',
        'locked': '🔒 {lock_type} locked',
        'unlocked': '🔓 {lock_type} unlocked',
        
        # Blacklist & moderation
        'blacklist_detected': '⚠️ Message deleted: contains blacklisted word',
        'lock_triggered': '🔒 {lock_type} is locked in this group',
        
        # Warns
        'warn_usage': '⚠️ *Warn User*\n\nReply to a user\'s message with /warn [reason]',
        'no_warns': '✅ No warnings',
        'warns_list': '⚠️ *Warnings: {count}/{limit}*\n\n',
        'no_reason': 'No reason',
        'resetwarns_usage': '❌ Reply to a user\'s message to reset warnings',
        'warns_reset_success': '✅ Warnings reset',
        
        # Kick/Ban/Unban/Add
        'kick_usage': '👢 *Kick User*\n\nReply to a user\'s message with /kick\n\n_Note: Bot needs admin rights_',
        'ban_usage': '🚫 *Ban User*\n\nReply to a user\'s message with /ban\n\n_Note: Bot needs admin rights_',
        'unban_usage': '✅ *Unban User*\n\nUsage: /unban <phone number>\n\nExample: /unban 972501234567',
        'user_unbanned': '✅ {user} removed from ban list',
        'user_not_banned': 'ℹ️ User not found in ban list',
        'add_usage': '➕ *Add User to Group*\n\nUsage: /add <phone number>\n\nExample: /add 972501234567\nOr: /add 972501234567,972509876543',
        'user_added': '✅ {user} added to group',
        'user_add_failed': '❌ Failed to add {user}\n\nPossible reasons:\n• User blocked the bot\n• User privacy settings\n• Bot is not admin',
        'users_added': '✅ {count} users added to group',
        'invite_link': '🔗 *Group Invite Link:*\n\n{link}',
        'invite_failed': '❌ Failed to generate invite link',
        'invalid_phone': '❌ Invalid phone number: {phone}\n\nCorrect format: 972501234567 (no +, -, spaces)',
        
        # Delete Commands
        'delete_commands_on': '✅ Command deletion enabled\n\nCommands sent to the bot will now be automatically deleted',
        'delete_commands_off': '❌ Command deletion disabled\n\nCommands will remain in chat',
        'delete_commands_status': '🗑️ *Command Deletion:* {status}',
        
        # Welcome
        'welcome_current': '👋 *Current Welcome Message:*\n\n{message}',
        'welcome_not_set_admin': 'ℹ️ No welcome message set.\n\nAdmins can set one with /setwelcome',
        
        # Blacklist
        'blacklist_list': '🚫 *Blacklisted Words ({count}):*\n\n',
        'blacklist_empty_admin': 'ℹ️ No blacklisted words in this chat.\n\nAdmins can add with /addblacklist',
        
        # Locks
        'locks_status': '🔒 *Current Locks:*\n\n',
        'links_label': 'Links',
        'stickers_label': 'Stickers',
        'media_label': 'Media',
        'lock_locked': '🔒 Locked',
        'lock_unlocked': '🔓 Unlocked',
        
        # AI Moderation
        'aimod_on': '''✅ *AI Moderation Enabled!*

The bot will automatically detect:
🤖 Toxic/offensive content
🚫 Spam
🔞 Sexual content
⚠️ Threats

*Useful commands:*
• /aimodstatus - Check settings
• /aihelp - Full guide

💡 Send /aihelp for more info''',
        'aimod_off': '❌ AI Moderation disabled',
        'aimod_status_disabled': '❌ AI Moderation is *disabled*\n\nUse /aimod on to enable',
        'aimod_status_header': '🤖 *AI Moderation Status*\n\n',
        'status_enabled': '✅ Enabled',
        'status_disabled': '❌ Disabled',
        'api_key_set': '✅ Set',
        'api_key_not_set': '❌ Not set (using global)',
        'thresholds_label': '*Thresholds:*',
        'auto_delete_label': 'Auto-delete',
        'auto_warn_label': 'Auto-warn',
        'category_invalid': '❌ Invalid category. Choose from: {categories}',
        'threshold_set': '✅ {category} threshold set to {threshold}%',
        
        # Help for specific commands
        'help_cmd_not_found': '❓ Command not found: /{cmd}\n\nSend /help for available commands',
        'help_cmd_header': '📖 *Help for /{cmd}*\n\n',
        'help_cmd_usage': '*Usage:* {usage}\n',
        'help_cmd_desc': '*Description:* {desc}\n',
        'help_cmd_example': '*Example:* {example}',
        'help_cmd_admin': '\n\n_🔐 This command requires admin permissions_',
        'help_use_cmd': '\n\n💡 Send `/help <command>` for detailed info about a command',
        
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

# Command help dictionary for /help <cmd>
COMMAND_HELP = {
    'he': {
        'start': {'usage': '/start', 'desc': 'התחל את הבוט וקבל הודעת פתיחה', 'example': '/start', 'admin': False},
        'help': {'usage': '/help [פקודה]', 'desc': 'הצג רשימת פקודות או מידע על פקודה ספציפית', 'example': '/help warn', 'admin': False},
        'info': {'usage': '/info', 'desc': 'הצג מידע על הבוט', 'example': '/info', 'admin': False},
        'ping': {'usage': '/ping', 'desc': 'בדוק אם הבוט פועל', 'example': '/ping', 'admin': False},
        'rules': {'usage': '/rules', 'desc': 'הצג את חוקי הקבוצה', 'example': '/rules', 'admin': False},
        'setrules': {'usage': '/setrules <טקסט>', 'desc': 'הגדר חוקים לקבוצה', 'example': '/setrules 1. היו נחמדים\\n2. אין ספאם', 'admin': True},
        'clearrules': {'usage': '/clearrules', 'desc': 'מחק את חוקי הקבוצה', 'example': '/clearrules', 'admin': True},
        'warn': {'usage': '/warn [סיבה]', 'desc': 'תן אזהרה למשתמש (השב להודעה)', 'example': '/warn ספאם', 'admin': True},
        'warns': {'usage': '/warns', 'desc': 'בדוק כמה אזהרות למשתמש (השב להודעה)', 'example': '/warns', 'admin': False},
        'resetwarns': {'usage': '/resetwarns', 'desc': 'אפס אזהרות למשתמש (השב להודעה)', 'example': '/resetwarns', 'admin': True},
        'setwarn': {'usage': '/setwarn <מספר>', 'desc': 'הגדר מגבלת אזהרות', 'example': '/setwarn 3', 'admin': True},
        'kick': {'usage': '/kick', 'desc': 'בעט משתמש מהקבוצה (השב להודעה)', 'example': '/kick', 'admin': True},
        'ban': {'usage': '/ban', 'desc': 'חסום משתמש מהקבוצה (השב להודעה)', 'example': '/ban', 'admin': True},
        'unban': {'usage': '/unban <טלפון>', 'desc': 'בטל חסימה של משתמש', 'example': '/unban 972501234567', 'admin': True},
        'add': {'usage': '/add <טלפון>', 'desc': 'הוסף משתמש לקבוצה', 'example': '/add 972501234567', 'admin': True},
        'invite': {'usage': '/invite', 'desc': 'קבל לינק הזמנה לקבוצה', 'example': '/invite', 'admin': True},
        'delcmds': {'usage': '/delcmds <on|off|status>', 'desc': 'הפעל/כבה מחיקת פקודות', 'example': '/delcmds on', 'admin': True},
        'welcome': {'usage': '/welcome', 'desc': 'הצג הודעת קבלת פנים נוכחית', 'example': '/welcome', 'admin': False},
        'setwelcome': {'usage': '/setwelcome <הודעה>', 'desc': 'הגדר הודעת קבלת פנים. השתמש ב-{mention} לתיוג', 'example': '/setwelcome ברוך הבא {mention}!', 'admin': True},
        'blacklist': {'usage': '/blacklist', 'desc': 'הצג רשימת מילים חסומות', 'example': '/blacklist', 'admin': False},
        'addblacklist': {'usage': '/addblacklist <מילה>', 'desc': 'הוסף מילה לרשימה השחורה', 'example': '/addblacklist ספאם', 'admin': True},
        'rmblacklist': {'usage': '/rmblacklist <מילה>', 'desc': 'הסר מילה מהרשימה השחורה', 'example': '/rmblacklist ספאם', 'admin': True},
        'lock': {'usage': '/lock <סוג>', 'desc': 'נעל סוג תוכן (links/stickers/media)', 'example': '/lock links', 'admin': True},
        'unlock': {'usage': '/unlock <סוג>', 'desc': 'בטל נעילה', 'example': '/unlock links', 'admin': True},
        'locks': {'usage': '/locks', 'desc': 'הצג נעילות פעילות', 'example': '/locks', 'admin': False},
        'lang': {'usage': '/lang [he|en]', 'desc': 'הצג או שנה שפה', 'example': '/lang he', 'admin': True},
        'setlang': {'usage': '/setlang <he|en>', 'desc': 'שנה שפת הבוט', 'example': '/setlang en', 'admin': True},
        'aimod': {'usage': '/aimod [on|off]', 'desc': 'הפעל/כבה מודרציית AI או הצג סטטוס', 'example': '/aimod on', 'admin': True},
        'aimodstatus': {'usage': '/aimodstatus', 'desc': 'בדוק הגדרות AI', 'example': '/aimodstatus', 'admin': False},
        'aimodset': {'usage': '/aimodset <קטגוריה> <סף>', 'desc': 'כוונן רגישות AI (0-100)', 'example': '/aimodset toxicity 70', 'admin': True},
        'aimodbackend': {'usage': '/aimodbackend <backend>', 'desc': 'החלף מנוע AI', 'example': '/aimodbackend perspective', 'admin': True},
        'aimodkey': {'usage': '/aimodkey <backend> <key>', 'desc': 'הגדר API key למנוע', 'example': '/aimodkey perspective YOUR_KEY', 'admin': True},
        'aihelp': {'usage': '/aihelp', 'desc': 'מדריך מפורט ל-AI Moderation', 'example': '/aihelp', 'admin': False},
        'aitest': {'usage': '/aitest <טקסט או ציטוט>', 'desc': 'בדוק הודעה עם AI והצג ציונים', 'example': '/aitest (השב להודעה)', 'admin': True},
    },
    'en': {
        'start': {'usage': '/start', 'desc': 'Start the bot and get welcome message', 'example': '/start', 'admin': False},
        'help': {'usage': '/help [command]', 'desc': 'Show command list or info about specific command', 'example': '/help warn', 'admin': False},
        'info': {'usage': '/info', 'desc': 'Show bot information', 'example': '/info', 'admin': False},
        'ping': {'usage': '/ping', 'desc': 'Check if bot is running', 'example': '/ping', 'admin': False},
        'rules': {'usage': '/rules', 'desc': 'Show group rules', 'example': '/rules', 'admin': False},
        'setrules': {'usage': '/setrules <text>', 'desc': 'Set group rules', 'example': '/setrules 1. Be nice\\n2. No spam', 'admin': True},
        'clearrules': {'usage': '/clearrules', 'desc': 'Clear group rules', 'example': '/clearrules', 'admin': True},
        'warn': {'usage': '/warn [reason]', 'desc': 'Warn a user (reply to message)', 'example': '/warn spam', 'admin': True},
        'warns': {'usage': '/warns', 'desc': 'Check user warnings (reply to message)', 'example': '/warns', 'admin': False},
        'resetwarns': {'usage': '/resetwarns', 'desc': 'Reset user warnings (reply to message)', 'example': '/resetwarns', 'admin': True},
        'setwarn': {'usage': '/setwarn <number>', 'desc': 'Set warn limit', 'example': '/setwarn 3', 'admin': True},
        'kick': {'usage': '/kick', 'desc': 'Kick user from group (reply to message)', 'example': '/kick', 'admin': True},
        'ban': {'usage': '/ban', 'desc': 'Ban user from group (reply to message)', 'example': '/ban', 'admin': True},
        'unban': {'usage': '/unban <phone>', 'desc': 'Unban a user', 'example': '/unban 972501234567', 'admin': True},
        'add': {'usage': '/add <phone>', 'desc': 'Add user to group', 'example': '/add 972501234567', 'admin': True},
        'invite': {'usage': '/invite', 'desc': 'Get group invite link', 'example': '/invite', 'admin': True},
        'delcmds': {'usage': '/delcmds <on|off|status>', 'desc': 'Enable/disable command deletion', 'example': '/delcmds on', 'admin': True},
        'welcome': {'usage': '/welcome', 'desc': 'Show current welcome message', 'example': '/welcome', 'admin': False},
        'setwelcome': {'usage': '/setwelcome <message>', 'desc': 'Set welcome message. Use {mention} to tag', 'example': '/setwelcome Welcome {mention}!', 'admin': True},
        'blacklist': {'usage': '/blacklist', 'desc': 'Show blacklisted words', 'example': '/blacklist', 'admin': False},
        'addblacklist': {'usage': '/addblacklist <word>', 'desc': 'Add word to blacklist', 'example': '/addblacklist spam', 'admin': True},
        'rmblacklist': {'usage': '/rmblacklist <word>', 'desc': 'Remove word from blacklist', 'example': '/rmblacklist spam', 'admin': True},
        'lock': {'usage': '/lock <type>', 'desc': 'Lock content type (links/stickers/media)', 'example': '/lock links', 'admin': True},
        'unlock': {'usage': '/unlock <type>', 'desc': 'Unlock content', 'example': '/unlock links', 'admin': True},
        'locks': {'usage': '/locks', 'desc': 'Show active locks', 'example': '/locks', 'admin': False},
        'lang': {'usage': '/lang [he|en]', 'desc': 'Show or change language', 'example': '/lang he', 'admin': True},
        'setlang': {'usage': '/setlang <he|en>', 'desc': 'Change bot language', 'example': '/setlang en', 'admin': True},
        'aimod': {'usage': '/aimod [on|off]', 'desc': 'Enable/disable AI moderation or show status', 'example': '/aimod on', 'admin': True},
        'aimodstatus': {'usage': '/aimodstatus', 'desc': 'Check AI settings', 'example': '/aimodstatus', 'admin': False},
        'aimodset': {'usage': '/aimodset <category> <threshold>', 'desc': 'Adjust AI sensitivity (0-100)', 'example': '/aimodset toxicity 70', 'admin': True},
        'aimodbackend': {'usage': '/aimodbackend <backend>', 'desc': 'Change AI engine', 'example': '/aimodbackend perspective', 'admin': True},
        'aimodkey': {'usage': '/aimodkey <backend> <key>', 'desc': 'Set API key for engine', 'example': '/aimodkey perspective YOUR_KEY', 'admin': True},
        'aihelp': {'usage': '/aihelp', 'desc': 'Detailed AI Moderation guide', 'example': '/aihelp', 'admin': False},
        'aitest': {'usage': '/aitest <text or reply>', 'desc': 'Test message with AI and show scores', 'example': '/aitest (reply to message)', 'admin': True},
    }
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


# ============ BAN SYSTEM ============

def add_ban(chat_id: str, user_id: str, banned_by: str = None):
    """Add user to ban list"""
    existing = db_session.query(BannedUser).filter_by(
        chat_id=chat_id, user_id=user_id
    ).first()
    if not existing:
        ban = BannedUser(chat_id=chat_id, user_id=user_id, banned_by=banned_by)
        db_session.add(ban)
        db_session.commit()


def remove_ban(chat_id: str, user_id: str) -> bool:
    """Remove user from ban list, returns True if found and removed"""
    result = db_session.query(BannedUser).filter_by(
        chat_id=chat_id, user_id=user_id
    ).delete()
    db_session.commit()
    return result > 0


def is_banned(chat_id: str, user_id: str) -> bool:
    """Check if user is banned in chat"""
    return db_session.query(BannedUser).filter_by(
        chat_id=chat_id, user_id=user_id
    ).first() is not None


def get_banned_users(chat_id: str) -> list:
    """Get all banned users in chat"""
    return db_session.query(BannedUser).filter_by(chat_id=chat_id).all()


# ============ CHAT CONFIG SYSTEM ============

def should_delete_commands(chat_id: str) -> bool:
    """Check if commands should be deleted in this chat"""
    config = db_session.query(ChatConfig).filter_by(chat_id=chat_id).first()
    return config.delete_commands if config else False


def set_delete_commands(chat_id: str, enabled: bool):
    """Set whether to delete commands in this chat"""
    config = db_session.query(ChatConfig).filter_by(chat_id=chat_id).first()
    if config:
        config.delete_commands = enabled
    else:
        config = ChatConfig(chat_id=chat_id, delete_commands=enabled)
        db_session.add(config)
    db_session.commit()


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
                    lang = get_chat_lang(chat_id)
                    if lang == 'he':
                        msg = f"🤖 *מודרציית AI*\n\n"
                        msg += f"❌ הודעה סומנה: {ai_result.reason}\n"
                        msg += f"ביטחון: {ai_result.confidence:.1%}\n\n"
                        if settings.auto_delete:
                            msg += "_ההודעה תימחק_"
                    else:
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
        
        # Add warning and get count
        reason = reason or get_text(chat_id, 'no_reason')
        count, limit_reached = warn_user(target_user, chat_id, reason, warner_id)
        
        # Get warn settings
        limit, soft = get_warn_settings(chat_id)
        
        # Format user display (just the number part)
        user_display = target_user.split('@')[0]
        
        # Check if user reached limit
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
        
        warns = get_warns(target_user, chat_id)
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
        reset_warns(quoted_participant, chat_id)
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
        if not args:
            # Show current status (like /aimodstatus)
            self.cmd_aimodstatus(chat_id)
            return
        
        if args.lower() not in ['on', 'off']:
            self.client.send_message(chat_id, get_text(chat_id, 'usage_aimod'))
            return
        
        enabled = args.lower() == 'on'
        set_ai_moderation(chat_id, enabled)
        
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
            test_text = quoted_msg
        elif args:
            test_text = args
        else:
            msg = "❌ *שימוש:* /aitest\n\nהשב להודעה או כתוב טקסט:\n/aitest בדוק את הטקסט הזה"
            self.client.send_message(chat_id, msg)
            return
        
        # Get AI settings
        settings = get_ai_settings(chat_id)
        
        # Check with AI
        from bot_core.content_filter import ContentModerationService
        moderator = ContentModerationService(
            backend=settings.backend,
            api_key=settings.api_key
        )
        
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
        msg += f"Backend: {backend_emoji.get(settings.backend, '❓')} {settings.backend}\n\n"
        msg += f"📝 *Text:* {test_text[:100]}{'...' if len(test_text) > 100 else ''}\n\n"
        msg += f"*Scores:*\n"
        
        if result.scores:
            for category, score in sorted(result.scores.items()):
                percentage = score * 100
                threshold = thresholds.get(category, 0.7) * 100
                emoji = '🔴' if score >= thresholds.get(category, 0.7) else '🟢'
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
