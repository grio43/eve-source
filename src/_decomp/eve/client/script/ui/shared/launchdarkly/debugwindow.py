#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\launchdarkly\debugwindow.py
import uthread2
from carbonui.control.window import Window
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.button import Button
from carbonui import TextColor
import carbonui.const as uiconst
import launchdarkly
_headers = ['flag', 'callbacks', 'variation']
_initialized_label_text = 'SDK Initialized: {}'
_ld_user_key_label_text = 'LD User Key: {}'
_user_attributes_label_text = 'User Attributes: {}'
_last_log_label_text = 'Last Log: {}'

class LaunchDarklyDebugWindow(Window):
    __guid__ = 'LaunchDarklyDebugWindow'
    default_width = 600
    default_height = 600
    default_windowID = 'launchDarklyDebugWindow'
    default_minSize = [default_width, default_height]
    refresh_delay_seconds = 1.0

    def refresh(self):
        while not self.destroyed:
            self.update_labels()
            self.update_variations()
            uthread2.Sleep(self.refresh_delay_seconds)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('LaunchDarkly')
        self.ld_initialized = Label(name='ld_initialized', parent=self.content, align=uiconst.TOTOP)
        self.ld_user_key = Label(name='ld_user_key', parent=self.content, align=uiconst.TOTOP)
        self.ld_user_attributes = Label(name='ld_user_attributes', parent=self.content, align=uiconst.TOTOP)
        self.ld_last_log = Label(name='ld_last_log', parent=self.content, align=uiconst.TOTOP)
        self.ld_evaluate_text = SingleLineEditText(name='ld_evaluate_text', parent=self.content, align=uiconst.TOTOP)
        self.ld_evaluate_button = Button(name='ld_evaluate_button', parent=self.content, align=uiconst.TOTOP, label='Evaluate')
        c = launchdarkly.get_client()

        def evaluate_flag(flag_key):
            variation = c.get_json_variation_detail(feature_key=str(flag_key), fallback='{}')
            message = 'Variation: {}<br/>Index: {}<br/>Reason: {}'.format(variation[0], variation[1], variation[2])
            eve.Message('CustomInfo', {'info': message}, modal=0)

        self.ld_evaluate_button.SetFunc(lambda x: evaluate_flag(self.ld_evaluate_text.GetValue()))
        self.ld_queue_text = SingleLineEditText(name='ld_queue_text', parent=self.content, align=uiconst.TOTOP)
        self.ld_queue_button = Button(name='ld_queue_button', parent=self.content, align=uiconst.TOTOP, label='Queue Event')

        def queue_event(event_name):
            c.track(event_name)
            eve.Message('CustomInfo', {'info': 'Queued event {}'.format(event_name)}, modal=0)

        self.ld_queue_button.SetFunc(lambda x: queue_event(self.ld_queue_text.GetValue()))
        self.ld_flush_button = Button(name='ld_flush_button', parent=self.content, align=uiconst.TOTOP, label='Flush')
        self.ld_flush_button.SetFunc(lambda x: c.flush())
        self.variations = Scroll(id='variations', name='variations', parent=self.content, align=uiconst.TOALL)
        uthread2.StartTasklet(self.refresh)

    def update_labels(self):
        c = launchdarkly.get_client()
        initialized = c.is_initialized()
        self.ld_initialized.text = _initialized_label_text.format(initialized)
        if initialized:
            self.ld_initialized.SetTextColor(TextColor.NORMAL)
        else:
            self.ld_initialized.SetTextColor(eveColor.DANGER_RED)
        self.ld_user_key.text = _ld_user_key_label_text.format(c._ld_user_key)
        self.ld_user_attributes.text = _user_attributes_label_text.format(c.last_attributes)
        self.ld_last_log.text = _last_log_label_text.format(c.last_log)

    def update_variations(self):
        c = launchdarkly.get_client()
        variations = []
        for flag, variation in c.flag_state.items():
            callbacks = len(c.flag_callbacks.get(flag))
            variations.append(ScrollEntryNode(decoClass=SE_GenericCore, id=flag, name=flag, label='{}<t>{}<t>{}'.format(flag, callbacks, variation)))

        self.variations.Load(contentList=variations, headers=_headers)
