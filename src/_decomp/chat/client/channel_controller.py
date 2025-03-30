#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\channel_controller.py
import blue
import sys
import signals
import localization
import gametime
import threadutils
import logging
from chat.client.hide_messages import open_hide_message_settings
from collections import deque
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate
from carbonui.util.stringManip import SanitizeFilename
from eveProto.generated.eve_public.chat.local.local_pb2 import CLASSIFICATION_INVISIBLE
from inventorycommon.const import ownerSystem, ownerNone
from chatutil import CompleteAutoLinks
from chat.common.const import CLASSIFACTION_TO_COLOR, MemberClassification
from chat.client.const import MAX_MESSAGES_IN_HISTORY, CHATLOG_TEMPLATE, MAX_MESSAGES_PER_SEC, MAX_PENDING_MESSAGES
from chat.client.util import parse_chat_message, should_hide_message
logger = logging.getLogger('chat')

class BaseChatChannelController(object):
    __notifyevents__ = []

    def __init__(self, channel_id, category_id):
        self._is_closing = False
        self._channel_id = channel_id
        self._category_id = category_id
        self._window_id = 'chatchannel_%s' % self._channel_id
        self._member_ids = set()
        self._pending_messages = set()
        self._messages = deque(maxlen=MAX_MESSAGES_IN_HISTORY)
        self._sent_message_timestamps = deque(maxlen=MAX_MESSAGES_PER_SEC)
        self._logfile = None
        self._muted = None
        self.on_members_set = signals.Signal('on_members_set')
        self.on_members_cleared = signals.Signal('on_members_cleared')
        self.on_member_added = signals.Signal('on_member_added')
        self.on_member_removed = signals.Signal('on_member_removed')
        self.on_member_data_changed = signals.Signal('on_member_data_changed')
        self.on_message_added = signals.Signal('on_message_added')
        self.on_messages_cleared = signals.Signal('on_messages_cleared')
        self.on_pending_message_removed = signals.Signal('on_pending_message_removed')
        self._register()

    def close(self):
        if self._is_closing:
            return
        self._is_closing = True
        self._pending_messages.clear()
        self._messages.clear()
        self._sent_message_timestamps.clear()
        self._unregister()

    def _register(self):
        sm.RegisterNotify(self)
        self.chat_service.on_member_data_changed.connect(self._on_member_data_changed)

    def _unregister(self):
        sm.UnregisterNotify(self)
        self.chat_service.on_member_data_changed.disconnect(self._on_member_data_changed)

    @property
    def chat_service(self):
        return sm.GetService('chat')

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def category_id(self):
        return self._category_id

    @property
    def window_id(self):
        return self._window_id

    @property
    def window_display_name(self):
        return self.category_id

    @property
    def is_closable(self):
        return False

    @property
    def member_ids(self):
        return self._member_ids

    @property
    def member_count(self):
        return len(self._member_ids)

    @property
    def member_count_tooltip(self):
        return localization.GetByLabel('UI/Chat/CapsuleerCounterHint')

    @property
    def messages(self):
        return self._messages

    @property
    def message_count(self):
        return len(self._messages)

    @property
    def motd(self):
        return ''

    def close_by_user(self):
        self.chat_service.close_channel(self.channel_id)

    def clear_messages(self):
        if not self._messages:
            return
        self._messages.clear()
        self._pending_messages.clear()
        self._sent_message_timestamps.clear()
        self.on_messages_cleared()

    def _clear_members(self):
        if not self._member_ids:
            return
        self._member_ids.clear()
        self.on_members_cleared()

    def _on_member_data_changed(self, character_id, data):
        if character_id in self._member_ids:
            self.on_member_data_changed(character_id, data)

    def message_received(self, sender_id, text, message_id = None):
        if sender_id == session.charid:
            return
        if self.chat_service.is_blocked_character(sender_id, self.get_member_data(sender_id)):
            return
        if self.chat_service.is_reported_spammer(sender_id):
            return
        text = parse_chat_message(text)
        if not text:
            return
        if self.should_hide_message(text):
            return
        self._add_to_messages(sender_id, text)

    def should_hide_message(self, text):
        return should_hide_message(self.channel_id, self.category_id, text)

    def open_hide_message_settings(self):
        open_hide_message_settings(category_id=self.category_id, channel_id=self.channel_id, channel_name=self.channel_id)

    def add_game_message(self, text, sender_id = None):
        self._add_to_messages(sender_id, text)

    def can_send_chat_message(self):
        if self._is_at_sent_message_cap():
            eve.Message('uiwarning03')
            return False
        if self._muted:
            self.add_game_message(self._get_muted_reason(), sender_id=ownerSystem)
            return False
        return True

    def _is_at_sent_message_cap(self):
        if len(self._pending_messages) > MAX_PENDING_MESSAGES:
            return True
        if len(self._sent_message_timestamps) < MAX_MESSAGES_PER_SEC:
            return False
        return gametime.GetSecondsSinceWallclockTime(self._sent_message_timestamps[0]) < 1

    def send_chat_message(self, text):
        pass

    def _prime_unprimed_members(self, member_ids):
        members_to_prime = set()
        for member_id in member_ids:
            if not cfg.eveowners.GetIfExists(member_id):
                members_to_prime.add(member_id)

        cfg.eveowners.Prime(members_to_prime)

    def set_members(self, members):
        if not members:
            self._clear_members()
            return
        members = {member_id:member_data for member_id, member_data in members.iteritems() if member_data['classification'] != CLASSIFICATION_INVISIBLE}
        self._member_ids = set(members.keys())
        self._prime_unprimed_members(self._member_ids)
        self.chat_service.update_members_info(members)
        self.on_members_set()

    def add_member(self, character_id, character_info = None):
        if character_id in self._member_ids:
            return
        if character_info and character_info['classification'] == CLASSIFICATION_INVISIBLE:
            return
        self._member_ids.add(character_id)
        if character_info:
            self.chat_service.update_members_info({character_id: character_info})
        self.on_member_added(character_id)

    def remove_member(self, character_id):
        if character_id not in self._member_ids:
            return
        self._member_ids.remove(character_id)
        self.on_member_removed(character_id)

    def can_invite_character(self, character_id):
        return False

    def invite_character(self, character_id):
        pass

    def get_member_data(self, member_id):
        return self.chat_service.get_member_info(member_id)

    def has_member_data(self, member_id):
        return self.chat_service.has_member_info(member_id)

    def get_color_for_sender(self, member_id):
        if member_id in (ownerSystem, ownerNone):
            return '0xb2ee6666'
        if self.has_member_data(member_id):
            sender_classification = self.get_member_data(member_id).get('classification', None)
            return CLASSIFACTION_TO_COLOR.get(sender_classification, '0x99ffffff')
        try:
            name = cfg.eveowners.Get(member_id).name
            if name.startswith('GM'):
                return CLASSIFACTION_TO_COLOR[MemberClassification.GAME_MASTER]
            if name.startswith('CCP'):
                return CLASSIFACTION_TO_COLOR[MemberClassification.DEVELOPER]
            if name.startswith('ISD'):
                return CLASSIFACTION_TO_COLOR[MemberClassification.VOLUNTEER]
            return '0x99ffffff'
        except:
            return '0x99ffffff'

    def set_muted(self, end_date, reason):
        self._muted = {'end_date': end_date,
         'reason': reason}

    def clear_muted(self):
        self._muted = None

    def mute_player(self, character_id, duration, reason):
        pass

    def _get_muted_reason(self):
        if not self._muted:
            return ''
        return self._muted['reason']

    def _add_to_messages(self, sender_id, text, timestamp = None, color = None):
        if not timestamp:
            timestamp = gametime.GetWallclockTime()
        if not color:
            color = self.get_color_for_sender(sender_id)
        text = CompleteAutoLinks(text)
        self._messages.append((sender_id,
         text,
         timestamp,
         color))
        self.on_message_added(sender_id, text, timestamp, color)
        self._write_to_log_file(sender_id, text, timestamp)

    def _add_pending_message(self, message_id):
        self._pending_messages.add(message_id)
        self._sent_message_timestamps.append(gametime.GetWallclockTime())

    def _remove_pending_message(self, message_id, was_delivered = True):
        if message_id not in self._pending_messages:
            return
        self._pending_messages.remove(message_id)
        self.on_pending_message_removed(message_id, was_delivered)

    def _close_logfile(self):
        if self._logfile:
            self._logfile.Close()
            self._logfile = None

    @threadutils.threaded
    def _setup_log_file(self):
        if self._logfile or not settings.user.ui.Get('logchat', True):
            return
        now = gametime.GetWallclockTime()
        if session.charid:
            character_name = cfg.eveowners.Get(session.charid).name
        else:
            logger.warning('_SetupLogfile %s: No charid in session. Listener will be unknown character in chatlog' % self.window_display_name)
            character_name = 'unknown_character'
        chatlog = CHATLOG_TEMPLATE % (self.channel_id,
         self.window_display_name,
         character_name,
         FmtDate(now))
        year, month, weekday, day, hour, minute, second, msec = blue.os.GetTimeParts(now)
        date_time = '%d%.2d%.2d_%.2d%.2d%.2d' % (year,
         month,
         day,
         hour,
         minute,
         second)
        filename = '%s_%s' % (self.window_display_name, date_time)
        filename = SanitizeFilename(filename)
        post_fix = '_%s' % session.charid if session.charid else ''
        filename = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/logs/Chatlogs/%s%s.txt' % (filename, post_fix)
        try:
            self._logfile = blue.classes.CreateInstance('blue.ResFile')
            if not self._logfile.Open(filename, 0):
                self._logfile.Create(filename)
            self._logfile.Write(chatlog.encode('utf-16'))
        except Exception:
            self._logfile = None
            logger.exception('Failed to instantiate log file')
            sys.exc_clear()

    @threadutils.threaded
    def _write_to_log_file(self, sender_id, text, timestamp):
        if self._logfile is None or self._logfile.size <= 0:
            return
        text_without_tags = StripTags(text).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        try:
            if sender_id is None:
                who = localization.GetByLabel('UI/Common/Message')
            else:
                who = cfg.eveowners.Get(int(sender_id)).name
        except:
            who = sender_id

        line = '[%20s ] %s > %s\r\n' % (FmtDate(timestamp), who, text_without_tags)
        try:
            self._logfile.Write(line.encode('utf-16'))
        except:
            logger.error('Failed to write chat message to logfile', sender_id, text)
