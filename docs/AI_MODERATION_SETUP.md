# 🤖 AI Content Moderation Setup

מדריך הגדרת מודרציה חכמה עם תמיכה בעברית ואנגלית

---

## 📊 השוואת Backend-ים

| Backend | שפות | דיוק | מחיר | מהירות | הגדרה |
|---------|------|------|------|---------|-------|
| **Perspective API** ⭐ | עברית, אנגלית, +30 שפות | 9/10 | **חינם** (1M/יום) | מהיר | קל |
| **Azure Content** | עברית, אנגלית, +100 שפות | 10/10 | $$$ | מהיר מאוד | בינוני |
| **OpenAI** | אנגלית בלבד | 10/10 | **חינם** | מהיר | קל מאוד |
| **Detoxify** | אנגלית בלבד | 8/10 | **חינם** | בינוני | קל |
| **Rule-based** | עברית, אנגלית | 5/10 | **חינם** | מהיר מאוד | אין צורך |

---

## 1️⃣ Google Perspective API (מומלץ!) ⭐

**יתרונות:**
- ✅ תמיכה מלאה בעברית
- ✅ **חינם לחלוטין** עד 1 מיליון בקשות ליום
- ✅ דיוק גבוה מאוד
- ✅ זיהוי: רעילות, איומים, עלבונות, שנאה, תוכן מיני

### איך להשיג API Key:

1. כנס ל-[Google Cloud Console](https://console.cloud.google.com/)
2. צור פרויקט חדש או בחר קיים
3. הפעל את ה-API:
   - לך ל-**APIs & Services** → **Library**
   - חפש **Perspective Comment Analyzer API**
   - לחץ **Enable**
4. צור API Key:
   - לך ל-**APIs & Services** → **Credentials**
   - לחץ **Create Credentials** → **API Key**
   - העתק את המפתח

### הגדרה:

**בקובץ `.env` או משתני סביבה:**
```bash
PERSPECTIVE_API_KEY=your_api_key_here
```

**בקוד Python:**
```python
from bot_core.content_filter import get_moderator

moderator = get_moderator(
    backend='perspective',
    api_key='your_api_key_here'  # או None אם הגדרת במשתנה סביבה
)

result = moderator.check_message("טקסט לבדיקה")
if result.is_flagged:
    print(f"❌ {result.reason}")
```

**התקנה:**
```bash
pip install google-api-python-client
```

---

## 2️⃣ Azure Content Moderator (ארגוני)

**יתרונות:**
- ✅ תמיכה מלאה בעברית
- ✅ דיוק הכי גבוה
- ✅ תמיכה טכנית מקצועית
- ❌ בתשלום (אבל יש free tier)

### איך להשיג API Key:

1. כנס ל-[Azure Portal](https://portal.azure.com/)
2. צור **Content Safety** resource:
   - חפש "Content Safety" בחיפוש
   - לחץ **Create**
   - בחר subscription ו-resource group
   - בחר region (מומלץ: West Europe)
   - בחר pricing tier (F0 = חינם למוגבל)
3. לאחר היצירה:
   - לך ל-**Keys and Endpoint**
   - העתק את **Key 1** ואת **Endpoint**

### הגדרה:

**בקובץ `.env`:**
```bash
AZURE_API_KEY=your_api_key_here
AZURE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
```

**בקוד:**
```python
moderator = get_moderator(backend='azure')
```

**התקנה:**
```bash
pip install azure-ai-contentsafety
```

---

## 3️⃣ OpenAI Moderation API (אנגלית בלבד)

**יתרונות:**
- ✅ **חינם לחלוטין**
- ✅ דיוק מצוין
- ✅ מהיר מאוד
- ❌ אנגלית בלבד (לא תומך בעברית)

### איך להשיג API Key:

1. כנס ל-[OpenAI Platform](https://platform.openai.com/)
2. הירשם / התחבר
3. לך ל-[API Keys](https://platform.openai.com/api-keys)
4. לחץ **Create new secret key**
5. העתק את המפתח (לא תוכל לראות אותו שוב!)

### הגדרה:

**בקובץ `.env`:**
```bash
OPENAI_API_KEY=sk-your-key-here
```

**בקוד:**
```python
moderator = get_moderator(backend='openai')
```

**התקנה:**
```bash
pip install openai
```

---

## 4️⃣ Detoxify (מקומי, ללא API)

**יתרונות:**
- ✅ **חינם לחלוטין**
- ✅ פועל לוקלית (ללא שרת חיצוני)
- ✅ פרטיות מוחלטת
- ❌ אנגלית בלבד
- ❌ צריך די הרבה משאבים (RAM)

### הגדרה:

**התקנה:**
```bash
pip install detoxify torch
```

**בקוד:**
```python
moderator = get_moderator(backend='detoxify')
```

ההורדה הראשונה תיקח זמן (מוריד את המודל ~500MB)

---

## 5️⃣ Rule-based (ברירת מחדל)

**יתרונות:**
- ✅ **חינם לחלוטין**
- ✅ תמיכה בעברית + אנגלית
- ✅ מהיר מאוד
- ✅ אין צורך בהגדרה
- ❌ דיוק נמוך יחסית

### שימוש:

```python
moderator = get_moderator(backend='rules')  # ברירת מחדל
```

אין צורך בהתקנות נוספות!

---

## 🚀 שימוש בבוט

### הפעלת AI Moderation:

```
/aimod on
```

### הגדרת רגישות:

```
/aimodset toxicity 70     # רגישות 70% לתוכן רעיל
/aimodset spam 80         # רגישות 80% לספאם
/aimodset sexual 60       # רגישות 60% לתוכן מיני
```

### בדיקת סטטוס:

```
/aimodstatus
```

---

## 💡 המלצות

### לשימוש ביתי/קטן:
- **Perspective API** - הכי טוב! תמיכה בעברית וחינם

### לארגון/עסק:
- **Azure Content Moderator** - המקצועי ביותר, תמיכה מלאה

### לאנגלית בלבד:
- **OpenAI** - חינם ומצוין

### ללא אינטרנט:
- **Detoxify** - פועל לוקלית

### בלי הגדרה כלל:
- **Rule-based** - עובד out-of-the-box

---

## 🔧 שינוי Backend בזמן ריצה

ערוך את `whatsapp_bot_full.py`:

```python
# בפונקציה check_ai_moderation, שנה:
if bot_moderator is None:
    bot_moderator = get_moderator(
        backend='perspective',  # <-- שנה כאן
        api_key=None  # או מפתח ישירות
    )
```

או הגדר משתנה סביבה:
```bash
PERSPECTIVE_API_KEY=your_key_here
```

---

## ❓ שאלות נפוצות

**Q: איזה backend הכי טוב?**
A: לעברית + אנגלית - **Perspective API** (חינם ומצוין)

**Q: האם צריך לשלם?**
A: לא! Perspective, OpenAI, ו-Detoxify חינמיים לחלוטין

**Q: כמה זמן לוקח הגדרה?**
A: Perspective - 5 דקות. Rule-based - 0 דקות (כבר עובד)

**Q: מה הדיוק של כל backend?**
A: Azure > OpenAI > Perspective > Detoxify > Rules

**Q: האם זה עובד עם טלגרם?**
A: כן! `bot_core/content_filter.py` עובד גם בטלגרם וגם בוואטסאפ

---

## 📝 דוגמה מלאה

```python
from bot_core.content_filter import get_moderator

# אפשרות 1: Perspective (עברית + אנגלית)
moderator = get_moderator('perspective', api_key='YOUR_KEY')

# אפשרות 2: Rule-based (ללא הגדרה)
moderator = get_moderator('rules')

# בדיקת הודעה
result = moderator.check_message("הודעה לבדיקה")

if result.is_flagged:
    print(f"❌ הודעה חסומה: {result.reason}")
    print(f"רמת ביטחון: {result.confidence:.1%}")
    print(f"ציונים: {result.scores}")
else:
    print("✅ הודעה תקינה")

# בדיקת יכולות
print(f"קטגוריות נתמכות: {moderator.get_supported_categories()}")
print(f"שפות נתמכות: {moderator.get_supported_languages()}")
```

---

**זקוק לעזרה?** פתח issue ב-GitHub או שאל בקבוצה 💬
