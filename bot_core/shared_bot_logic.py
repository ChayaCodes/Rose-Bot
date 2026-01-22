"""
Shared bot logic for WhatsApp and Telegram.
Platform-specific adapters should implement the required action methods.
"""

from typing import Dict, List, Optional
import logging
import re

from bot_core.i18n import get_chat_text as get_text, TRANSLATIONS, LANG_NAMES, COMMAND_HELP

from bot_core.services.warn_service import (
    warn_user, reset_user_warns, set_warn_limit, get_warns, get_warn_settings
)
from bot_core.services.rules_service import get_rules, set_rules
from bot_core.services.welcome_service import (
    get_welcome_message as get_welcome,
    set_welcome_message as set_welcome,
)
from bot_core.services.blacklist_service import (
    add_blacklist_word as add_blacklist,
    remove_blacklist_word as remove_blacklist,
    get_blacklist_words as get_blacklist,
    check_blacklist
)
from bot_core.services.locks_service import set_lock, get_locks
from bot_core.services.language_service import get_chat_language as get_chat_lang, set_chat_language as set_chat_lang
from bot_core.services.ban_service import add_ban, remove_ban
from bot_core.services.chat_config_service import should_delete_commands, set_delete_commands
from bot_core.services.ai_moderation_service import (
    get_ai_settings, set_ai_enabled, set_ai_backend, set_ai_api_key, set_ai_threshold,
    set_ai_category_thresholds, set_ai_action, check_content_toxicity
)

logger = logging.getLogger(__name__)


class SharedBotLogic:
    def __init__(self, actions):
        """
        actions must implement:
        - send_message(chat_id, text)
        - delete_message(chat_id, message_id)
        - remove_participant(chat_id, user_id) -> bool
        - add_participants(chat_id, participants: List[str]) -> bool
        - get_invite_link(chat_id) -> Optional[str]
        - is_owner(chat_id, user_id) -> bool  # Group owner/creator
        - is_admin(chat_id, user_id) -> bool  # Group admin or higher
        - get_user_display(user_id) -> str
        - format_mention(user_id) -> str
        Optional:
        - get_group_members(chat_id) -> Optional[List[dict]]
        """
        self.actions = actions

    def _normalize_phone_to_user_id(self, raw_phone: str) -> Optional[str]:
        if not raw_phone:
            return None

        phone = raw_phone.strip()
        if '@' in phone:
            return phone

        digits = re.sub(r'\D', '', phone)
        if not digits:
            return None

        if digits.startswith('00'):
            digits = digits[2:]

        if digits.startswith('0') and len(digits) >= 9:
            digits = '972' + digits[1:]

        if len(digits) < 10:
            return None

        return f"{digits}@c.us"

    def _extract_phone_and_rest(self, text: str) -> (Optional[str], str):
        if not text:
            return None, ''

        match = re.search(r'\+?\d[\d\s().-]{6,}\d', text)
        if not match:
            return None, text.strip()

        phone = match.group(0)
        rest = (text[:match.start()] + text[match.end():]).strip()
        return phone, rest

    def _extract_phone_candidates(self, text: str) -> List[str]:
        if not text:
            return []
        return [m.strip() for m in re.findall(r'\+?\d[\d\s().-]{6,}\d', text)]

    def _extract_digits_from_id(self, value: Optional[str]) -> str:
        if not value:
            return ''
        if '@' in value:
            value = value.split('@')[0]
        return re.sub(r'\D', '', value)

    def _expand_user_candidates(self, user_id: str) -> List[str]:
        candidates = {user_id}
        digits = self._extract_digits_from_id(user_id)
        if digits:
            candidates.add(f"{digits}@c.us")
            candidates.add(f"{digits}@s.whatsapp.net")

        return list(candidates)

    def _resolve_user_from_args(self, chat_id: str, args: str) -> Optional[str]:
        if not args:
            return None

        phone, _ = self._extract_phone_and_rest(args)
        if not phone:
            self.actions.send_message(chat_id, get_text(chat_id, 'invalid_phone', phone=args.strip()))
            return None

        user_id = self._normalize_phone_to_user_id(phone)
        if not user_id:
            self.actions.send_message(chat_id, get_text(chat_id, 'invalid_phone', phone=phone))
            return None

        return user_id

    def _check_locks(self, chat_id: str, message: dict) -> Optional[str]:
        locks = get_locks(chat_id)
        text = message.get('body', '')

        if locks['links']:
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            if re.search(url_pattern, text):
                return get_text(chat_id, 'links_not_allowed')

        return None

    def _check_ai_moderation(self, chat_id: str, text: str) -> Optional[Dict]:
        settings = get_ai_settings(chat_id)
        if not settings['enabled']:
            return None

        from bot_core.content_filter import ContentModerator

        backend = settings['backend']
        api_key = settings['api_key']
        threshold_value = settings['threshold'] if settings['threshold'] <= 1 else settings['threshold'] / 100.0
        action = settings['action']

        moderator = ContentModerator(backend=backend, api_key=api_key)
        thresholds = {
            'toxicity': threshold_value,
            'spam': threshold_value,
            'sexual': threshold_value,
            'threat': threshold_value,
        }
        thresholds.update(settings.get('thresholds', {}))

        result = moderator.check_message(text, thresholds)
        if result.is_flagged:
            return {
                'is_toxic': True,
                'score': result.confidence,
                'backend': moderator.backend,
                'requested_backend': backend,
                'action': action,
                'reason': result.reason,
                'violation_type': str(result.violation_type) if result.violation_type else None,
            }

        return None

    def handle_message(self, message: dict):
        try:
            text = message.get('body', '').strip()
            from_id = message.get('from')
            chat_id = message.get('chatId', from_id)
            is_group = message.get('isGroup', False)

            logger.info(f"Message from {from_id} in {chat_id}: {text[:50]}")

            if text.startswith('/'):
                self.handle_command(text, from_id, chat_id, is_group, message)
                return

            if is_group:
                ai_result = self._check_ai_moderation(chat_id, text)
                if ai_result:
                    action = ai_result.get('action', 'warn')
                    score = ai_result.get('score', 0.0)
                    backend = ai_result.get('backend', 'unknown')
                    requested_backend = ai_result.get('requested_backend', backend)
                    msg_id = message.get('id')

                    do_warn = 'warn' in action
                    do_delete = 'delete' in action
                    do_kick = 'kick' in action
                    do_ban = 'ban' in action

                    action_parts = []
                    if do_warn:
                        action_parts.append(get_text(chat_id, 'ai_action_warn'))
                    if do_delete:
                        action_parts.append(get_text(chat_id, 'ai_action_delete'))
                    if do_kick:
                        action_parts.append(get_text(chat_id, 'ai_action_kick'))
                    if do_ban:
                        action_parts.append(get_text(chat_id, 'ai_action_ban'))

                    actions_text = ' + '.join(action_parts)

                    backend_label = backend if backend == requested_backend else f"{backend} ← {requested_backend}"
                    msg = get_text(chat_id, 'ai_moderation_header', backend=backend_label)
                    msg += get_text(chat_id, 'ai_toxic_detected')
                    msg += get_text(chat_id, 'ai_score_label', score=score)
                    msg += get_text(chat_id, 'ai_reason_label', reason=ai_result.get('reason', get_text(chat_id, 'no_reason')))
                    msg += get_text(chat_id, 'ai_actions_label', actions=actions_text)
                    self.actions.send_message(chat_id, msg)

                    if do_delete and msg_id:
                        self.actions.delete_message(chat_id, msg_id)

                    if do_warn:
                        user_display = self.actions.get_user_display(from_id)
                        warn_count, warn_limit = warn_user(chat_id, from_id, user_display, get_text(chat_id, 'toxic_content'))
                        if warn_count >= warn_limit:
                            _, soft = get_warn_settings(chat_id)
                            if soft:
                                self.actions.remove_participant(chat_id, from_id)
                            else:
                                add_ban(chat_id, from_id, user_display, reason="Too many warns")
                                self.actions.remove_participant(chat_id, from_id)

                    if do_ban:
                        user_display = self.actions.get_user_display(from_id)
                        add_ban(chat_id, from_id, user_display, reason="AI detected toxic content")
                        self.actions.remove_participant(chat_id, from_id)
                    elif do_kick:
                        self.actions.remove_participant(chat_id, from_id)

                    return

                blacklisted = check_blacklist(chat_id, text)
                if blacklisted:
                    self.actions.send_message(chat_id, get_text(chat_id, 'blacklist_detected'))
                    return

                lock_violation = self._check_locks(chat_id, message)
                if lock_violation:
                    self.actions.send_message(chat_id, get_text(chat_id, 'lock_triggered', lock_type=lock_violation))
                    return

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)

    def handle_command(self, text: str, from_id: str, chat_id: str, is_group: bool, message: dict):
        try:
            parts = text.split(maxsplit=1)
            command = parts[0][1:].lower()
            args = parts[1] if len(parts) > 1 else ""

            self._process_command(command, args, from_id, chat_id, is_group, message)

            if is_group and should_delete_commands(chat_id):
                message_id = message.get('id')
                if message_id:
                    self.actions.delete_message(chat_id, message_id)

        except Exception as e:
            logger.error(f"Error handling command '{text}': {e}", exc_info=True)
            try:
                self.actions.send_message(chat_id, get_text(chat_id, 'error_occurred'))
            except Exception:
                pass

    def _process_command(self, command: str, args: str, from_id: str, chat_id: str, is_group: bool, message: dict):
        quoted_msg = message.get('quotedMsg')
        quoted_participant = message.get('quotedParticipant')

        if command == 'start':
            self.cmd_start(chat_id)
        elif command == 'help':
            self.cmd_help(chat_id, from_id, self.actions.is_admin(chat_id, from_id), args)
        elif command == 'info':
            self.cmd_info(chat_id, from_id)
        elif command == 'ping':
            self.actions.send_message(chat_id, get_text(chat_id, 'pong'))

        elif command == 'rules':
            self.cmd_rules(chat_id)
        elif command == 'setrules':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_setrules(chat_id, args)

        elif command == 'warn':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_warn(chat_id, from_id, args, message)
        elif command == 'warns':
            self.cmd_warns(chat_id, from_id, message, args)
        elif command == 'resetwarns':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_resetwarns(chat_id, message, args)
        elif command == 'setwarn':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_setwarn(chat_id, args)

        elif command == 'kick':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_kick(chat_id, message, args)
        elif command == 'ban':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_ban(chat_id, message, args)
        elif command == 'unban':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_unban(chat_id, args)
        elif command == 'role':
            self.cmd_role(chat_id, message, args)
        elif command == 'add':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_add(chat_id, args)
        elif command == 'invite':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_invite(chat_id)
        elif command == 'delcmds':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_delcmds(chat_id, args)

        elif command == 'setwelcome':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_setwelcome(chat_id, args)
        elif command == 'welcome':
            self.cmd_welcome(chat_id)

        elif command == 'blacklist':
            self.cmd_blacklist(chat_id)
        elif command == 'addblacklist':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_addblacklist(chat_id, args)
        elif command == 'rmblacklist':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_rmblacklist(chat_id, args)

        elif command == 'lock':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_lock(chat_id, args)
        elif command == 'unlock':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_unlock(chat_id, args)
        elif command == 'locks':
            self.cmd_locks(chat_id)

        elif command == 'aimod':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimod(chat_id, args)
        elif command == 'aimodset':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodset(chat_id, args)
        elif command == 'aimodstatus':
            self.cmd_aimodstatus(chat_id)
        elif command == 'aimodkey':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodkey(chat_id, args)
        elif command == 'aimodbackend':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodbackend(chat_id, args)
        elif command == 'aimodaction':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodaction(chat_id, args)
        elif command == 'aimodthreshold':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aimodthreshold(chat_id, args)
        elif command == 'aihelp':
            self.cmd_aihelp(chat_id)
        elif command == 'aitest':
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_aitest(chat_id, args, quoted_msg)

        elif command in ('setlang', 'lang'):
            if not self.actions.is_admin(chat_id, from_id):
                self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                return
            self.cmd_setlang(chat_id, args)
        else:
            self.actions.send_message(chat_id, get_text(chat_id, 'unknown_command', command=command))

    def cmd_start(self, chat_id: str):
        self.actions.send_message(chat_id, get_text(chat_id, 'start_msg'))

    def cmd_help(self, chat_id: str, from_id: str, is_admin_user: bool, args: str = ''):
        lang = get_chat_lang(chat_id)

        if args:
            cmd_name = args.lower().strip().lstrip('/')
            cmd_data = COMMAND_HELP.get(lang, {}).get(cmd_name)

            if cmd_data:
                if cmd_data['admin'] and not is_admin_user:
                    self.actions.send_message(chat_id, get_text(chat_id, 'admin_only'))
                    return
                msg = get_text(chat_id, 'help_cmd_header', cmd=cmd_name)
                msg += get_text(chat_id, 'help_cmd_usage', usage=cmd_data['usage'])
                msg += get_text(chat_id, 'help_cmd_desc', desc=cmd_data['desc'])
                msg += get_text(chat_id, 'help_cmd_example', example=cmd_data['example'])
                if cmd_data['admin']:
                    msg += get_text(chat_id, 'help_cmd_admin')
                self.actions.send_message(chat_id, msg)
                return
            else:
                self.actions.send_message(chat_id, get_text(chat_id, 'help_cmd_not_found', cmd=cmd_name))
                return

        msg = get_text(chat_id, 'help_general')
        msg += get_text(chat_id, 'help_general_admin' if is_admin_user else 'help_general_user')

        msg += get_text(chat_id, 'help_rules')
        msg += get_text(chat_id, 'help_rules_admin' if is_admin_user else 'help_rules_user')

        msg += get_text(chat_id, 'help_warns')
        msg += get_text(chat_id, 'help_warns_admin' if is_admin_user else 'help_warns_user')

        if is_admin_user:
            msg += get_text(chat_id, 'help_moderation')
            msg += get_text(chat_id, 'help_moderation_admin')

        msg += get_text(chat_id, 'help_welcome')
        msg += get_text(chat_id, 'help_welcome_admin' if is_admin_user else 'help_welcome_user')

        msg += get_text(chat_id, 'help_blacklist')
        msg += get_text(chat_id, 'help_blacklist_admin' if is_admin_user else 'help_blacklist_user')

        msg += get_text(chat_id, 'help_locks')
        msg += get_text(chat_id, 'help_locks_admin' if is_admin_user else 'help_locks_user')

        if is_admin_user:
            msg += get_text(chat_id, 'help_language_admin')

        msg += get_text(chat_id, 'help_ai')
        msg += get_text(chat_id, 'help_ai_admin' if is_admin_user else 'help_ai_user')

        msg += get_text(chat_id, 'help_note')
        msg += get_text(chat_id, 'help_use_cmd')
        self.actions.send_message(chat_id, msg)

    def cmd_info(self, chat_id: str, from_id: str):
        msg = get_text(chat_id, 'bot_info', from_id=from_id, chat_id_value=chat_id)
        self.actions.send_message(chat_id, msg)

    def cmd_rules(self, chat_id: str):
        rules = get_rules(chat_id)
        if rules:
            msg = get_text(chat_id, 'rules_show', rules=rules)
        else:
            msg = get_text(chat_id, 'rules_not_set')
        self.actions.send_message(chat_id, msg)

    def cmd_setrules(self, chat_id: str, rules_text: str):
        if not rules_text:
            self.actions.send_message(chat_id, get_text(chat_id, 'usage_setrules'))
            return
        set_rules(chat_id, rules_text)
        self.actions.send_message(chat_id, get_text(chat_id, 'rules_set'))

    def cmd_warn(self, chat_id: str, warner_id: str, reason: str, message: dict):
        quoted_msg = message.get('quotedMsg')
        quoted_participant = message.get('quotedParticipant')

        target_user = None
        if quoted_msg and quoted_participant:
            target_user = quoted_participant
        else:
            if not reason:
                self.actions.send_message(chat_id, get_text(chat_id, 'warn_usage'))
                return
            phone, rest = self._extract_phone_and_rest(reason)
            if not phone:
                self.actions.send_message(chat_id, get_text(chat_id, 'warn_usage'))
                return
            target_user = self._normalize_phone_to_user_id(phone)
            if not target_user:
                self.actions.send_message(chat_id, get_text(chat_id, 'invalid_phone', phone=phone))
                return
            reason = rest

        user_display = self.actions.get_user_display(target_user)
        reason = reason or get_text(chat_id, 'no_reason')
        count, limit = warn_user(chat_id, target_user, user_display, reason)
        _, soft = get_warn_settings(chat_id)

        if count >= limit:
            msg = get_text(chat_id, 'warn_limit_reached', user=user_display)
            self.actions.send_message(chat_id, msg)

            if not soft:
                success = self.actions.remove_participant(chat_id, target_user)
                if success:
                    self.actions.send_message(chat_id, get_text(chat_id, 'user_banned', user=user_display))
        else:
            msg = get_text(chat_id, 'warn_issued', user=user_display, reason=reason, count=count, limit=limit)
            self.actions.send_message(chat_id, msg)

    def cmd_warns(self, chat_id: str, user_id: str, message: dict, args: str = ''):
        quoted_participant = message.get('quotedParticipant')
        target_user = quoted_participant

        if not target_user and args:
            target_user = self._resolve_user_from_args(chat_id, args)
            if not target_user:
                return

        if not target_user:
            target_user = user_id

        warns = get_warns(chat_id, target_user)
        limit, _ = get_warn_settings(chat_id)

        user_display = self.actions.get_user_display(target_user)

        if not warns:
            msg = get_text(chat_id, 'warns_none', user=user_display)
        else:
            msg = get_text(chat_id, 'warns_list', count=len(warns), limit=limit)
            for i, warn in enumerate(warns, 1):
                reason = warn.reason or get_text(chat_id, 'no_reason')
                msg += f"{i}. {reason}\n"

        self.actions.send_message(chat_id, msg)

    def cmd_resetwarns(self, chat_id: str, message: dict, args: str = ''):
        quoted_participant = message.get('quotedParticipant')
        target_user = quoted_participant

        if not target_user and args:
            target_user = self._resolve_user_from_args(chat_id, args)
            if not target_user:
                return

        if not target_user:
            self.actions.send_message(chat_id, get_text(chat_id, 'resetwarns_usage'))
            return

        reset_user_warns(chat_id, target_user)
        user_display = self.actions.get_user_display(target_user)
        self.actions.send_message(chat_id, get_text(chat_id, 'warns_reset', user=user_display))

    def cmd_setwarn(self, chat_id: str, limit_str: str):
        try:
            limit = int(limit_str)
            if limit < 1:
                raise ValueError
            set_warn_limit(chat_id, limit)
            self.actions.send_message(chat_id, get_text(chat_id, 'warn_limit_set', limit=limit))
        except Exception:
            self.actions.send_message(chat_id, get_text(chat_id, 'usage_setwarn'))

    def cmd_kick(self, chat_id: str, message: dict, args: str = ''):
        quoted_participant = message.get('quotedParticipant')
        target_user = quoted_participant

        if not target_user and args:
            target_user = self._resolve_user_from_args(chat_id, args)
            if not target_user:
                return

        if not target_user:
            self.actions.send_message(chat_id, get_text(chat_id, 'kick_usage'))
            return

        user_display = self.actions.get_user_display(target_user)
        success = self.actions.remove_participant(chat_id, target_user)
        if success:
            self.actions.send_message(chat_id, get_text(chat_id, 'user_kicked', user=user_display))
        else:
            self.actions.send_message(chat_id, get_text(chat_id, 'kick_failed'))

    def cmd_ban(self, chat_id: str, message: dict, args: str = ''):
        quoted_participant = message.get('quotedParticipant')
        target_user = quoted_participant
        reason = None

        if not target_user and args:
            phone, rest = self._extract_phone_and_rest(args)
            if not phone:
                self.actions.send_message(chat_id, get_text(chat_id, 'ban_usage'))
                return
            target_user = self._normalize_phone_to_user_id(phone)
            if not target_user:
                self.actions.send_message(chat_id, get_text(chat_id, 'invalid_phone', phone=phone))
                return
            reason = rest or None

        if not target_user:
            self.actions.send_message(chat_id, get_text(chat_id, 'ban_usage'))
            return

        user_display = self.actions.get_user_display(target_user)
        add_ban(chat_id, target_user, user_display=user_display, reason=reason)
        success = self.actions.remove_participant(chat_id, target_user)
        if success:
            self.actions.send_message(chat_id, get_text(chat_id, 'user_banned', user=user_display))
        else:
            self.actions.send_message(chat_id, get_text(chat_id, 'ban_failed'))

    def cmd_unban(self, chat_id: str, phone: str):
        if not phone:
            self.actions.send_message(chat_id, get_text(chat_id, 'unban_usage'))
            return

        user_id = self._normalize_phone_to_user_id(phone)
        if not user_id:
            self.actions.send_message(chat_id, get_text(chat_id, 'invalid_phone', phone=phone))
            return

        phone_display = user_id.split('@')[0]
        if remove_ban(chat_id, user_id):
            self.actions.send_message(chat_id, get_text(chat_id, 'user_unbanned', user=phone_display))
        else:
            self.actions.send_message(chat_id, get_text(chat_id, 'user_not_banned'))

    def cmd_role(self, chat_id: str, message: dict, args: str = ''):
        quoted_participant = message.get('quotedParticipant')
        target_user = quoted_participant

        if not target_user and args:
            target_user = self._resolve_user_from_args(chat_id, args)
            if not target_user:
                return

        if not target_user:
            self.actions.send_message(chat_id, get_text(chat_id, 'role_usage'))
            return

        user_display = self.actions.get_user_display(target_user)
        is_admin = False
        members = None
        if hasattr(self.actions, 'get_group_members'):
            try:
                members = self.actions.get_group_members(chat_id)
            except Exception:
                members = None

        if members is None:
            self.actions.send_message(chat_id, get_text(chat_id, 'role_unknown', user=user_display))
            return

        candidates = set(self._expand_user_candidates(target_user))
        target_digits = self._extract_digits_from_id(target_user)
        allow_digit_match = not target_user.endswith('@lid')
        candidate_digits = set()
        if allow_digit_match:
            candidate_digits = {self._extract_digits_from_id(c) for c in candidates if self._extract_digits_from_id(c)}

        for member in members:
            member_id = member.get('id')
            if isinstance(member_id, dict):
                member_id = member_id.get('_serialized') or member_id.get('user')
            if not member_id:
                continue
            if member_id in candidates:
                is_admin = bool(member.get('isAdmin') or member.get('isSuperAdmin') or member.get('isSuperadmin'))
                break
            member_lid = member.get('lid')
            if member_lid and member_lid == target_user:
                is_admin = bool(member.get('isAdmin') or member.get('isSuperAdmin') or member.get('isSuperadmin'))
                break
            member_phone = member.get('phone')
            if member_phone and target_digits and self._extract_digits_from_id(member_phone) == target_digits:
                is_admin = bool(member.get('isAdmin') or member.get('isSuperAdmin') or member.get('isSuperadmin'))
                break
            if allow_digit_match:
                member_digits = self._extract_digits_from_id(member_id)
                if member_digits and member_digits in candidate_digits:
                    is_admin = bool(member.get('isAdmin') or member.get('isSuperAdmin') or member.get('isSuperadmin'))
                    break

        key = 'role_admin' if is_admin else 'role_member'
        self.actions.send_message(chat_id, get_text(chat_id, key, user=user_display))

    def cmd_add(self, chat_id: str, phones: str):
        if not phones:
            self.actions.send_message(chat_id, get_text(chat_id, 'add_usage'))
            return

        phone_list = self._extract_phone_candidates(phones)
        if not phone_list:
            self.actions.send_message(chat_id, get_text(chat_id, 'add_usage'))
            return

        participants = []
        display_numbers = []
        for phone in phone_list:
            user_id = self._normalize_phone_to_user_id(phone)
            if not user_id:
                self.actions.send_message(chat_id, get_text(chat_id, 'invalid_phone', phone=phone))
                return
            participants.append(user_id)
            display_numbers.append(user_id.split('@')[0])

        result = self.actions.add_participants(chat_id, participants)
        success = result.get('success') if isinstance(result, dict) else bool(result)
        if success:
            # Check for invite sent
            invite_sent = False
            invite_link_sent = False
            invite_link_failed = False
            if isinstance(result, dict):
                invite_sent = result.get('inviteSent', False)
                invite_link_sent = result.get('inviteLinkSent', False)
                invite_link_failed = result.get('inviteLinkFailed', False)
                # Also check nested result array
                data = result.get('result') or []
                if not invite_sent and isinstance(data, list):
                    invite_sent = any(r.get('inviteSent') for r in data if isinstance(r, dict))

            if invite_link_failed:
                self.actions.send_message(chat_id, get_text(chat_id, 'invite_private_failed', user=display_numbers[0]))
            elif invite_link_sent:
                self.actions.send_message(chat_id, get_text(chat_id, 'invite_sent_private_link', user=display_numbers[0]))
            elif invite_sent:
                self.actions.send_message(chat_id, get_text(chat_id, 'invite_sent_private', user=display_numbers[0]))
            elif len(participants) == 1:
                self.actions.send_message(chat_id, get_text(chat_id, 'user_added', user=display_numbers[0]))
            else:
                self.actions.send_message(chat_id, get_text(chat_id, 'users_added', count=len(participants)))
        else:
            error = result.get('error') if isinstance(result, dict) else None
            if error:
                logger.error("Failed to add participants", extra={"chat_id": chat_id, "phones": phones, "error": error})
            self.actions.send_message(chat_id, get_text(chat_id, 'user_add_failed', user=phones))

    def cmd_invite(self, chat_id: str):
        link = self.actions.get_invite_link(chat_id)
        if link:
            self.actions.send_message(chat_id, get_text(chat_id, 'invite_link', link=link))
        else:
            self.actions.send_message(chat_id, get_text(chat_id, 'invite_failed'))

    def cmd_delcmds(self, chat_id: str, args: str):
        action = (args or '').strip().lower()
        if action in ('on', 'enable', 'enabled'):
            set_delete_commands(chat_id, True)
            self.actions.send_message(chat_id, get_text(chat_id, 'delete_commands_on'))
        elif action in ('off', 'disable', 'disabled'):
            set_delete_commands(chat_id, False)
            self.actions.send_message(chat_id, get_text(chat_id, 'delete_commands_off'))
        else:
            status = 'ON' if should_delete_commands(chat_id) else 'OFF'
            self.actions.send_message(chat_id, get_text(chat_id, 'delete_commands_status', status=status))

    def cmd_setwelcome(self, chat_id: str, welcome_text: str):
        if not welcome_text:
            self.actions.send_message(chat_id, get_text(chat_id, 'usage_setwelcome'))
            return

        set_welcome(chat_id, welcome_text)
        self.actions.send_message(chat_id, get_text(chat_id, 'welcome_set'))

    def cmd_welcome(self, chat_id: str):
        welcome = get_welcome(chat_id)
        if welcome:
            msg = get_text(chat_id, 'welcome_current', message=welcome)
        else:
            msg = get_text(chat_id, 'welcome_not_set_admin')
        self.actions.send_message(chat_id, msg)

    def cmd_blacklist(self, chat_id: str):
        words = get_blacklist(chat_id)
        if words:
            msg = get_text(chat_id, 'blacklist_list', count=len(words)) + "\n".join(f"• {w}" for w in words)
        else:
            msg = get_text(chat_id, 'blacklist_empty_admin')
        self.actions.send_message(chat_id, msg)

    def cmd_addblacklist(self, chat_id: str, word: str):
        if not word:
            self.actions.send_message(chat_id, get_text(chat_id, 'usage_addblacklist'))
            return

        add_blacklist(chat_id, word)
        self.actions.send_message(chat_id, get_text(chat_id, 'blacklist_added', word=word))

    def cmd_rmblacklist(self, chat_id: str, word: str):
        if not word:
            self.actions.send_message(chat_id, get_text(chat_id, 'usage_rmblacklist'))
            return

        remove_blacklist(chat_id, word)
        self.actions.send_message(chat_id, get_text(chat_id, 'blacklist_removed', word=word))

    def cmd_lock(self, chat_id: str, lock_type: str):
        valid_types = ['links', 'stickers', 'media']
        if lock_type.lower() not in valid_types:
            self.actions.send_message(chat_id, get_text(chat_id, 'usage_lock'))
            return

        set_lock(chat_id, lock_type.lower(), True)
        self.actions.send_message(chat_id, get_text(chat_id, 'locked', lock_type=lock_type))

    def cmd_unlock(self, chat_id: str, lock_type: str):
        valid_types = ['links', 'stickers', 'media']
        if lock_type.lower() not in valid_types:
            self.actions.send_message(chat_id, get_text(chat_id, 'usage_unlock'))
            return

        set_lock(chat_id, lock_type.lower(), False)
        self.actions.send_message(chat_id, get_text(chat_id, 'unlocked', lock_type=lock_type))

    def cmd_locks(self, chat_id: str):
        locks = get_locks(chat_id)
        msg = get_text(chat_id, 'locks_status')
        links_status = get_text(chat_id, 'lock_locked') if locks['links'] else get_text(chat_id, 'lock_unlocked')
        stickers_status = get_text(chat_id, 'lock_locked') if locks['stickers'] else get_text(chat_id, 'lock_unlocked')
        media_status = get_text(chat_id, 'lock_locked') if locks['media'] else get_text(chat_id, 'lock_unlocked')
        msg += f"{get_text(chat_id, 'links_label')}: {links_status}\n"
        msg += f"{get_text(chat_id, 'stickers_label')}: {stickers_status}\n"
        msg += f"{get_text(chat_id, 'media_label')}: {media_status}"
        self.actions.send_message(chat_id, msg)

    def cmd_aimod(self, chat_id: str, args: str):
        if not args:
            self.cmd_aimodstatus(chat_id)
            return

        if args.lower() not in ['on', 'off']:
            self.actions.send_message(chat_id, get_text(chat_id, 'usage_aimod'))
            return

        enabled = args.lower() == 'on'
        set_ai_enabled(chat_id, enabled)
        msg = get_text(chat_id, 'aimod_on') if enabled else get_text(chat_id, 'aimod_off')
        self.actions.send_message(chat_id, msg)

    def cmd_aimodset(self, chat_id: str, args: str):
        parts = args.rsplit(maxsplit=1)
        if len(parts) != 2:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodset_usage'))
            return

        categories_raw = parts[0].lower()
        try:
            threshold = int(parts[1])
            if threshold < 0 or threshold > 100:
                raise ValueError
        except Exception:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimod_threshold_invalid'))
            return

        def normalize_category(value: str) -> str:
            return value.strip().lower().replace('-', '_').replace('/', '_')

        valid_categories = [
            'toxicity', 'severe_toxicity', 'obscene', 'insult', 'identity_hate',
            'spam', 'promotion', 'sexual', 'sexual_minors', 'threat',
            'harassment', 'harassment_threatening', 'hate', 'hate_threatening',
            'violence', 'violence_graphic', 'self_harm', 'self_harm_intent',
            'self_harm_instructions', 'illicit', 'illicit_violent'
        ]

        if categories_raw in ('all', '*'):
            categories = valid_categories
        else:
            categories = [normalize_category(c) for c in categories_raw.split(',') if c.strip()]

        invalid = [c for c in categories if c not in valid_categories]
        if invalid:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodset_invalid_category', categories=', '.join(valid_categories)))
            return

        set_ai_category_thresholds(chat_id, categories, threshold)
        display_categories = 'all' if categories_raw in ('all', '*') else ', '.join(categories)
        self.actions.send_message(chat_id, get_text(chat_id, 'aimodset_threshold_set', category=display_categories, threshold=threshold))

    def cmd_aihelp(self, chat_id: str):
        self.actions.send_message(chat_id, get_text(chat_id, 'aihelp_full'))

    def cmd_aitest(self, chat_id: str, args: str, quoted_msg: Optional[str] = None):
        test_text = None
        if quoted_msg:
            if isinstance(quoted_msg, dict):
                test_text = quoted_msg.get('body', '')
            else:
                test_text = quoted_msg
        elif args:
            test_text = args
        else:
            self.actions.send_message(chat_id, get_text(chat_id, 'aitest_usage'))
            return

        if not isinstance(test_text, str):
            test_text = str(test_text)
        if not test_text.strip():
            self.actions.send_message(chat_id, get_text(chat_id, 'aitest_usage'))
            return

        settings = get_ai_settings(chat_id)

        from bot_core.content_filter import ContentModerator
        moderator = ContentModerator(
            backend=settings['backend'],
            api_key=settings['api_key']
        )

        requested_backend = settings['backend']
        used_backend = moderator.backend

        threshold_value = settings['threshold'] / 100.0
        thresholds = {
            'toxicity': threshold_value,
            'spam': threshold_value,
            'sexual': threshold_value,
            'threat': threshold_value,
        }
        thresholds.update(settings.get('thresholds', {}))

        result = moderator.check_message(test_text, thresholds)

        backend_emoji = {
            'openai': '🤖'
        }

        msg = get_text(chat_id, 'aitest_header')
        msg += get_text(chat_id, 'aitest_backend', emoji=backend_emoji.get(requested_backend, '❓'), backend=requested_backend)
        if used_backend != requested_backend:
            msg += get_text(chat_id, 'aitest_backend_used_fallback', emoji=backend_emoji.get(used_backend, '❓'), backend=used_backend)
        msg += "\n"
        msg += get_text(chat_id, 'aitest_text', text=f"{test_text[:100]}{'...' if len(test_text) > 100 else ''}")
        msg += get_text(chat_id, 'aitest_scores')

        if result.scores:
            for category, score in sorted(result.scores.items()):
                percentage = score * 100
                if category == 'promotion':
                    threshold_value = thresholds.get('spam', thresholds.get('toxicity', 0.7))
                else:
                    threshold_value = thresholds.get(category, thresholds.get('toxicity', 0.7))
                threshold = threshold_value * 100
                emoji = '🔴' if score >= threshold_value else '🟢'
                display_category = category.replace('_', ' ').title()
                msg += get_text(chat_id, 'aitest_score_line', emoji=emoji, category=display_category, percentage=percentage, threshold=threshold)
        else:
            msg += get_text(chat_id, 'aitest_no_scores')

        msg += get_text(chat_id, 'aitest_result')
        if result.is_flagged:
            msg += get_text(chat_id, 'aitest_flagged')
            msg += get_text(chat_id, 'aitest_type', type=result.violation_type)
            msg += get_text(chat_id, 'aitest_confidence', confidence=result.confidence * 100)
            msg += get_text(chat_id, 'aitest_reason', reason=result.reason)
        else:
            msg += get_text(chat_id, 'aitest_passed')
            msg += get_text(chat_id, 'aitest_reason', reason=result.reason)

        self.actions.send_message(chat_id, msg)

    def cmd_aimodstatus(self, chat_id: str):
        settings = get_ai_settings(chat_id)

        if not settings['enabled']:
            msg = get_text(chat_id, 'aimod_status_disabled')
        else:
            backend_emoji = {
                'openai': '🤖'
            }
            backend_name = {
                'openai': 'OpenAI'
            }

            action = settings['action']
            if action == 'warn':
                action_display = get_text(chat_id, 'ai_action_warn')
            elif action == 'delete':
                action_display = get_text(chat_id, 'ai_action_delete')
            elif action == 'kick':
                action_display = get_text(chat_id, 'ai_action_kick')
            elif action == 'ban':
                action_display = get_text(chat_id, 'ai_action_ban')
            elif action == 'warn_delete':
                action_display = f"{get_text(chat_id, 'ai_action_warn')} + {get_text(chat_id, 'ai_action_delete')}"
            elif action == 'delete_kick':
                action_display = f"{get_text(chat_id, 'ai_action_delete')} + {get_text(chat_id, 'ai_action_kick')}"
            elif action == 'delete_ban':
                action_display = f"{get_text(chat_id, 'ai_action_delete')} + {get_text(chat_id, 'ai_action_ban')}"
            else:
                action_display = action

            backend = settings['backend']
            api_key_status = get_text(chat_id, 'aimod_status_api_key_set') if settings['api_key'] else get_text(chat_id, 'aimod_status_api_key_not_set')

            msg = get_text(chat_id, 'aimod_status_header')
            msg += get_text(chat_id, 'aimod_status_enabled')
            msg += get_text(chat_id, 'aimod_status_backend', emoji=backend_emoji.get(backend, '❓'), name=backend_name.get(backend, backend))
            msg += get_text(chat_id, 'aimod_status_api_key', status=api_key_status)
            msg += get_text(chat_id, 'aimod_status_threshold', threshold=settings['threshold'])
            msg += get_text(chat_id, 'aimod_status_action', action=action_display)
            msg += get_text(chat_id, 'aimod_status_actions_header')
            msg += get_text(chat_id, 'aimod_status_action_warn')
            msg += get_text(chat_id, 'aimod_status_action_delete')
            msg += get_text(chat_id, 'aimod_status_action_kick')
            msg += get_text(chat_id, 'aimod_status_action_ban')
            msg += get_text(chat_id, 'aimod_status_commands')
            msg += get_text(chat_id, 'aimod_status_cmd_backend')
            msg += get_text(chat_id, 'aimod_status_cmd_threshold')
            msg += get_text(chat_id, 'aimod_status_cmd_action')

        self.actions.send_message(chat_id, msg)

    def cmd_aimodkey(self, chat_id: str, args: str):
        parts = args.split(maxsplit=1)
        if len(parts) != 2:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodkey_usage'))
            return

        backend = parts[0].lower()
        api_key = parts[1]

        valid_backends = ['openai']
        if backend not in valid_backends:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodkey_invalid_backend', backends=', '.join(valid_backends)))
            return

        set_ai_backend(chat_id, backend)
        set_ai_api_key(chat_id, api_key)
        self.actions.send_message(chat_id, get_text(chat_id, 'aimodkey_key_saved', backend=backend))

    def cmd_aimodbackend(self, chat_id: str, backend: str):
        if not backend:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodbackend_usage'))
            return

        backend = backend.lower()
        valid_backends = ['openai']

        if backend not in valid_backends:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodbackend_invalid_backend', backends=', '.join(valid_backends)))
            return

        settings = get_ai_settings(chat_id)

        if backend == 'openai' and not settings['api_key']:
            import os
            if not os.getenv('OPENAI_API_KEY'):
                self.actions.send_message(
                    chat_id,
                    get_text(
                        chat_id,
                        'aimodbackend_missing_key',
                        backend=backend,
                        env_var='OPENAI_API_KEY'
                    )
                )
                return

        set_ai_backend(chat_id, backend)
        self.actions.send_message(chat_id, get_text(chat_id, 'aimodbackend_set', backend=backend))

    def cmd_aimodaction(self, chat_id: str, action: str):
        if not action:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodaction_usage'))
            return

        action = action.lower()
        valid_actions = ['warn', 'delete', 'kick', 'ban', 'warn_delete', 'delete_kick', 'delete_ban']

        if action not in valid_actions:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodaction_invalid', action=action, actions=', '.join(valid_actions)))
            return

        set_ai_action(chat_id, action)

        if action == 'warn':
            action_desc = get_text(chat_id, 'ai_action_warn')
        elif action == 'delete':
            action_desc = get_text(chat_id, 'ai_action_delete')
        elif action == 'kick':
            action_desc = get_text(chat_id, 'ai_action_kick')
        elif action == 'ban':
            action_desc = get_text(chat_id, 'ai_action_ban')
        elif action == 'warn_delete':
            action_desc = f"{get_text(chat_id, 'ai_action_warn')} + {get_text(chat_id, 'ai_action_delete')}"
        elif action == 'delete_kick':
            action_desc = f"{get_text(chat_id, 'ai_action_delete')} + {get_text(chat_id, 'ai_action_kick')}"
        elif action == 'delete_ban':
            action_desc = f"{get_text(chat_id, 'ai_action_delete')} + {get_text(chat_id, 'ai_action_ban')}"
        else:
            action_desc = action

        self.actions.send_message(chat_id, get_text(chat_id, 'aimodaction_set', action=action_desc))

    def cmd_aimodthreshold(self, chat_id: str, threshold_str: str):
        if not threshold_str:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodthreshold_usage'))
            return

        try:
            threshold = int(threshold_str)
            if threshold < 0 or threshold > 100:
                raise ValueError
        except Exception:
            self.actions.send_message(chat_id, get_text(chat_id, 'aimodthreshold_invalid'))
            return

        set_ai_threshold(chat_id, threshold)

        sensitivity = (
            get_text(chat_id, 'sensitivity_low')
            if threshold < 40
            else get_text(chat_id, 'sensitivity_medium')
            if threshold < 70
            else get_text(chat_id, 'sensitivity_high')
        )

        self.actions.send_message(chat_id, get_text(chat_id, 'aimodthreshold_set', threshold=threshold, sensitivity=sensitivity))

    def cmd_setlang(self, chat_id: str, args: str):
        if not args:
            current_lang = get_chat_lang(chat_id)
            lang_name = LANG_NAMES.get(current_lang, current_lang)
            msg = get_text(chat_id, 'lang_current', lang_name=lang_name)
            self.actions.send_message(chat_id, msg)
            return

        lang_code = args.lower().strip()
        if lang_code not in TRANSLATIONS:
            msg = get_text(chat_id, 'lang_invalid')
            self.actions.send_message(chat_id, msg)
            return

        set_chat_lang(chat_id, lang_code)
        lang_name = LANG_NAMES.get(lang_code, lang_code)
        msg = get_text(chat_id, 'lang_changed', lang=lang_code, lang_name=lang_name)
        self.actions.send_message(chat_id, msg)

    def handle_group_join(self, event: dict):
        try:
            chat_id = event.get('chatId')
            participants = event.get('participants', [])

            if not chat_id or not participants:
                return

            logger.info(f"Group join event in {chat_id}: {participants}")

            welcome_msg = get_welcome(chat_id)
            if not welcome_msg:
                return

            for participant_id in participants:
                message = welcome_msg.replace('{mention}', self.actions.format_mention(participant_id))
                self.actions.send_message(chat_id, message)
                logger.info(f"Sent welcome message to {participant_id}")
        except Exception as e:
            logger.error(f"Error handling group join: {e}")
