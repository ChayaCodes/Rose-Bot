"""
Internationalization (i18n) System
Multi-language support for the bot
"""

from typing import Dict

# Language names
LANG_NAMES = {
    'he': 'עברית',
    'en': 'English'
}

# Translations dictionary
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


def get_text(lang_code: str, key: str, **kwargs) -> str:
    """
    Get translated text for a language
    
    Args:
        lang_code: Language code (he, en, etc.)
        key: Translation key
        **kwargs: Format parameters
    
    Returns:
        Translated and formatted text
    """
    text = TRANSLATIONS.get(lang_code, {}).get(key, TRANSLATIONS['en'].get(key, key))
    return text.format(**kwargs) if kwargs else text
