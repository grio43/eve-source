#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\chat_service.py
import launchdarkly
from carbon.common.script.sys.service import Service
import carbonui.const as uiconst
import uthread2
from carbon.common.script.util.format import FmtDate
from eveexceptions import UserError
import signals
from chat.common.const import ChatCategory, LOCAL_CHAT_FEATURE_FLAG_KEY, LOCAL_CHAT_FEATURE_FLAG_FALLBACK
from chat.common.util import get_classification_from_role
from chat.client.window import ChatWindow
from chat.client.local_chat.channel_controller import LocalChatChannelController
from chat.client.local_chat.validators.paste import DefaultValidator
_category_channel_class = {ChatCategory.LOCAL: LocalChatChannelController}

class ChatSvc(Service):
    __guid__ = 'svc.chat'
    __displayname__ = 'Chat Service'
    __notifyevents__ = ['OnSessionChanged', 'ProcessSessionReset']
    __dependencies__ = []
    __startupdependencies__ = ['publicGatewaySvc']

    def __init__(self):
        super(ChatSvc, self).__init__()
        self._members_info = {}
        self.on_member_data_changed = signals.Signal('on_member_info_changed')
        self.on_member_data_changed_live_update = signals.Signal('on_member_info_changed_live_update')
        self._reported_spammer_ids = set()
        self._chat_channels = {}
        self._is_local_chat_service_enabled = None
        self._load_local_tasklet = None
        self._paste_validators = {}
        self._default_paste_validator = DefaultValidator()

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        ld_client = launchdarkly.get_client()
        ld_client.notify_flag(LOCAL_CHAT_FEATURE_FLAG_KEY, LOCAL_CHAT_FEATURE_FLAG_FALLBACK, self._on_local_chat_service_flag_changed)

    def OnSessionChanged(self, is_remote, session, change):
        if 'charid' in change or 'corpid' in change or 'allianceid' in change or 'warfactionid' in change:
            if 'charid' in change:
                if self._is_local_chat_service_enabled and not self._load_local_tasklet:
                    self._load_local_tasklet = uthread2.start_tasklet(self._load_local_channel)
            self._update_self_from_session()

    def ProcessSessionReset(self):
        self.flush()

    def flush(self):
        self._members_info.clear()
        if self._load_local_tasklet:
            self._load_local_tasklet.kill()
            self._load_local_tasklet = None
        for channel_id in self._chat_channels.keys():
            self.close_channel(channel_id)

    def add_paste_validator(self, validator):
        if validator.identifier not in self._paste_validators:
            self._paste_validators[validator.identifier] = validator

    def remove_paste_validator(self, validator):
        if validator.identifier in self._paste_validators:
            self._paste_validators.pop(validator.identifier)

    def validate_paste(self, text):
        for validator in self._paste_validators.values():
            result = validator.validate(text)
            if result:
                return result

        return self._default_paste_validator.validate(text)

    @property
    def is_local_chat_service_enabled(self):
        return self._is_local_chat_service_enabled

    def _on_local_chat_service_flag_changed(self, ld_client, flag_key, flag_fallback, flag_deleted):
        is_enabled = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)
        if self._is_local_chat_service_enabled == is_enabled:
            return
        self._is_local_chat_service_enabled = is_enabled
        if not self._load_local_tasklet:
            self._load_local_tasklet = uthread2.start_tasklet(self._load_local_channel)

    def get_member_info(self, member_id):
        return self._members_info.get(member_id, {})

    def has_member_info(self, member_id):
        return member_id in self._members_info

    def update_members_info(self, members, signal = False):
        for member_id, member_info in members.iteritems():
            self._members_info[member_id] = member_info
            if signal:
                self.on_member_data_changed(member_id, member_info)

    def add_game_message(self, text, sender_id = None):
        if self.is_local_chat_service_enabled:
            channel = self.get_channel(ChatCategory.LOCAL)
            if channel:
                channel.add_game_message(text, sender_id)
        else:
            sm.GetService('XmppChat').LocalEchoAll(text, sender_id)

    def get_channel(self, channel_id):
        return self._chat_channels.get(channel_id, None)

    def join_channel(self, channel_id, category_id, open = True):
        if channel_id not in self._chat_channels:
            channel_class = _category_channel_class.get(category_id, None)
            if channel_class:
                self._chat_channels[channel_id] = channel_class(channel_id=channel_id, category_id=category_id)
        if open:
            self.open_channel_window(channel_id)

    def close_channel(self, channel_id):
        channel = self._chat_channels.pop(channel_id, None)
        if channel:
            channel.close()
            try:
                window = ChatWindow.GetIfOpen(windowID=channel.window_id)
                if window:
                    window.Close()
            except:
                pass

    def open_channel_window(self, channel_id):
        channel = self.get_channel(channel_id)
        if not channel:
            return
        ChatWindow(windowID=channel.window_id, caption=channel.window_display_name, controller=channel, check_open_minimized=True)

    def invite_to_private_chat(self, character_id):
        sm.GetService('XmppChat').Invite(character_id)

    def is_blocked_character(self, character_id, character_info):
        address_book = sm.GetService('addressbook')
        try:
            return address_book.IsBlocked(character_id) or address_book.IsBlocked(character_info.get('corporation_id')) or address_book.IsBlocked(character_info.get('alliance_id'))
        except:
            return False

    def has_reported_spammers(self):
        return bool(self._reported_spammer_ids)

    def clear_reported_spammers(self):
        self._reported_spammer_ids.clear()

    def is_reported_spammer(self, character_id):
        return character_id in self._reported_spammer_ids

    def report_isk_spammer(self, character_id, channel_id):
        if eve.Message('ConfirmReportISKSpammer', {'name': cfg.eveowners.Get(character_id).name}, uiconst.YESNO) != uiconst.ID_YES:
            return
        if character_id == session.charid:
            raise UserError('ReportISKSpammerCannotReportYourself')
        if self.is_reported_spammer(character_id):
            return
        self._reported_spammer_ids.add(character_id)
        all_messages = []
        channel = self.get_channel(channel_id)
        if channel:
            all_messages = list(channel.messages)
        else:
            xmpp_window = sm.GetService('XmppChat').GetGroupChatWindow(channel_id)
            if xmpp_window:
                all_messages = list(xmpp_window.messages)
        spam_entries = []
        character_info = cfg.eveowners.GetIfExists(character_id)
        character_name = character_info.name if character_info else character_id
        for sender_id, text, timestamp, color in reversed(all_messages):
            if sender_id != character_id:
                continue
            spam_entries.append('[%s] %s > %s' % (FmtDate(timestamp, 'nl'), character_name, text))
            if len(spam_entries) >= 10:
                break

        sm.RemoteSvc('userSvc').ReportISKSpammer(character_id, channel_id, spam_entries)

    def get_player_count_in_local(self):
        result = 0
        if self.is_local_chat_service_enabled:
            channel = self.get_channel(ChatCategory.LOCAL)
            if channel:
                result = channel.member_count
        else:
            result = sm.GetService('XmppChat').GetNumPilotsInSystem()
        return result or 0

    def _load_local_channel(self):
        uthread2.sleep(0.5)
        self._load_local_tasklet = None
        channel_id = ChatCategory.LOCAL
        if self.is_local_chat_service_enabled:
            sm.GetService('XmppChat').UpdateLocalChatMigrated(self.is_local_chat_service_enabled)
            self.join_channel(category_id=channel_id, channel_id=channel_id, open=False)
        else:
            self.close_channel(channel_id)
            sm.GetService('XmppChat').UpdateLocalChatMigrated(self.is_local_chat_service_enabled)

    def _update_self_from_session(self):
        if session.charid:
            self._members_info[session.charid] = {'corporation_id': session.corpid,
             'alliance_id': session.allianceid,
             'war_faction_id': session.warfactionid,
             'classification': get_classification_from_role(session.role)}

    def mute_player(self, character_id, channel_id, duration_seconds, reason):
        if channel_id == 'local':
            print 'GAGGING FOR LOCAL'
            self.get_channel(channel_id).mute_player(character_id, duration_seconds, reason)
        else:
            sm.ProxySvc('XmppChatMgr').GMMute(channel_id, character_id, reason, duration_seconds)

    def unmute_player(self, character_id, channel_id):
        if channel_id == 'local':
            raise NotImplementedError('Unmute not implemented for local chat')
        else:
            sm.ProxySvc('XmppChatMgr').GMUnmute(channel_id, character_id)
