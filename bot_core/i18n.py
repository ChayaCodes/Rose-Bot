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
        'user_kicked': '👢 {user} הוצא מהקבוצה',
        'user_banned': '🚫 {user} נחסם מהקבוצה',
        'kick_failed': '❌ לא הצלחתי להוציא את המשתמש',
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
🤖 תוכן רעיל/פוגעני
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

# Command help dictionary for /help <cmd>
COMMAND_HELP = {
   'he': {
      'start': {'usage': '/start', 'desc': 'התחל את הבוט וקבל הודעת פתיחה', 'example': '/start', 'admin': False},
      'help': {'usage': '/help [פקודה]', 'desc': 'הצג רשימת פקודות או מידע על פקודה ספציפית', 'example': '/help warn', 'admin': False},
      'info': {'usage': '/info', 'desc': 'הצג מידע על הבוט', 'example': '/info', 'admin': False},
      'ping': {'usage': '/ping', 'desc': 'בדוק אם הבוט פועל', 'example': '/ping', 'admin': False},
      'rules': {'usage': '/rules', 'desc': 'הצג את חוקי הקבוצה', 'example': '/rules', 'admin': False},
      'setrules': {'usage': '/setrules <טקסט>', 'desc': 'הגדר חוקים לקבוצה', 'example': '/setrules 1. היו נחמדים\n2. אין ספאם', 'admin': True},
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
      'setrules': {'usage': '/setrules <text>', 'desc': 'Set group rules', 'example': '/setrules 1. Be nice\n2. No spam', 'admin': True},
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


def get_chat_text(chat_id: str, key: str, **kwargs) -> str:
    """
    Get translated text for a specific chat
    
    Args:
        chat_id: Chat identifier
        key: Translation key
        **kwargs: Format parameters
    
    Returns:
        Translated and formatted text
    """
    from .services.language_service import get_chat_language
    lang = get_chat_language(chat_id)
    return get_text(lang, key, **kwargs)
