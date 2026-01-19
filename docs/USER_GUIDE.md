# WhatsApp Bot User Guide
## For Non-Technical Users

---

## 📱 What is this bot?

This is a WhatsApp bot that helps manage groups automatically. It can:
- Welcome new members
- Remove spam messages
- Ban troublesome users
- Answer common questions
- Much more!

---

## 🚀 Getting Started

### 1. Add the Bot to Your Group

If someone else set up the bot, they need to:
1. Save the bot's phone number in their contacts
2. Add it to your WhatsApp group
3. Make it a group admin (important!)

### 2. Talk to the Bot

You can send commands to the bot in two ways:

**In Private Chat:**
1. Find the bot's number in your contacts
2. Send it a message with a command

**In Group Chat:**
1. Just type the command in the group
2. The bot will respond

---

## 💬 Basic Commands

All commands start with `/` (slash)

### Getting Help

```
/start
```
- Use this when you first talk to the bot
- Shows welcome message

```
/help
```
- Shows list of all available commands
- Use this if you forget what commands exist

```
/info
```
- Shows information about the bot
- Shows your user ID

### Fun Commands

```
/echo Hello world
```
- The bot will repeat what you say
- Try: `/echo I love this bot!`

---

## 👥 Group Management Commands
### (Only for Group Admins)

### Removing Users

```
/kick
```
- Reply to someone's message with `/kick`
- That person will be removed from the group
- Example:
  1. Find a spam message
  2. Reply to it
  3. Type `/kick`
  4. Done!

```
/ban
```
- Same as kick, but permanently blocks the user
- They can't rejoin the group

### Warnings

```
/warn
```
- Reply to someone's message with `/warn`
- Gives them a warning
- After 3 warnings, they're automatically kicked

```
/warns
```
- Reply to someone's message with `/warns`
- Shows how many warnings they have

```
/resetwarn
```
- Reply to someone's message to clear their warnings

### Quiet Mode

```
/mute
```
- Reply to someone's message to stop them from sending messages
- They can still read messages

```
/unmute
```
- Allow them to send messages again

---

## ⚙️ Group Settings Commands

### Welcome Messages

```
/setwelcome Hello {first}, welcome to {chat}!
```
- Sets a message to show when new people join
- Use `{first}` for their name
- Use `{chat}` for group name

```
/welcome on
```
- Turn on welcome messages

```
/welcome off
```
- Turn off welcome messages

### Rules

```
/setrules Be nice to everyone. No spam.
```
- Sets the group rules

```
/rules
```
- Shows the group rules

### Filters (Auto-Responses)

```
/filter hello Hi there! How can I help?
```
- When someone says "hello", bot responds automatically

```
/stop hello
```
- Removes the auto-response for "hello"

```
/filters
```
- Shows all active filters

---

## 🚫 Protection Features

### Anti-Flood

Stops people from sending too many messages too quickly.

```
/setflood 10
```
- Kicks users who send more than 10 messages in a row
- Prevents spam

```
/flood
```
- Shows current flood settings

### Blacklist

Blocks specific words from being used.

```
/addblacklist badword
```
- Any message with "badword" will be deleted
- User gets a warning

```
/blacklist
```
- Shows all blacklisted words

```
/unblacklist badword
```
- Removes "badword" from blacklist

---

## 📝 Notes (Saved Messages)

Save important information for later.

```
/save grouplink https://chat.whatsapp.com/xxxxx
```
- Saves the group link with name "grouplink"

```
/get grouplink
```
- Shows the saved group link

```
/notes
```
- Shows all saved notes

```
/clear grouplink
```
- Deletes the saved note

---

## 🔍 Information Commands

### User Information

```
/id
```
- Shows your user ID and chat ID

Reply to someone's message with:
```
/id
```
- Shows their user ID

### Group Information

```
/stats
```
- Shows group statistics
- Number of members, messages, etc.

---

## 💡 Tips for Using the Bot

### 1. Making Commands Work

- Commands only work if you're an admin (for admin commands)
- The bot must be an admin in the group
- Commands are case-insensitive (`/Help` works the same as `/help`)

### 2. Replying to Messages

Many commands need you to reply to a message:
1. Long-press on the message
2. Tap "Reply"
3. Type the command
4. Send

### 3. Getting Help

If a command doesn't work:
- Check if you spelled it correctly
- Check if you have admin rights
- Check if the bot is an admin
- Try `/help` to see available commands

---

## 🎯 Common Scenarios

### Scenario 1: Someone is Spamming

1. Reply to their spam message
2. Type `/warn`
3. If they continue, type `/kick` (replied to their message)

### Scenario 2: Setting Up New Group

1. Make bot an admin
2. Set welcome message: `/setwelcome Welcome {first}!`
3. Set rules: `/setrules Be respectful. No spam.`
4. Turn on welcome: `/welcome on`
5. Set flood limit: `/setflood 5`

### Scenario 3: Blocking Bad Words

1. Type `/addblacklist badword`
2. Repeat for each word you want to block
3. Check list: `/blacklist`

---

## ❓ Frequently Asked Questions

**Q: Why isn't the bot responding?**
A: Make sure:
- The bot is in the group
- The bot is an admin
- You're using commands correctly (starting with `/`)

**Q: Can I use the bot in private chat?**
A: Yes! Most commands work in private chat too.

**Q: Who can use admin commands?**
A: Only WhatsApp group admins can use commands like `/kick`, `/ban`, `/warn`

**Q: How do I see all commands?**
A: Type `/help` to see the complete list

**Q: Can I customize the bot's responses?**
A: Yes! Use `/filter` to create custom auto-responses

**Q: How do I remove the bot?**
A: Just remove it from the group like any other member

---

## 📞 Need More Help?

If you're still having trouble:
1. Try `/help` command first
2. Ask the person who set up the bot
3. Check if the bot is an admin in your group
4. Make sure you're an admin (for admin commands)

---

## 🎉 Have Fun!

The bot is here to make managing your group easier. Experiment with different commands and find what works best for your group!

**Pro Tip:** Start simple! Just use `/welcome`, `/rules`, and `/kick` at first. Add more features as you get comfortable.

---

*This bot is powered by Rose Bot technology*
