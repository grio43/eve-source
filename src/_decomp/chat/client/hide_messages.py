#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\hide_messages.py
import re
import localization
import carbonui
from carbonui.control.button import Button
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.primitives.container import Container
from carbon.common.script.util.commonutils import StripTags
from chat.common.const import ChatCategory, CATEGORY_LABEL_PATH
SPLITTER = ','
MAX_LENGTH = 500
HIDE_MESSAGE_PATTERNS = {}
NON_FILTERABLE_CATEGORIES = (ChatCategory.PRIVATE, ChatCategory.FLEET)
HAS_PER_CHANNEL_SETTING = (ChatCategory.LOCAL, ChatCategory.SYSTEM, ChatCategory.PLAYER)

def open_hide_message_settings(category_id, channel_id, channel_name):
    window = HideMessageSettingWindow.GetIfOpen()
    if window:
        window.Close()
    if category_id in NON_FILTERABLE_CATEGORIES:
        return
    HideMessageSettingWindow.Open(category_id=category_id, channel_id=channel_id, channel_name=channel_name)


def has_hide_message_setting(category_id):
    return category_id not in NON_FILTERABLE_CATEGORIES


def get_hide_message_pattern(channel_id, category_id):
    if settings.user.ui.HasKey(_get_setting_key(channel_id)):
        return _get_hide_message_pattern(channel_id)
    if settings.user.ui.HasKey(_get_setting_key(category_id)):
        return _get_hide_message_pattern(category_id)


def _hide_message_setting_changed(channel_id, category_id):
    global HIDE_MESSAGE_PATTERNS
    if channel_id:
        HIDE_MESSAGE_PATTERNS.pop(channel_id, None)
    if category_id:
        HIDE_MESSAGE_PATTERNS.pop(category_id, None)


def _get_hide_message_pattern(key):
    if key not in HIDE_MESSAGE_PATTERNS:
        channel_hide_word_list = settings.user.ui.Get(_get_setting_key(key), None)
        if channel_hide_word_list:
            text = '|'.join((re.escape(word) for word in channel_hide_word_list))
            pattern = re.compile(text, re.IGNORECASE)
        else:
            pattern = None
        HIDE_MESSAGE_PATTERNS[key] = pattern
    return HIDE_MESSAGE_PATTERNS[key]


def _get_setting_key(key):
    return 'chat_hide_message_{}'.format(key)


class HideMessageSettingWindow(Window):
    default_width = 380
    default_height = 480
    default_isCompact = True
    default_minSize = (default_width, default_height)
    default_windowID = 'HideMessageSettingWindow'
    default_captionLabelPath = 'UI/Chat/MessageFilterWindowTitle'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self._channel_id = attributes.channel_id
        self._category_id = attributes.category_id
        if self._category_id not in HAS_PER_CHANNEL_SETTING or self._category_id == self._channel_id:
            self._channel_id = None
        btnGroup = ButtonGroup(parent=self.sr.main, align=carbonui.Align.TOBOTTOM, padTop=16)
        Button(parent=btnGroup, label=localization.GetByLabel('UI/Common/Buttons/Save'), func=self._save)
        Button(parent=btnGroup, label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self._cancel)
        if self._channel_id:
            channel_container = Container(name='channel_container', parent=self.sr.main, align=carbonui.Align.TOBOTTOM_PROP, height=0.5)
            carbonui.TextHeader(parent=channel_container, align=carbonui.Align.TOTOP, text=localization.GetByLabel('UI/Chat/MessageFilterChannelSection', channel_name=attributes.channel_name), padTop=16)
            is_overriding = settings.user.ui.HasKey(_get_setting_key(self._channel_id))
            self._override_checkbox = Checkbox(parent=channel_container, align=carbonui.Align.TOTOP, text=localization.GetByLabel('UI/Chat/MessageFilterChannelOverride'), hint=localization.GetByLabel('UI/Chat/MessageFilterChannelOverrideHint'), checked=is_overriding, callback=self._override_checked, padBottom=4, padTop=4)
            channel_hide_word_list = settings.user.ui.Get(_get_setting_key(self._channel_id), [])
            channel_hide_words = SPLITTER.join(channel_hide_word_list)
            self._channel_field = EditPlainText(name='channel_field', parent=channel_container, align=carbonui.Align.TOALL, ignoreTags=True, setvalue=channel_hide_words, hintText=localization.GetByLabel('UI/Chat/MessageFilterDetails'), maxLength=MAX_LENGTH)
            if not is_overriding:
                self._channel_field.Disable()
        category_container = Container(parent=self.sr.main, name='category_container', align=carbonui.Align.TOALL)
        category_name = localization.GetByLabel(CATEGORY_LABEL_PATH.get(self._category_id, ''))
        carbonui.TextHeader(parent=category_container, align=carbonui.Align.TOTOP, text=localization.GetByLabel('UI/Chat/MessageFilterCategorySection', category_name=category_name))
        category_hide_word_list = settings.user.ui.Get(_get_setting_key(self._category_id), [])
        category_hide_words = SPLITTER.join(category_hide_word_list)
        self._category_field = EditPlainText(name='category_field', parent=category_container, align=carbonui.Align.TOALL, ignoreTags=True, setvalue=category_hide_words, hintText=localization.GetByLabel('UI/Chat/MessageFilterDetails'), maxLength=MAX_LENGTH)

    def _override_checked(self, checkbox):
        if checkbox.GetValue():
            self._channel_field.Enable()
        else:
            self._channel_field.Disable()

    def _save(self, *args, **kwargs):

        def GetTextParts(editField):
            text = editField.GetValue()
            text = StripTags(text)
            textParts = text.strip(SPLITTER).split(SPLITTER)
            textParts = filter(None, (word.strip() for word in textParts))
            return textParts

        if self._channel_id:
            override = self._override_checkbox.GetValue()
            if override:
                channel_hide_words = GetTextParts(self._channel_field)
                settings.user.ui.Set(_get_setting_key(self._channel_id), channel_hide_words)
            else:
                settings.user.ui.Delete(_get_setting_key(self._channel_id))
        category_hide_words = GetTextParts(self._category_field)
        settings.user.ui.Set(_get_setting_key(self._category_id), category_hide_words)
        _hide_message_setting_changed(self._channel_id, self._category_id)
        self.CloseByUser()

    def _cancel(self, *args, **kwargs):
        self.CloseByUser()
