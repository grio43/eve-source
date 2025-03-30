#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\window.py
import blue
from bannedwords.client import bannedwords
import gametime
from carbon.common.script.util.format import GetTimeParts
from inventorycommon.const import ownerSystem
import threadutils
import uthread2
import logging
from carbon.common.script.sys.serviceConst import ROLE_LEGIONEER, ROLE_CENTURION, ROLEMASK_ELEVATEDPLAYER, ROLE_GML
import carbonui
from carbonui import Align, PickState, AxisAlignment
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.control.window import Window
from carbonui.services.setting import UserSettingBool, UserSettingEnum
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.decorative.divider_line import DividerLine
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.text.settings import get_font_size_for_preset
from carbonui.fontconst import EVE_SMALL_FONTSIZE
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples
from carbonui.window.settings import GetRegisteredState
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.util.linkUtil import GetCharIDFromTextLink
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.comtool.filterSettings import ChatFilterSettings
from eve.common.script.sys.idCheckers import IsEvePlayerCharacter
import eveicon
from menu import MenuLabel
import localization
from chatutil.filter import CleanText, ShouldHightlightBlink
from chat.client.chat_settings import default_light_background_setting, default_message_mode_setting, default_compact_member_entries_setting, default_show_member_list_setting, default_font_size_setting, global_font_size_setting, elevated_chat_highlighting_setting, show_message_timestamp_setting, highlight_my_messages_setting, ApplyFontSizeGloballySetting, EffectiveFontSizeSetting, auto_collapse_messages, auto_collapse_message_lines
from chat.client.const import AVAILABLE_FONT_SIZES, MAX_MESSAGE_LENGTH, MAX_MESSAGES_IN_HISTORY, SLASH_EMOTE_STRING, SLASH_ME_STRING, CHAT_MESSAGE_MODE_LABEL_PATH
from chat.client.util import get_chat_default_height, get_chat_default_width, parse_pasted_text, parse_chat_message, truncate_chat_message, check_banned_message_in_new_player_channel
from chat.client.window_stack import ChatWindowStack
from chat.client.message_list_entry import ChatMessageListEntry
from chat.client.member_list_entry import ChatMemberListEntry, ChatMemberCompactListEntry
from chat.client.slash_command import handle_slash_command
from chat.client.hide_messages import open_hide_message_settings, has_hide_message_setting
logger = logging.getLogger('chat')

class BaseChatWindow(Window):
    default_caption = 'Chat'
    default_windowID = 'ChatWindow'
    default_stackID = 'ChatWindowStack'
    default_iconNum = 'res:/ui/Texture/WindowIcons/chatchannel.png'
    default_left = 16
    default_isKillable = False
    default_minSize = (120, 120)
    default_isCompact = True
    default_apply_content_padding = False

    @staticmethod
    def default_top():
        return uicore.desktop.height - ChatWindow.default_height() - 16

    @staticmethod
    def default_width():
        return get_chat_default_width()

    @staticmethod
    def default_height():
        return get_chat_default_height()

    @staticmethod
    def default_isLightBackground():
        return default_light_background_setting.get()

    @classmethod
    def should_open_stacked_window_as_minimized(cls, window_id):
        stack_id = cls.GetRegisteredOrDefaultStackID(windowID=window_id)
        return GetRegisteredState(stack_id, 'minimized')

    def GetStackClass(self):
        return ChatWindowStack

    def PostApplyAttributes(self, attributes):
        attributes['openMinimized'] = self.should_open_stacked_window_as_minimized(attributes.windowID) if attributes.get('check_open_minimized', False) else False
        Window.PostApplyAttributes(self, attributes)


class ChatWindow(BaseChatWindow):
    __notifyevents__ = ['OnPortraitCreated']
    _controller = None
    _member_list_entries = {}
    _pending_message_entries = {}
    _pending_portrait_reloads = set()
    _previous_inputs = ['']
    _previous_input_index = None
    _highlighted_text = ''
    _member_update_lock = None
    _message_update_lock = None

    def ApplyAttributes(self, attributes):
        self._controller = attributes.controller
        self._member_update_lock = uthread2.Semaphore()
        self._message_update_lock = uthread2.Semaphore()
        super(ChatWindow, self).ApplyAttributes(attributes)
        self._setup_settings()
        self._layout()
        self._register()
        uthread2.start_tasklet(self._update_member_count)
        uthread2.start_tasklet(self._setup_members_list, force_reload=True)
        uthread2.start_tasklet(self._reload_messages)

    def CloseByUser(self, *args):
        if self.closing and not self.killable:
            return
        super(ChatWindow, self).CloseByUser(*args)
        self._controller.close_by_user()

    def Close(self, *args, **kwargs):
        if self.closing:
            return
        self.unregister()
        if sm.GetService('focus').GetFocusChannel() == self:
            sm.GetService('focus').SetFocusChannel()
        self._controller = None
        super(ChatWindow, self).Close(*args, **kwargs)

    def _register(self):
        sm.RegisterNotify(self)
        self._controller.on_members_set.connect(self._on_members_set)
        self._controller.on_members_cleared.connect(self._on_members_cleared)
        self._controller.on_member_added.connect(self._on_member_added)
        self._controller.on_member_removed.connect(self._on_member_removed)
        self._controller.on_member_data_changed.connect(self._on_member_data_changed)
        self._controller.on_message_added.connect(self._on_message_added)
        self._controller.on_messages_cleared.connect(self._on_messages_cleared)
        self._controller.on_pending_message_removed.connect(self._on_pending_message_removed)

    def unregister(self):
        sm.UnregisterNotify(self)
        if self._controller:
            self._controller.on_members_set.disconnect(self._on_members_set)
            self._controller.on_members_cleared.disconnect(self._on_members_cleared)
            self._controller.on_member_added.disconnect(self._on_member_added)
            self._controller.on_member_removed.disconnect(self._on_member_removed)
            self._controller.on_member_data_changed.disconnect(self._on_member_data_changed)
            self._controller.on_message_added.disconnect(self._on_message_added)
            self._controller.on_messages_cleared.disconnect(self._on_messages_cleared)
            self._controller.on_pending_message_removed.disconnect(self._on_pending_message_removed)
        global_font_size_setting.on_change.disconnect(self._on_global_font_size_setting_changed)
        elevated_chat_highlighting_setting.on_change.disconnect(self._on_elevated_chat_highlighting_setting_changed)
        show_message_timestamp_setting.on_change.disconnect(self._on_show_message_timestamp_setting_changed)

    def _on_members_set(self):
        self._on_members_cleared()
        self._update_members()

    def _on_members_cleared(self):
        if not self._controller:
            return
        self._update_member_count()
        self._member_list_entries.clear()
        self._member_list_scroll.Clear()

    def _on_member_added(self, character_id):
        self._update_members()

    def _on_member_removed(self, character_id):
        self._update_members()

    @threadutils.threaded
    def _on_member_data_changed(self, character_id, data):
        entry = self._member_list_entries.get(character_id, None)
        if entry:
            entry.corpID = data.get('corporation_id', None)
            entry.allianceID = data.get('alliance_id', None)
            entry.warFactionID = data.get('war_faction_id', None)
            if entry.panel:
                entry.panel.UpdateRelationship(character_id)

    def _on_messages_cleared(self):
        with self._message_update_lock:
            if not self._controller:
                return
            self._pending_message_entries.clear()
            self._messages_scroll.Clear()

    def _on_message_added(self, sender_id, text, timestamp, color):
        if sender_id == session.charid:
            return
        with self._message_update_lock:
            if not self._controller:
                return
            self._construct_new_message_entry(sender_id, text, timestamp, color)

    def _on_pending_message_removed(self, message_id, was_delivered):
        if not self._controller:
            return
        message_entry = self._pending_message_entries.pop(message_id, None)
        if message_entry and not was_delivered:
            ChatMessageListEntry.MarkMessageUndelivered(message_entry)

    @threadutils.throttled(0.2)
    def _reload_messages(self):
        with self._message_update_lock:
            if not self._controller:
                return
            portion = self._messages_scroll.GetScrollProportion()
            self._messages_scroll.Clear()
            nodes = []
            for sender, text, timestamp, color in self._controller.messages:
                node = self._construct_message_entry(sender, text, timestamp, color)
                nodes.append(node)

            self._messages_scroll.AddNodes(-1, nodes)
            if portion:
                self._messages_scroll.ScrollToProportion(portion)

    def _construct_new_message_entry(self, sender_id, text, timestamp, color):
        message_nodes = self._messages_scroll.GetNodes()
        if message_nodes and len(message_nodes) >= MAX_MESSAGES_IN_HISTORY:
            self._messages_scroll.RemoveNodes([message_nodes[0]])
        entry = self._construct_message_entry(sender_id, text, timestamp, color)
        self._messages_scroll.AddNodes(-1, [entry])
        self._blink_channel_if_needed(sender_id, text)
        return entry

    def _construct_message_entry(self, sender_id, text, timestamp, color):
        try:
            character_id = int(sender_id)
        except:
            character_id = sender_id

        if elevated_chat_highlighting_setting.is_enabled():
            highlight_func = self._highlight_message
            collect_words_in_stack = True
        else:
            highlight_func = None
            collect_words_in_stack = False
        if auto_collapse_messages.get() and character_id and character_id != session.charid and IsEvePlayerCharacter(character_id):
            maxLines = int(auto_collapse_message_lines.get())
        else:
            maxLines = None
        node = ScrollEntryNode(decoClass=ChatMessageListEntry, text=text, timestamp=timestamp, fontsize=self._get_font_size(), letterspace=self._get_letter_space(), sender=sender_id, charid=character_id, mode=self._message_style_setting.get(), color=color, channelMenu=self._get_channel_context_menu, mouseOverWordCallback=highlight_func, collectWordsInStack=collect_words_in_stack, channelid=self._controller.channel_id, maxLines=maxLines, showExpander=False)
        return node

    @threadutils.throttled(0.2)
    def _reload_members(self):
        with self._member_update_lock:
            if not self._controller:
                return
            self._member_list_scroll.Clear()
            self._member_list_entries.clear()
            entries = []
            member_ids = self._controller.member_ids.copy()
            if member_ids:
                cfg.eveowners.Prime(member_ids)
            for character_id in member_ids:
                entry = self._construct_member_list_entry(character_id)
                if not entry:
                    continue
                entries.append(entry)

            sorted_entries = sorted(entries, key=lambda x: x.charIndex)
            self._member_list_scroll.AddNodes(-1, sorted_entries)

    @threadutils.throttled(0.2)
    def _update_members(self):
        self._update_member_count()
        with self._member_update_lock:
            if not self._controller:
                return
            current_rendered_ids = set(self._member_list_entries.keys())
            removed_character_ids = current_rendered_ids - self._controller.member_ids
            added_character_ids = self._controller.member_ids - current_rendered_ids
            self._remove_members(removed_character_ids)
            if added_character_ids:
                cfg.eveowners.Prime(added_character_ids)
                self._add_members(added_character_ids)

    def _remove_members(self, character_ids):
        entries = []
        for character_id in character_ids:
            entry = self._member_list_entries.pop(character_id, None)
            if entry:
                entries.append(entry)

        if entries:
            self._member_list_scroll.RemoveNodes(entries)

    def _add_members(self, character_ids):
        for character_id in character_ids:
            self._construct_new_member_list_entry(character_id)

    def _construct_new_member_list_entry(self, character_id):
        if self.destroyed or character_id in self._member_list_entries or character_id not in self._controller.member_ids:
            return
        entry = self._construct_member_list_entry(character_id)
        if not entry:
            return
        idx = GetIdxForUser_WithBinarySearch(self._member_list_scroll, entry.charIndex)
        self._member_list_scroll.AddNodes(idx, [entry], updateScroll=False)
        entry.positionFromTop = idx * entry.height
        self._update_member_list_scroll_position()

    def _construct_member_list_entry(self, character_id):
        owner_info = cfg.eveowners.GetIfExists(character_id)
        if not owner_info:
            logger.warning('_construct_member_list_entry not constructing for character_id %s as it was not in cfg.eveowners', character_id)
            return
        if self._compact_member_entries_setting.is_enabled():
            entry_type = ChatMemberCompactListEntry
        else:
            entry_type = ChatMemberListEntry
        member_data = self._controller.get_member_data(character_id)
        entry = GetFromClass(entry_type, {'channelID': self._controller.channel_id,
         'charID': character_id,
         'info': owner_info,
         'corpID': member_data.get('corporation_id', None),
         'allianceID': member_data.get('alliance_id', None),
         'warFactionID': member_data.get('war_faction_id', None),
         'showChatBubble': not self._compact_member_entries_setting.is_enabled(),
         'charIndex': owner_info.name.lower()})
        self._member_list_entries[character_id] = entry
        return entry

    @threadutils.throttled(0.2)
    def _update_member_count(self):
        if not self._controller:
            return
        member_count = self._controller.member_count
        if member_count > 1:
            self._num_members_label.text = str(member_count)
            self._num_members_container.display = True
            self.caption = u'{} [{}]'.format(self._controller.window_display_name, member_count)
        else:
            self._num_members_container.display = False
            self.caption = self._controller.window_display_name

    def _update_min_size(self):
        if self._member_list_container is None:
            return
        default_min_width, default_min_height = self.default_minSize
        user_list_width, _ = self.GetWindowSizeForContentSize(width=self._member_list_container.width)
        min_width = max(default_min_width, user_list_width)
        self.SetMinSize((min_width, default_min_height))

    def _handle_input_on_return(self):
        text = parse_chat_message(self._input_field.GetValue(html=0), truncate=False)
        if not text:
            return
        bannedwords.check_chat_character_allowed(session.charid)
        bannedwords.check_chat_words_allowed(text)
        self._input_field.SetValue('')
        if self._previous_inputs[-1] != text:
            self._previous_inputs.append(text)
        self._previous_input_index = None
        if text.startswith(SLASH_ME_STRING):
            text = text.replace(SLASH_ME_STRING, SLASH_EMOTE_STRING, 1)
        if text.startswith('/') and not (text.startswith(SLASH_EMOTE_STRING) or text == '/'):
            handle_slash_command(text, channel_controller=self._controller)
            return
        text = truncate_chat_message(text)
        if text == '':
            return
        if not self._controller.can_send_chat_message():
            return
        check_banned_message_in_new_player_channel(self._controller.category_id, text)
        timestamp = gametime.GetWallclockTime()
        color = self._controller.get_color_for_sender(session.charid)
        entry = self._construct_new_message_entry(session.charid, text, timestamp, color)
        message_id = self._controller.send_chat_message(text)
        if message_id:
            self._pending_message_entries[message_id] = entry

    @threadutils.throttled(0.5)
    def _update_member_list_scroll_position(self):
        if not self._controller:
            return
        width, _ = self._member_list_scroll.sr.clipper.GetAbsoluteSize()
        with self._member_list_scroll.KillUpdateThreadAndBlock():
            self._member_list_scroll.UpdateNodesWidthAndPosition(width)
            self._member_list_scroll.UpdatePosition(fromWhere='AddNodes')

    def _setup_settings(self):
        self._message_style_setting = UserSettingEnum(settings_key='%s_mode' % self.name, default_value=lambda : default_message_mode_setting.get(), options=default_message_mode_setting.options)
        self._font_size_setting = UserSettingEnum(settings_key='chatfontsize_%s' % self.name, default_value=lambda : default_font_size_setting.get(), options=AVAILABLE_FONT_SIZES)
        self._apply_font_size_globally_setting = ApplyFontSizeGloballySetting(font_size_setting=self._font_size_setting)
        self._effective_font_size_setting = EffectiveFontSizeSetting(font_size_setting=self._font_size_setting)
        self._chat_notifications_enabled_setting = UserSettingBool(settings_key='chatWindowBlink_%s' % self.name, default_value=True)
        self._show_member_list_setting = UserSettingBool(settings_key='%s_usermode' % self.name, default_value=lambda : default_show_member_list_setting.get())
        self._compact_member_entries_setting = UserSettingBool(settings_key='chatCondensedUserList_%s' % self.name, default_value=lambda : default_compact_member_entries_setting.get())
        self._message_style_setting.on_change.connect(self._on_message_style_setting_changed)
        self._font_size_setting.on_change.connect(self._on_font_size_setting_changed)
        self._apply_font_size_globally_setting.on_change.connect(self._on_apply_font_size_globally_setting_changed)
        self._show_member_list_setting.on_change.connect(self._on_show_member_list_setting_changed)
        self._compact_member_entries_setting.on_change.connect(self._on_compact_member_entries_setting_changed)
        global_font_size_setting.on_change.connect(self._on_global_font_size_setting_changed)
        elevated_chat_highlighting_setting.on_change.connect(self._on_elevated_chat_highlighting_setting_changed)
        show_message_timestamp_setting.on_change.connect(self._on_show_message_timestamp_setting_changed)

    def _layout(self):
        self._construct_input()
        self._construct_user_list()
        self._construct_message_area()
        self._update_min_size()
        self.killable = self._controller.is_closable
        if elevated_chat_highlighting_setting.is_enabled():
            self._input_field.OnKeyUp = self._check_turn_highlight_off
            self._messages_scroll.OnKeyUp = self._check_turn_highlight_off

    def _construct_input(self):
        input_cont = ContainerAutoSize(parent=self.content, align=Align.TOBOTTOM, alignMode=Align.TOBOTTOM, padTop=-3)
        bottom_divider = Divider(name='bottom_divider', parent=input_cont, align=Align.TOTOP_NOPUSH, pickState=PickState.ON, height=8)
        self._input_field = EditPlainText(parent=input_cont, align=Align.TOBOTTOM, height=settings.user.ui.Get('chatinputsize_%s' % self.name, 64), innerPadding=(8, 8, 8, 8), padding=(-1, 3, -1, -1), pushContent=True, maxLength=MAX_MESSAGE_LENGTH)
        self._input_field.ValidatePaste = parse_pasted_text
        self._input_field.OnReturn = self._handle_input_on_return
        self._input_field.CtrlUp = self._handle_input_control_up
        self._input_field.CtrlDown = self._handle_input_control_down
        self._input_field.RegisterFocus = self._RegisterFocus
        bottom_divider.Startup(self._input_field, 'height', 'y', 30, 96)
        bottom_divider.OnSizeChanged = self._on_input_size_changed

    def _construct_user_list(self):
        self._member_list_container = Container(parent=self.content, align=Align.TORIGHT, width=settings.user.ui.Get('%s_userlistwidth' % self.name, 128), clipChildren=True)
        DividerLine(parent=self._member_list_container, align=Align.TOLEFT_NOPUSH)
        self._user_list_underlay = Fill(bgParent=self._member_list_container, align=Align.TOALL, padLeft=1, color=(1.0, 1.0, 1.0, 0.05))
        divider = Divider(name='user_list_divider', parent=self._member_list_container, align=Align.TOLEFT_NOPUSH, pickState=PickState.ON, width=8, cross_axis_alignment=AxisAlignment.START)
        divider.Startup(victim=self._member_list_container, attribute='width', xory='x', minValue=50, maxValue=200)
        divider.OnSizeChanged = self._user_list_end_scale
        self._num_members_container = Container(name='num_members_container', parent=self._member_list_container, align=Align.TOTOP, pickState=PickState.ON, height=16, padding=(8, 8, 8, 0), hint=self._controller.member_count_tooltip)
        self._num_members_container.display = False
        Sprite(name='num_members_sprite', parent=self._num_members_container, align=Align.CENTERLEFT, pickState=carbonui.PickState.OFF, width=16, height=16, texturePath=eveicon.person, color=carbonui.TextColor.NORMAL)
        self._num_members_label = EveLabelSmall(name='num_members_label', parent=self._num_members_container, align=Align.CENTERLEFT, left=20, text='')
        self._member_list_scroll = BasicDynamicScroll(name='user_list_scroll', parent=self._member_list_container, align=Align.TOALL, padding=(8, 8, 8, 0), entry_spacing=self._get_user_list_entry_spacing(), pushContent=True)
        self._member_list_scroll.isCondensed = self._compact_member_entries_setting.is_enabled()
        self._member_list_scroll.GetContentContainer().OnDropData = self._on_drop_to_user_list

    def _construct_message_area(self):
        self._messages_scroll = BasicDynamicScroll(parent=self.content, align=Align.TOALL, innerPadding=(8, 8, 8, 8), entry_spacing=4, pushContent=False, stickToBottom=True)
        self._messages_scroll.sr.content.GetMenu = self._get_channel_context_menu
        self._messages_scroll.Load(contentList=[], fixedEntryHeight=18)

    def _setup_members_list(self, force_reload = False):
        if not self._controller:
            return
        if not self._show_member_list_setting.is_enabled():
            self._member_list_container.display = False
        else:
            minW = 50
            maxW = 200
            self._member_list_container.width = min(maxW, max(minW, self._member_list_container.width))
            self._member_list_container.display = True
            condensed = self._compact_member_entries_setting.is_enabled()
            if force_reload or condensed != getattr(self._member_list_scroll, 'isCondensed', False):
                self._reload_members()

    def _on_message_style_setting_changed(self, value):
        if not self._controller:
            return
        self._reload_messages()
        uicore.registry.SetFocus(self)

    def _on_font_size_setting_changed(self, value):
        if self._apply_font_size_globally_setting.is_enabled():
            global_font_size_setting.set(self._font_size_setting.get())
        else:
            self._update_font_size()

    def _on_apply_font_size_globally_setting_changed(self, value):
        if self._apply_font_size_globally_setting.is_enabled():
            global_font_size_setting.set(self._font_size_setting.get())

    def _on_global_font_size_setting_changed(self, value):
        self._update_font_size()

    def _on_elevated_chat_highlighting_setting_changed(self, value):
        if elevated_chat_highlighting_setting.is_enabled():
            if self._input_field and not self._input_field.destroyed:
                self._input_field.OnKeyUp = self._check_turn_highlight_off
            if self._messages_scroll and not self._messages_scroll.destroyed:
                self._messages_scroll.OnKeyUp = self._check_turn_highlight_off
        else:
            if self._input_field and not self._input_field.destroyed:
                self._input_field.OnKeyUp = None
            if self._messages_scroll and not self._messages_scroll.destroyed:
                self._messages_scroll.OnKeyUp = None
        self._turn_message_highlight_off()
        self._reload_messages()

    def _on_show_member_list_setting_changed(self, value):
        self._setup_members_list()

    def _on_compact_member_entries_setting_changed(self, value):
        is_compact = self._compact_member_entries_setting.is_enabled()
        if self._show_member_list_setting.is_enabled():
            self._member_list_scroll.entry_spacing = self._get_user_list_entry_spacing()
            self._reload_members()
        self._member_list_scroll.isCondensed = is_compact if self._member_list_scroll.display else -1

    def _on_show_message_timestamp_setting_changed(self, value):
        self._reload_messages()

    def _on_input_size_changed(self):
        settings.user.ui.Set('chatinputsize_%s' % self.name, self._input_field.height)

    def _update_font_size(self):
        self._reload_messages()
        self._input_field.SetDefaultFontSize(self._get_font_size())

    def _get_font_size(self):
        font_size = global_font_size_setting.get()
        if font_size is None:
            font_size = self._font_size_setting.get()
        return font_size

    def _get_letter_space(self):
        font_size = self._get_font_size()
        small_font_size = get_font_size_for_preset(EVE_SMALL_FONTSIZE)
        if font_size <= small_font_size:
            return 1
        else:
            return 0

    def _get_user_list_entry_spacing(self):
        if self._compact_member_entries_setting.is_enabled():
            return 1
        else:
            return 4

    def _check_turn_highlight_off(self, *args, **kwargs):
        if elevated_chat_highlighting_setting.is_enabled():
            self._turn_message_highlight_off()

    def _highlight_message(self, findText = '', *args):
        if not self._is_highlighting():
            return
        if len(findText.strip().replace('(', '').replace(')', '')) < 2:
            return
        if self._highlighted_text != findText:
            self._turn_message_highlight_off()
        self._highlighted_text = findText
        nodes = self._messages_scroll.GetNodes()
        for eachNode in nodes:
            if eachNode.panel:
                eachNode.panel.LoadHighlightedText(findText)

    def _turn_message_highlight_off(self):
        _highlighted_text = getattr(self, '_highlighted_text', '')
        if not _highlighted_text:
            return
        for eachNode in self._messages_scroll.GetNodes():
            if eachNode.panel:
                eachNode.panel.RemoveHighlightedText()

        self._highlighted_text = None

    def _is_highlighting(self, *args):
        return elevated_chat_highlighting_setting.is_enabled() and uicore.uilib.Key(carbonui.uiconst.VK_CONTROL)

    def _blink_channel_if_needed(self, sender_id, text):
        if sender_id in (session.charid, ownerSystem):
            return
        blink_enabled = self._chat_notifications_enabled_setting.is_enabled()
        if blink_enabled or ShouldHightlightBlink(text):
            self.Blink()
            if self.state == carbonui.uiconst.UI_HIDDEN or self.IsMinimized():
                self.SetBlinking()

    def _get_channel_context_menu(self, *args):
        m = [(MenuLabel('UI/Common/CopyAll'), self._copy_all_messages)]
        return m

    def _copy_all_messages(self):
        t = ''
        for node in self._messages_scroll.GetNodes():
            timestr = ''
            if show_message_timestamp_setting.is_enabled():
                year, month, wd, day, hour, min, sec, ms = GetTimeParts(node.timestamp)
                timestr = '[%02d:%02d:%02d] ' % (hour, min, sec)
            who = node.sender
            try:
                who = cfg.eveowners.Get(who).name
            except ValueError:
                pass

            text = node.text.replace('&gt;', '>').replace('&amp;', '&')
            text = CleanText(text)
            t += '%s%s > %s\r\n' % (timestr, who, text)

        blue.pyos.SetClipboardData(t)

    def _handle_input_control_down(self, editctrl):
        self._browse_inputs(1)

    def _handle_input_control_up(self, editctrl):
        self._browse_inputs(-1)

    def _browse_inputs(self, updown):
        if self._previous_input_index is None:
            self._previous_input_index = len(self._previous_inputs) - 1
        else:
            self._previous_input_index += updown
        if self._previous_input_index < 0:
            self._previous_input_index = len(self._previous_inputs) - 1
        elif self._previous_input_index >= len(self._previous_inputs):
            self._previous_input_index = 0
        self._input_field.SetValue(self._previous_inputs[self._previous_input_index], cursorPos=-1)

    def _user_list_end_scale(self, *args):
        settings.user.ui.Set('%s_userlistwidth' % self.name, self._member_list_container.width)
        self._update_min_size()

    def _on_drop_to_user_list(self, dragObj, nodes):
        for node in nodes[:5]:
            character_id = GetCharIDFromTextLink(node)
            if not character_id:
                guid = getattr(node, '__guid__', None)
                if guid not in AllUserEntries():
                    return
                character_id = node.charID
            if self._controller.can_invite_character(character_id):
                self._controller.invite_character(character_id)

    def _RegisterFocus(self, *args, **kwargs):
        sm.GetService('focus').SetFocusChannel(self)

    def SetCharFocus(self, char):
        uicore.registry.SetFocus(self._input_field)
        uicore.layer.menu.Flush()
        if char is not None:
            self._input_field.OnChar(char, 0)

    def OnTabSelect(self):
        uicore.registry.SetFocus(self._input_field)
        self._reload_pending_portaits()

    def OnPortraitCreated(self, charID, _size):
        if self.destroyed or self._messages_scroll is None:
            return
        self._pending_portrait_reloads.add(charID)
        if not self.display:
            return
        self._reload_pending_portaits()

    def _reload_pending_portaits(self):
        if not self._pending_portrait_reloads:
            return
        if self._show_member_list_setting.is_enabled():
            for character_id in self._pending_portrait_reloads:
                entry = self._member_list_entries.get(character_id, None)
                if entry and entry.panel and not entry.panel.picloaded:
                    entry.panel.LoadPortrait(orderIfMissing=False)

        for entry in self._messages_scroll.GetNodes():
            if not entry.panel or not entry.panel.display:
                continue
            if entry.charid in self._pending_portrait_reloads and not entry.panel.picloaded:
                entry.panel.LoadPortrait(orderIfMissing=False)

        self._pending_portrait_reloads.clear()

    def OnSetActive_(self, *args):
        if self._user_list_underlay is not None:
            animations.FadeTo(self._user_list_underlay, startVal=self._user_list_underlay.opacity, endVal=0.05, duration=0.1)

    def OnSetInactive(self, *args):
        super(ChatWindow, self).OnSetInactive()
        if self._user_list_underlay is not None:
            animations.FadeOut(self._user_list_underlay, duration=0.3)

    def OnMouseUp(self, _):
        self.StackSelf()

    @threadutils.threaded
    def StackSelf(self):
        if self.stacked:
            self.stack.Check()
        elif self.FindWindowToStackTo():
            pass
        else:
            self._ConstructStack([(self, 1)], [])

    def SetBlinking(self):
        super(ChatWindow, self).SetBlinking()
        sm.ScatterEvent('OnChatWindowStartBlinking', self)

    def SetNotBlinking(self):
        super(ChatWindow, self).SetNotBlinking()
        sm.ScatterEvent('OnChatWindowStopBlinking', self)

    def GetMenu(self, *args):
        menu = MenuData()
        menu.AddCaption(self.caption)
        menu.AddSeparator()
        self._add_channel_menu(menu)
        tab_menu = CreateMenuDataFromRawTuples(super(ChatWindow, self).GetMenu(*args))
        if tab_menu is not None and tab_menu.GetEntries():
            menu += tab_menu
            menu.AddSeparator()
        return menu

    def GetMenuMoreOptions(self):
        menu = super(ChatWindow, self).GetMenuMoreOptions()
        self._add_channel_menu(menu)
        return menu

    def _add_channel_menu(self, menu):
        gm_options = MenuData()
        if session.role & ROLE_GML:
            gm_options.AddEntry(text='channel id: ' + self._controller.channel_id, func=lambda : blue.pyos.SetClipboardData(self._controller.channel_id))
            gm_options.AddEntry(text='category id: ' + self._controller.category_id, func=lambda : blue.pyos.SetClipboardData(self._controller.category_id))
            gm_options.AddEntry(text='window id: ' + self._controller.window_id, func=lambda : blue.pyos.SetClipboardData(self._controller.window_id))
            gm_options.AddSeparator()
            gm_options.AddEntry(text='Reload Members', func=self._reload_members)
            gm_options.AddEntry(text='Reload Messages', func=self._reload_messages)
            gm_options.AddEntry(text='Copy Members Data', func=self._qa_copy_member_data)
        if gm_options.GetEntries():
            menu.AddEntry(text='GM / WM Extras', subMenuData=gm_options)
        elevated_role_mask = ROLE_CENTURION | ROLE_LEGIONEER | ROLEMASK_ELEVATEDPLAYER
        if session.role & elevated_role_mask:
            menu.AddCheckbox(text='Special chat highlighting', setting=elevated_chat_highlighting_setting)
            menu.AddSeparator()
        menu.AddLabel(localization.GetByLabel('UI/Chat/ChannelSettingsSection'))
        member_list_options = MenuData()
        member_list_options.AddCheckbox(text=localization.GetByLabel('UI/Chat/ShowMemberList'), setting=self._show_member_list_setting)
        member_list_options.AddSeparator()
        member_list_options.AddCheckbox(text=localization.GetByLabel('UI/Chat/ShowCompactMemberList'), setting=self._compact_member_entries_setting)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/MemberList'), texturePath=eveicon.people, subMenuData=member_list_options)
        font_size_menu = MenuData()
        font_size_menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/UseFontSizeInAllChannels'), setting=self._apply_font_size_globally_setting)
        font_size_menu.AddSeparator()
        for font_size in self._effective_font_size_setting.options:
            font_size_menu.AddRadioButton(text=str(font_size), value=font_size, setting=self._effective_font_size_setting)

        menu.AddEntry(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/FontSize'), texturePath=eveicon.font_size, subMenuData=font_size_menu)
        message_style_menu = MenuData()
        for mode in self._message_style_setting.options:
            message_style_menu.AddRadioButton(text=localization.GetByLabel(CHAT_MESSAGE_MODE_LABEL_PATH[mode]), value=mode, setting=self._message_style_setting)

        menu.AddEntry(text=localization.GetByLabel('UI/Chat/MessagePortraits'), texturePath=eveicon.person, subMenuData=message_style_menu)
        if has_hide_message_setting(self._controller.category_id):
            menu.AddEntry(text=localization.GetByLabel('UI/Chat/MessageFilterContextMenu'), texturePath=eveicon.filter, func=self._open_hide_message_settings)
        menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/BlinkOnNewActivity'), setting=self._chat_notifications_enabled_setting)
        if self._controller.motd:
            menu.AddEntry(text=localization.GetByLabel('UI/Chat/ReloadChannelMOTD'), func=self._show_motd)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/ClearAllContent'), func=self._controller.clear_messages)
        menu.AddSeparator()
        menu.AddLabel(localization.GetByLabel('UI/Chat/GlobalSettingsSection'))
        autoCollapseMenu = MenuData()
        autoCollapseMenu.AddCheckbox(localization.GetByLabel('UI/Chat/AutoCollapseMessagesEnabled'), hint=localization.GetByLabel('UI/Chat/AutoCollapseMessagesHint'), setting=auto_collapse_messages)
        autoCollapseMenu.AddSlider(localization.GetByLabel('UI/Chat/AutoCollapseMessagesLines'), setting=auto_collapse_message_lines, isInteger=True)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/AutoCollapseMessages'), hint=localization.GetByLabel('UI/Chat/AutoCollapseMessagesHint'), texturePath=eveicon.collapse, subMenuData=autoCollapseMenu)
        menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/HighlightMyMessages'), setting=highlight_my_messages_setting)
        menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/ShowTimestamp'), setting=show_message_timestamp_setting)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/ConfigureWordFiltersAndHighlights'), func=self._set_word_and_highlight_filters)
        return menu

    def _set_word_and_highlight_filters(self):
        ChatFilterSettings.Open()

    def _open_hide_message_settings(self):
        self._controller.open_hide_message_settings()

    def _show_motd(self):
        motd = self._controller.motd
        if motd:
            message = localization.GetByLabel('UI/Chat/ChannelMotd', motd=motd)
            self._controller.add_game_message(text=message, sender_id=ownerSystem)

    def _qa_copy_member_data(self):
        import json
        data = {member_id:self._controller.get_member_data(member_id) for member_id in self._controller.member_ids}
        blue.pyos.SetClipboardData(json.dumps(data, indent=2, sort_keys=True))


def GetIdxForUser_WithBinarySearch(member_list_scroll, entry_name):
    a = member_list_scroll.GetNodes()
    x = entry_name
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid].charIndex:
            hi = mid
        else:
            lo = mid + 1

    return lo
