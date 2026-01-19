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
      'help_general_user': '\n/start - הפעל את הבוט\n/help - הצג הודעה זו\n/info - מידע על הבוט\n/ping - בדוק סטטוס\n\n',
      'help_general_admin': '\n/start - הפעל את הבוט\n/help - הצג הודעה זו\n/info - מידע על הבוט\n/ping - בדוק סטטוס\n/setlang <he|en> - שנה שפה\n\n',
        'help_rules': '*חוקים:*',
      'help_rules_user': '\n/rules - הצג חוקי קבוצה\n\n',
      'help_rules_admin': '\n/rules - הצג חוקי קבוצה\n/setrules <טקסט> - הגדר חוקים (מנהל)\n\n',
        'help_warns': '*אזהרות:*',
      'help_warns_user': '\n/warns - בדוק אזהרות\n\n',
      'help_warns_admin': '\n/warns - בדוק אזהרות\n/warn - אזהרה למשתמש (השב להודעה)\n/resetwarns - אפס אזהרות (השב להודעה)\n/setwarn <מספר> - הגדר מגבלת אזהרות (מנהל)\n\n',
        'help_moderation': '*ניהול:*',
      'help_moderation_admin': '''\n/kick - בעט משתמש (השב להודעה)
   /ban - חסום משתמש (השב להודעה)
   /unban <טלפון> - בטל חסימה של משתמש
   /add <טלפון> - הוסף משתמש לקבוצה
   /invite - קבל קישור הזמנה לקבוצה
   /delcmds <on|off|status> - מחיקת פקודות\n\n''',
        'help_welcome': '*קבלת פנים:*',
      'help_welcome_user': '\n/welcome - הצג הודעה נוכחית\n\n',
      'help_welcome_admin': '\n/welcome - הצג הודעה נוכחית\n/setwelcome <טקסט> - הגדר הודעת קבלת פנים (מנהל)\n\n',
        'help_blacklist': '*רשימה שחורה:*',
      'help_blacklist_user': '\n/blacklist - הצג מילים חסומות\n\n',
      'help_blacklist_admin': '\n/blacklist - הצג מילים חסומות\n/addblacklist <מילה> - הוסף לרשימה (מנהל)\n/rmblacklist <מילה> - הסר מהרשימה (מנהל)\n\n',
        'help_locks': '*נעילות:*',
      'help_locks_user': '\n/locks - הצג נעילות נוכחיות\n\n',
      'help_locks_admin': '\n/locks - הצג נעילות נוכחיות\n/lock <סוג> - נעל links/stickers/media (מנהל)\n/unlock <סוג> - בטל נעילה (מנהל)\n\n',
        'help_ai': '*AI Moderation:*',
      'help_language_admin': '''🌍 *שפה:*
   /lang - הצג שפה נוכחית
   /lang he|en - שנה שפה (מנהל)\n\n''',
      'help_ai_user': '\n/aimodstatus - בדוק הגדרות AI\n/aihelp - מדריך מלא\n\n',
      'help_ai_admin': '\n/aimodstatus - בדוק הגדרות AI\n/aihelp - מדריך מלא\n/aimod on|off - הפעל/כבה מודרציית AI (מנהל)\n/aitest <טקסט> - בדיקת הודעה עם AI (או השב להודעה) (מנהל)\n\n',
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

💻 *Backend נוכחי:* Detoxify (ללא צורך ב-API key)

*פקודות שימושיות:*
• /aimodstatus - בדיקת הגדרות
• /aimodset - כוונון רגישות
• /aimodbackend - החלפת מנוע AI
• /aimodkey - הגדרת API key

💡 *טיפ:* Detoxify עובד מצוין לאנגלית ללא עלות.
לשיפור עברית, הוסף API key של Perspective או Azure.

📚 למידע נוסף: AI_MODERATION_SETUP.md''',
        'aimod_disabled': '❌ AI Moderation כבוי',
        'aimod_threshold_invalid': '❌ הסף חייב להיות מספר בין 0-100',
        
        # Language
        'lang_changed': '✅ השפה שונתה ל-{lang}!\n🌍 כל ההודעות יהיו עכשיו ב{lang_name}',
        'lang_current': 'ℹ️ השפה הנוכחית: {lang_name}\n\nזמין: עברית (he), English (en)',
        'lang_invalid': '❌ קוד שפה לא חוקי. זמין: he, en',
        
        # Ping
        'pong': '🏓 Pong!',
        
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
   • /aimodset <קטגוריה> <מספר> - כוונן רגישות לפי קטגוריה (מנהל)
   • /aimodthreshold <0-100> - רגישות כללית (מנהל)

   🎯 *איך מכוונים רגישות?*
   • /aimodthreshold קובע רגישות כללית לכל הקטגוריות
   • 0-40 = נמוכה (מסנן רק תוכן קיצוני)
   • 40-70 = בינונית (מומלץ)
   • 70-100 = גבוהה (עשוי לזהות גם תוכן תקין)

   דוגמאות:
   /aimodthreshold 60
   /aimodset sexual 80

   💡 טיפ: התחילו עם 60 והתאימו לפי הצורך.

   🔧 *מנועות זמינים:*

💻 *detoxify* (ברירת מחדל)
   • שפות: אנגלית
   • עלות: חינם (מקומי)
   • API Key: לא נדרש
   • דרישה: pip install detoxify

🌍 *perspective* (מומלץ לעברית!)
   • שפות: עברית + אנגלית
   • עלות: חינם (1 QPS)
   • קבל API Key: https://perspectiveapi.com
   • הגדרה: /aimodkey perspective <key>

☁️ *azure* (מדויק מאוד)
   • שפות: עברית + אנגלית
   • עלות: חינם עד 5,000/חודש
   • קבל API Key: Azure Portal
   • הגדרה: AZURE_ENDPOINT + /aimodkey azure <key>

🤖 *openai*
   • שפות: אנגלית (בעיקר)
   • עלות: חינם (free tier)
   • קבל API Key: platform.openai.com
   • הגדרה: /aimodkey openai <key>

🎯 *קטגוריות לכיוון:*
• toxicity - תוכן פוגעני
• spam - ספאם
• sexual - תוכן מיני
• threat - איומים

💡 דוגמה: /aimodset toxicity 70''',
        
        # Additional messages for hardcoded strings
        'ai_action_warn': '⚠️ אזהרה',
        'ai_action_delete': '🗑️ מחיקה',
        'ai_action_kick': '👋 הסרה',
        'ai_action_ban': '🚫 חסימה',
        'ai_moderation_header': '🤖 *מודרציית AI ({backend})*\n\n',
        'ai_toxic_detected': '❌ תוכן רעיל זוהה\n',
        'ai_score_label': 'ציון: {score:.1%}\n',
        'ai_actions_label': 'פעולות: {actions}',
        'toxic_content': 'תוכן רעיל',
        'no_reason': 'ללא סיבה',
        'error_occurred': '❌ אירעה שגיאה',
        'help_cmd_header': '*פקודה: /{cmd}*\n\n',
        'help_cmd_usage': '*שימוש:* {usage}\n',
        'help_cmd_desc': '*תיאור:* {desc}\n',
        'help_cmd_example': '*דוגמה:* {example}\n',
        'help_cmd_admin': '\n_📋 פקודת מנהל_',
        'help_cmd_not_found': '❌ פקודה לא נמצאה: {cmd}',
        'help_use_cmd': '\n\n💡 שימוש: /help <פקודה> למידע נוסף',
        'bot_info': '🤖 *Rose Bot*\n\nמזהה: {from_id}\nצ\'אט: {chat_id}',
        'warn_usage': '❌ השב להודעה של משתמש כדי להזהיר אותו',
        'warns_list': '⚠️ *אזהרות ({count}/{limit}):*\n',
        'resetwarns_usage': '❌ השב להודעה של משתמש כדי לאפס אזהרות',
        'kick_usage': '❌ השב להודעה של משתמש כדי להוציא אותו',
        'ban_usage': '❌ השב להודעה של משתמש כדי לחסום אותו',
        'unban_usage': '❌ שימוש: /unban <מספר טלפון>',
        'invalid_phone': '❌ מספר טלפון לא תקין: {phone}',
        'user_unbanned': '✅ {user} בוטלה חסימתו',
        'user_not_banned': 'ℹ️ המשתמש לא חסום',
        'add_usage': '❌ שימוש: /add <מספר טלפון>\nדוגמה: /add 972501234567',
        'user_added': '✅ {user} נוסף לקבוצה',
        'users_added': '✅ {count} משתמשים נוספו לקבוצה',
        'user_add_failed': '❌ נכשל בהוספת {user}',
        'invite_link': '🔗 *לינק הזמנה:*\n{link}',
        'invite_failed': '❌ נכשל בקבלת לינק הזמנה',
        'delete_commands_on': '✅ מחיקת פקודות הופעלה',
        'delete_commands_off': '❌ מחיקת פקודות כובתה',
        'delete_commands_status': 'ℹ️ מחיקת פקודות: {status}',
        'welcome_current': '👋 *הודעת קבלת פנים נוכחית:*\n\n{message}',
        'welcome_not_set_admin': 'ℹ️ לא הוגדרה הודעת קבלת פנים.\n\nהגדר עם /setwelcome',
        'blacklist_list': '🚫 *מילים חסומות ({count}):*\n',
        'blacklist_empty_admin': 'ℹ️ אין מילים חסומות.\n\nהוסף עם /addblacklist',
        'usage_lock': '❌ שימוש: /lock <links|stickers|media>',
        'locked': '🔒 {lock_type} ננעל',
        'usage_unlock': '❌ שימוש: /unlock <links|stickers|media>',
        'unlocked': '🔓 {lock_type} נפתח',
        'locks_status': '🔐 *נעילות נוכחיות:*\n',
        'lock_locked': '🔒 נעול',
        'lock_unlocked': '🔓 פתוח',
        'links_label': 'לינקים',
        'stickers_label': 'מדבקות',
        'media_label': 'מדיה',
        'usage_aimod': '❌ שימוש: /aimod <on|off>',
        'aimod_on': '✅ מודרציית AI הופעלה!',
        'aimod_off': '❌ מודרציית AI כובתה',
        'links_not_allowed': 'קישורים אינם מותרים בצ\'אט זה',
        
        # AI Test command
        'aitest_usage': '❌ *שימוש:* /aitest\n\nהשב להודעה או כתוב טקסט:\n/aitest בדוק את הטקסט הזה',
        'aitest_header': '🔍 *בדיקת AI Moderation*\n\n',
        'aitest_backend': 'Backend: {emoji} {backend}\n',
        'aitest_backend_used': 'Backend used: {emoji} {backend} (אין API key)\n',
        'aitest_backend_fallback': 'Backend used: {emoji} {backend} (fallback)\n',
        'aitest_text': '📝 *טקסט:* {text}\n\n',
        'aitest_scores': '*ציונים:*\n',
        'aitest_score_line': '{emoji} {category}: {percentage:.1f}% (סף: {threshold:.0f}%)\n',
        'aitest_result': '\n*תוצאה:* ',
        'aitest_flagged': '❌ *FLAGGED*\n',
        'aitest_passed': '✅ *PASSED*\n',
        'aitest_type': 'סוג: {type}\n',
        'aitest_confidence': 'ביטחון: {confidence:.1f}%\n',
        'aitest_reason': 'סיבה: {reason}',
        
        # AI Status command additions
      'aimod_status_disabled': '❌ מודרציית AI כבויה\n\nהשתמש ב-/aimod on כדי להפעיל',
        'aimod_status_header': '🤖 *סטטוס AI Moderation*\n\n',
        'aimod_status_enabled': 'סטטוס: ✅ מופעל\n',
        'aimod_status_backend': 'Backend: {emoji} {name}\n',
        'aimod_status_api_key': 'API Key: {status}\n',
        'aimod_status_threshold': 'סף: {threshold}%\n',
        'aimod_status_action': 'פעולה: {action}\n\n',
        'aimod_status_actions_header': '*פעולות זמינות:*\n',
        'aimod_status_action_warn': '• warn - אזהרה למשתמש\n',
        'aimod_status_action_delete': '• delete - מחיקת הודעה\n',
        'aimod_status_action_kick': '• kick - הסרה מהקבוצה\n',
        'aimod_status_action_ban': '• ban - חסימה והסרה\n\n',
        'aimod_status_commands': '*פקודות:*\n',
        'aimod_status_cmd_backend': '/aimodbackend <backend> - החלף מנוע\n',
        'aimod_status_cmd_threshold': '/aimodthreshold <0-100> - שנה רגישות\n',
        'aimod_status_cmd_action': '/aimodaction <action> - שנה פעולה',

        # AI Set thresholds
        'aimodset_usage': '''❌ Usage: /aimodset <category> <threshold>

*Categories:*
• toxicity - Toxic/hateful content
• spam - Spam messages
• sexual - Sexual content
• threat - Threatening messages

*Threshold:* 0-100 (higher = more strict)
Example: /aimodset spam 70''',
        'aimodset_invalid_category': '❌ קטגוריה לא תקינה. בחר מ: {categories}',
        'aimodset_threshold_set': '✅ סף {category} הוגדר ל-{threshold}%',

        # AI Test details
        'aitest_backend_used_missing_key': 'Backend used: {emoji} {backend} (אין API key)\n',
        'aitest_backend_used_fallback': 'Backend used: {emoji} {backend} (fallback)\n',
        'aitest_no_scores': '_אין ציונים זמינים_\n',

        # AI Status details
        'aimod_status_api_key_set': '✅ מוגדר',
        'aimod_status_api_key_not_set': '❌ לא מוגדר',

        # AI Key command
        'aimodkey_usage': '''❌ *שימוש:* /aimodkey <backend> <api_key>

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
   • איך להשיג:
     1) צור משאב “Content Safety” ב-Azure Portal
     2) העתק את ה-Key ואת ה-Endpoint
     3) הגדר AZURE_ENDPOINT כמשתנה סביבה
     4) השתמש ב-/aimodkey azure <KEY>
   • פורטל: https://portal.azure.com

🤖 *openai* (OpenAI Moderation)
   • תומך: אנגלית בלבד
   • API Key: דרוש חשבון OpenAI
   • איך להשיג: https://platform.openai.com

💻 *detoxify* (מודל מקומי)
   • תומך: אנגלית בלבד
   • ללא צורך ב-API key ✅
   • דורש התקנה: pip install detoxify

*דוגמאות שימוש:*
/aimodkey perspective AIzaSyA...
/aimodkey azure a1b2c3d4e5...

🔒 *אבטחה:* המפתח נשמר רק עבור הקבוצה הזו
💰 *עלות:* כל קבוצה יכולה להשתמש במפתח משלה

📚 *מדריך מלא:* AI_MODERATION_SETUP.md''',
        'aimodkey_invalid_backend': '❌ Backend לא תקין. בחר מ: {backends}',
        'aimodkey_backend_set_no_key': '✅ Backend הוגדר ל-*{backend}*\n\nאין צורך ב-API key עבור backend זה.',
        'aimodkey_key_saved': '✅ API key נשמר עבור *{backend}* backend!\n\n🔒 המפתח נשמר בצורה מאובטחת ומשמש רק לקבוצה זו.\n\nהשתמש ב-/aimod on להפעלה.',

        # AI Backend command
        'aimodbackend_usage': '''❌ *שימוש:* /aimodbackend <backend>

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

*דוגמה:*
/aimodbackend perspective

💡 *טיפ:* השתמש ב-/aimodkey להגדרת API key לפני.''',
        'aimodbackend_invalid_backend': '❌ Backend לא תקין. בחר מ: {backends}',
        'aimodbackend_missing_key': '❌ *{backend}* דורש API key!\n\n🔑 הגדר מפתח תחילה:\n/aimodkey {backend} YOUR_KEY\n\nאו הגדר משתנה סביבה:\n{env_var}\n\n⚠️ ה-backend לא שונה. תחילה הגדר API key.',
        'aimodbackend_set': '✅ Backend הוגדר ל-*{backend}*',

        # AI Action command
        'aimodaction_usage': '''❌ *שימוש:* /aimodaction <action>

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
/aimodaction delete_ban''',
        'aimodaction_invalid': '❌ פעולה לא תקינה: {action}\nבחר מ: {actions}',
        'aimodaction_set': '✅ פעולת AI moderation שונתה ל:\n{action}',

        # AI Threshold command
        'aimodthreshold_usage': '''❌ *שימוש:* /aimodthreshold <0-100>

🎯 *רגישות זיהוי תוכן רעיל*

הסף קובע כמה רגיש הבוט:
• 0-40: רגיש מעט (רק תוכן ממש רעיל)
• 40-70: רגישות בינונית ✅ (מומלץ)
• 70-100: רגיש מאוד (עלול לזהות גם תוכן תקין)

*דוגמאות:*
/aimodthreshold 60 - רגישות בינונית
/aimodthreshold 80 - רגיש מאוד

💡 *טיפ:* התחל עם 60 והתאם לפי הצורך''',
        'aimodthreshold_invalid': '❌ הסף חייב להיות מספר בין 0 ל-100',
        'sensitivity_low': 'נמוכה',
        'sensitivity_medium': 'בינונית',
        'sensitivity_high': 'גבוהה',
        'aimodthreshold_set': '✅ סף הזיהוי שונה ל-{threshold}%\nרגישות: {sensitivity}',
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
      'help_general_user': '\n/start - Start the bot\n/help - Show this message\n/info - Bot information\n/ping - Check bot status\n\n',
      'help_general_admin': '\n/start - Start the bot\n/help - Show this message\n/info - Bot information\n/ping - Check bot status\n/setlang <code> - Set language (he/en)\n\n',
        'help_rules': '*Rules:*',
      'help_rules_user': '\n/rules - Show group rules\n\n',
      'help_rules_admin': '\n/rules - Show group rules\n/setrules <text> - Set group rules (admin)\n\n',
        'help_warns': '*Warns:*',
      'help_warns_user': '\n/warns - Check user warns\n\n',
      'help_warns_admin': '\n/warns - Check user warns\n/warn - Warn a user (reply to message)\n/resetwarns - Reset warns (reply to message)\n/setwarn <number> - Set warn limit (admin)\n\n',
        'help_moderation': '*Moderation:*',
      'help_moderation_admin': '''\n/kick - Kick user (reply to message)
   /ban - Ban user (reply to message)
   /unban <phone> - Unban a user
   /add <phone> - Add user to group
   /invite - Get group invite link
   /delcmds <on|off|status> - Command deletion\n\n''',
        'help_welcome': '*Welcome:*',
      'help_welcome_user': '\n/welcome - Show current welcome\n\n',
      'help_welcome_admin': '\n/welcome - Show current welcome\n/setwelcome <text> - Set welcome message (admin)\n\n',
        'help_blacklist': '*Blacklist:*',
      'help_blacklist_user': '\n/blacklist - Show blacklisted words\n\n',
      'help_blacklist_admin': '\n/blacklist - Show blacklisted words\n/addblacklist <word> - Add word to blacklist (admin)\n/rmblacklist <word> - Remove from blacklist (admin)\n\n',
        'help_locks': '*Locks:*',
      'help_locks_user': '\n/locks - Show current locks\n\n',
      'help_locks_admin': '\n/locks - Show current locks\n/lock <type> - Lock links/stickers/media (admin)\n/unlock <type> - Unlock (admin)\n\n',
        'help_ai': '*AI Moderation:*',
      'help_language_admin': '''🌍 *Language:*
   /lang - Show current language
   /lang he|en - Change language (admin)\n\n''',
      'help_ai_user': '\n/aimodstatus - Check AI settings\n/aihelp - Detailed AI moderation guide\n\n',
      'help_ai_admin': '\n/aimodstatus - Check AI settings\n/aihelp - Detailed AI moderation guide\n/aimod on|off - Enable/disable AI moderation (admin)\n/aitest <text> - Test text with AI (or reply) (admin)\n\n',
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

📋 *Current Backend:* Detoxify (local, no API key needed)

*Useful commands:*
• /aimodstatus - Check settings
• /aimodset - Adjust sensitivity
• /aimodbackend - Change AI engine
• /aimodkey - Set API key

💡 *Tip:* Add a Perspective or Azure API key for better Hebrew accuracy.

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
   • /aimodset <category> <num> - Adjust sensitivity per category (admin)
   • /aimodthreshold <0-100> - Overall sensitivity (admin)

   🎯 *How to tune sensitivity:*
   • /aimodthreshold sets a general sensitivity for all categories
   • 0-40 = low (only very toxic content)
   • 40-70 = medium (recommended)
   • 70-100 = high (may flag normal content)

   Examples:
   /aimodthreshold 60
   /aimodset sexual 80

   💡 Tip: start with 60 and adjust as needed.

   🔧 *Available Backends:*

💻 *detoxify* (default)
   • Languages: English
   • Cost: Free (local)
   • API Key: Not required
   • Requires: pip install detoxify

🌍 *perspective* (recommended for Hebrew!)
   • Languages: Hebrew + English
   • Cost: Free (1 QPS)
   • Get API Key: https://perspectiveapi.com
   • Setup: /aimodkey perspective <key>

☁️ *azure* (very accurate)
   • Languages: Hebrew + English
   • Cost: Free up to 5,000/month
   • Get API Key: Azure Portal
   • Setup: AZURE_ENDPOINT + /aimodkey azure <key>

🤖 *openai*
   • Languages: English (mainly)
   • Cost: Free (free tier)
   • Get API Key: platform.openai.com
   • Setup: /aimodkey openai <key>

🎯 *Categories to adjust:*
• toxicity - Offensive content
• spam - Spam messages
• sexual - Adult content
• threat - Threats

💡 Example: /aimodset toxicity 70''',
        
        # Additional messages for hardcoded strings
        'ai_action_warn': '⚠️ Warn',
        'ai_action_delete': '🗑️ Delete',
        'ai_action_kick': '👋 Kick',
        'ai_action_ban': '🚫 Ban',
        'ai_moderation_header': '🤖 *AI Moderation ({backend})*\n\n',
        'ai_toxic_detected': '❌ Toxic content detected\n',
        'ai_score_label': 'Score: {score:.1%}\n',
        'ai_actions_label': 'Actions: {actions}',
        'toxic_content': 'Toxic content',
        'no_reason': 'No reason provided',
        'error_occurred': '❌ An error occurred',
        'help_cmd_header': '*Command: /{cmd}*\n\n',
        'help_cmd_usage': '*Usage:* {usage}\n',
        'help_cmd_desc': '*Description:* {desc}\n',
        'help_cmd_example': '*Example:* {example}\n',
        'help_cmd_admin': '\n_📋 Admin command_',
        'help_cmd_not_found': '❌ Command not found: {cmd}',
        'help_use_cmd': '\n\n💡 Use: /help <command> for more info',
        'bot_info': '🤖 *Rose Bot*\n\nID: {from_id}\nChat: {chat_id}',
        'warn_usage': '❌ Reply to a user message to warn them',
        'warns_list': '⚠️ *Warnings ({count}/{limit}):*\n',
        'resetwarns_usage': '❌ Reply to a user message to reset warns',
        'kick_usage': '❌ Reply to a user message to kick them',
        'ban_usage': '❌ Reply to a user message to ban them',
        'unban_usage': '❌ Usage: /unban <phone number>',
        'invalid_phone': '❌ Invalid phone number: {phone}',
        'user_unbanned': '✅ {user} has been unbanned',
        'user_not_banned': 'ℹ️ User is not banned',
        'add_usage': '❌ Usage: /add <phone number>\nExample: /add 972501234567',
        'user_added': '✅ {user} added to group',
        'users_added': '✅ {count} users added to group',
        'user_add_failed': '❌ Failed to add {user}',
        'invite_link': '🔗 *Invite Link:*\n{link}',
        'invite_failed': '❌ Failed to get invite link',
        'delete_commands_on': '✅ Command deletion enabled',
        'delete_commands_off': '❌ Command deletion disabled',
        'delete_commands_status': 'ℹ️ Command deletion: {status}',
        'welcome_current': '👋 *Current welcome message:*\n\n{message}',
        'welcome_not_set_admin': 'ℹ️ No welcome message set.\n\nSet one with /setwelcome',
        'blacklist_list': '🚫 *Blacklisted words ({count}):*\n',
        'blacklist_empty_admin': 'ℹ️ No blacklisted words.\n\nAdd with /addblacklist',
        'usage_lock': '❌ Usage: /lock <links|stickers|media>',
        'locked': '🔒 {lock_type} locked',
        'usage_unlock': '❌ Usage: /unlock <links|stickers|media>',
        'unlocked': '🔓 {lock_type} unlocked',
        'locks_status': '🔐 *Current locks:*\n',
        'lock_locked': '🔒 Locked',
        'lock_unlocked': '🔓 Unlocked',
        'links_label': 'Links',
        'stickers_label': 'Stickers',
        'media_label': 'Media',
        'usage_aimod': '❌ Usage: /aimod <on|off>',
        'aimod_on': '✅ AI moderation enabled!',
        'aimod_off': '❌ AI moderation disabled',
        'links_not_allowed': 'Links are not allowed in this chat',
        
        # AI Test command
        'aitest_usage': '❌ *Usage:* /aitest\n\nReply to a message or write text:\n/aitest check this text',
        'aitest_header': '🔍 *AI Moderation Test*\n\n',
        'aitest_backend': 'Backend: {emoji} {backend}\n',
        'aitest_backend_used': 'Backend used: {emoji} {backend} (no API key)\n',
        'aitest_backend_fallback': 'Backend used: {emoji} {backend} (fallback)\n',
        'aitest_text': '📝 *Text:* {text}\n\n',
        'aitest_scores': '*Scores:*\n',
        'aitest_score_line': '{emoji} {category}: {percentage:.1f}% (threshold: {threshold:.0f}%)\n',
        'aitest_result': '\n*Result:* ',
        'aitest_flagged': '❌ *FLAGGED*\n',
        'aitest_passed': '✅ *PASSED*\n',
        'aitest_type': 'Type: {type}\n',
        'aitest_confidence': 'Confidence: {confidence:.1f}%\n',
        'aitest_reason': 'Reason: {reason}',
        
        # AI Status command additions
        'aimod_status_disabled': '❌ AI Moderation is *disabled*\n\nUse /aimod on to enable',
        'aimod_status_header': '🤖 *AI Moderation Status*\n\n',
        'aimod_status_enabled': 'Status: ✅ Enabled\n',
        'aimod_status_backend': 'Backend: {emoji} {name}\n',
        'aimod_status_api_key': 'API Key: {status}\n',
        'aimod_status_threshold': 'Threshold: {threshold}%\n',
        'aimod_status_action': 'Action: {action}\n\n',
        'aimod_status_actions_header': '*Available actions:*\n',
        'aimod_status_action_warn': '• warn - warn user\n',
        'aimod_status_action_delete': '• delete - delete message\n',
        'aimod_status_action_kick': '• kick - remove from group\n',
        'aimod_status_action_ban': '• ban - ban and remove\n\n',
        'aimod_status_commands': '*Commands:*\n',
        'aimod_status_cmd_backend': '/aimodbackend <backend> - change engine\n',
        'aimod_status_cmd_threshold': '/aimodthreshold <0-100> - adjust sensitivity\n',
        'aimod_status_cmd_action': '/aimodaction <action> - change action',

        # AI Set thresholds
        'aimodset_usage': '''❌ Usage: /aimodset <category> <threshold>

*Categories:*
• toxicity - Toxic/hateful content
• spam - Spam messages
• sexual - Sexual content
• threat - Threatening messages

*Threshold:* 0-100 (higher = more strict)
Example: /aimodset spam 70''',
        'aimodset_invalid_category': '❌ Invalid category. Choose from: {categories}',
        'aimodset_threshold_set': '✅ {category} threshold set to {threshold}%',

        # AI Test details
        'aitest_backend_used_missing_key': 'Backend used: {emoji} {backend} (no API key)\n',
        'aitest_backend_used_fallback': 'Backend used: {emoji} {backend} (fallback)\n',
        'aitest_no_scores': '_No scores available_\n',

        # AI Status details
        'aimod_status_api_key_set': '✅ Set',
        'aimod_status_api_key_not_set': '❌ Not set',

        # AI Key command
        'aimodkey_usage': '''❌ *Usage:* /aimodkey <backend> <api_key>

🤖 *Available backends:*

🌍 *perspective* (Google Perspective API)
   • Supports: Hebrew + English
   • Recommended: ✅ Great for Hebrew!
   • API Key: Free up to 1M checks/month
   • Get it: https://perspectiveapi.com

☁️ *azure* (Azure Content Safety)
   • Supports: Hebrew + English + 100 languages
   • Recommended: ✅ Most accurate!
   • API Key: Free up to 5K checks/month
   • How to get it:
     1) Create a “Content Safety” resource in Azure Portal
     2) Copy the Key and the Endpoint
     3) Set AZURE_ENDPOINT as an environment variable
     4) Use /aimodkey azure <KEY>
   • Portal: https://portal.azure.com

🤖 *openai* (OpenAI Moderation)
   • Supports: English only
   • API Key: OpenAI account required
   • Get it: https://platform.openai.com

💻 *detoxify* (Local model)
   • Supports: English only
   • No API key needed ✅
   • Requires: pip install detoxify

*Examples:*
/aimodkey perspective AIzaSyA...
/aimodkey azure a1b2c3d4e5...

🔒 *Security:* Key is stored only for this group
💰 *Cost:* Each group can use its own key

📚 *Full guide:* AI_MODERATION_SETUP.md''',
        'aimodkey_invalid_backend': '❌ Invalid backend. Choose from: {backends}',
        'aimodkey_backend_set_no_key': '✅ Backend set to *{backend}*\n\nNo API key needed for this backend.',
        'aimodkey_key_saved': '✅ API key saved for *{backend}* backend!\n\n🔒 Your key is stored securely and used only for this group.\n\nUse /aimod on to enable AI moderation.',

        # AI Backend command
        'aimodbackend_usage': '''❌ *Usage:* /aimodbackend <backend>

🔄 *Switch AI engine* (without changing API key)

🤖 *Available backends:*

🌍 *perspective* - Google Perspective
   • Supports: Hebrew + English + 30 languages
   • Free (1M requests/day)
   • Most accurate for Hebrew ✅

☁️ *azure* - Azure Content Safety
   • Supports: Hebrew + English + 100 languages
   • Free up to 5K/month
   • Enterprise-grade ✅

🤖 *openai* - OpenAI Moderation
   • Supports: English only
   • Free
   • Very accurate

💻 *detoxify* - Local model
   • Supports: English only
   • Free, runs locally
   • No API key needed ✅

*Example:*
/aimodbackend perspective

💡 *Tip:* Use /aimodkey to set an API key first.''',
        'aimodbackend_invalid_backend': '❌ Invalid backend. Choose from: {backends}',
        'aimodbackend_missing_key': '❌ *{backend}* requires an API key!\n\n🔑 Set a key first:\n/aimodkey {backend} YOUR_KEY\n\nOr set env var:\n{env_var}\n\n⚠️ Backend not changed. Set API key first.',
        'aimodbackend_set': '✅ Backend set to *{backend}*',

        # AI Action command
        'aimodaction_usage': '''❌ *Usage:* /aimodaction <action>

⚡ *Available actions:*

⚠️ *warn* - warn only
   • Add warning to user
   • If max warns reached - kick/ban

🗑️ *delete* - delete only
   • Automatically delete toxic message

👋 *kick* - remove only
   • Remove user from group
   • Can rejoin via link

🚫 *ban* - ban and remove
   • Ban user and remove
   • Cannot rejoin

💡 *Combined actions:*

⚠️🗑️ *warn_delete* - warn + delete
   • Warn and delete the message

🗑️👋 *delete_kick* - delete + kick
   • Delete message and remove user

🗑️🚫 *delete_ban* - delete + ban
   • Delete message and ban permanently

*Examples:*
/aimodaction delete
/aimodaction warn_delete
/aimodaction delete_ban''',
        'aimodaction_invalid': '❌ Invalid action: {action}\nChoose from: {actions}',
        'aimodaction_set': '✅ AI moderation action changed to:\n{action}',

        # AI Threshold command
        'aimodthreshold_usage': '''❌ *Usage:* /aimodthreshold <0-100>

🎯 *Toxic content detection sensitivity*

The threshold determines sensitivity:
• 0-40: Low (only very toxic content)
• 40-70: Medium ✅ (recommended)
• 70-100: High (may flag normal content)

*Examples:*
/aimodthreshold 60 - medium sensitivity
/aimodthreshold 80 - high sensitivity

💡 *Tip:* Start with 60 and adjust as needed''',
        'aimodthreshold_invalid': '❌ Threshold must be a number between 0 and 100',
        'sensitivity_low': 'low',
        'sensitivity_medium': 'medium',
        'sensitivity_high': 'high',
        'aimodthreshold_set': '✅ Threshold set to {threshold}%\nSensitivity: {sensitivity}',
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
      'aitest': {'usage': '/aitest <טקסט> או השב להודעה', 'desc': 'בדוק הודעה עם AI והצג ציונים', 'example': '/aitest בדוק את הטקסט הזה', 'admin': True},
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
      'aitest': {'usage': '/aitest <text> or reply', 'desc': 'Test message with AI and show scores', 'example': '/aitest test this text', 'admin': True},
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
