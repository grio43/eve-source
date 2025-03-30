#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\ui.py
from ast import literal_eval
from carbonui.control.window import Window
from carbonui.uicore import uicore
from uihider import get_ui_hider, get_template_name
import threadutils
from .base import Action

class RevealUi(Action):
    atom_id = 9

    def __init__(self, ui_hiding_template_id = '', **kwargs):
        super(RevealUi, self).__init__(**kwargs)
        self.ui_hiding_template_id = ui_hiding_template_id

    def start(self, **kwargs):
        super(RevealUi, self).start(**kwargs)
        if self.ui_hiding_template_id is not None:
            get_ui_hider().reveal_ui(self.ui_hiding_template_id)

    @classmethod
    def get_subtitle(cls, ui_hiding_template_id = None, **kwargs):
        if ui_hiding_template_id is not None:
            return get_template_name(ui_hiding_template_id)
        return ''


class RevealAllUi(Action):
    atom_id = 10

    def start(self, **kwargs):
        super(RevealAllUi, self).start(**kwargs)
        get_ui_hider().reveal_everything()


class HideAllUi(Action):
    atom_id = 11

    def start(self, **kwargs):
        super(HideAllUi, self).start(**kwargs)
        get_ui_hider().hide_everything()


class OpenWindow(Action):
    atom_id = 198

    def __init__(self, window_id = None, **kwargs):
        super(OpenWindow, self).__init__(**kwargs)
        self.window_id = window_id

    def start(self, **kwargs):
        super(OpenWindow, self).start(**kwargs)
        if not self.window_id:
            return
        from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataRaw import BTNDATARAW_BY_ID
        if self.window_id in BTNDATARAW_BY_ID:
            window_class = BTNDATARAW_BY_ID[self.window_id].wndCls
            if window_class:
                window_class.Open()
                return
        for window in Window.__subclasses__():
            window_id = getattr(window, 'default_windowID', None)
            if self.window_id == window_id:
                window.Open()
                return

    @classmethod
    def get_subtitle(cls, window_id = '', **kwargs):
        return u'Window ID:{}'.format(window_id)


class CloseWindow(Action):
    atom_id = 199

    def __init__(self, window_id = None, **kwargs):
        super(CloseWindow, self).__init__(**kwargs)
        self.window_id = window_id

    def start(self, **kwargs):
        super(CloseWindow, self).start(**kwargs)
        if self.window_id:
            window = Window.GetIfOpen(windowID=self.window_id)
            if window:
                window.CloseByUser()

    @classmethod
    def get_subtitle(cls, window_id = '', **kwargs):
        return u'Window ID:{}'.format(window_id)


class PlayVideo(Action):
    atom_id = 239

    def __init__(self, resource_file_path = None, show_background = None, audio_ui_event = None, **kwargs):
        super(PlayVideo, self).__init__(**kwargs)
        self.resource_file_path = self.get_atom_parameter_value('resource_file_path', resource_file_path)
        self.show_background = self.get_atom_parameter_value('show_background', show_background)
        self.audio_ui_event = self.get_atom_parameter_value('audio_ui_event', audio_ui_event)
        self.video = None

    def start(self, **kwargs):
        super(PlayVideo, self).start(**kwargs)
        self._start_video()

    def stop(self):
        super(PlayVideo, self).stop()
        self._stop_video()

    def _start_video(self):
        import eveui
        self.video = eveui.VideoOverlay(resource_file_path=self.resource_file_path, show_background=self.show_background, audio_ui_event=self.audio_ui_event)
        self.video.start()

    def _stop_video(self):
        if self.video:
            self.video.stop()

    @classmethod
    def get_subtitle(cls, resource_file_path = '', **kwargs):
        return u'{}'.format(resource_file_path)


class SetClientSettings(Action):
    atom_id = 293

    def __init__(self, settings_section = None, settings_group = None, settings_id = None, settings_value = None, **kwargs):
        super(SetClientSettings, self).__init__(**kwargs)
        self.settings_section = self.get_atom_parameter_value('settings_section', settings_section)
        self.settings_group = self.get_atom_parameter_value('settings_group', settings_group)
        self.settings_id = settings_id
        self.settings_value = settings_value

    def start(self, **kwargs):
        super(SetClientSettings, self).start(**kwargs)
        try:
            value = literal_eval(self.settings_value)
        except (SyntaxError, ValueError):
            value = self.settings_value

        settings[self.settings_section].Set(self.settings_group, self.settings_id, value)

    @classmethod
    def get_subtitle(cls, settings_section = None, settings_group = None, settings_id = None, settings_value = None, **kwargs):
        return u'{}.{}.{}={}'.format(cls.get_atom_parameter_value('settings_section', settings_section), cls.get_atom_parameter_value('settings_group', settings_group), settings_id or 'MISSING', settings_value)


class UiElementAction(Action):
    atom_id = 335

    def __init__(self, function_name = None, ui_element_name = None, ui_element_object = None, **kwargs):
        super(UiElementAction, self).__init__(**kwargs)
        self.function_name = self.get_atom_parameter_value('function_name', function_name)
        self.ui_element_name = ui_element_name
        self.ui_element_object = ui_element_object

    def start(self, **kwargs):
        super(UiElementAction, self).start(**kwargs)
        if not self.function_name:
            return
        if self.ui_element_object:
            ui_element = self.ui_element_object
        elif self.ui_element_name:
            element_key_val = sm.GetService('uipointerSvc').FindElementToPointTo(self.ui_element_name, shouldExcludeInvisible=True)
            ui_element = element_key_val.pointToElement if element_key_val else None
        else:
            return
        if not ui_element:
            return
        function = getattr(ui_element, self.function_name)
        if function and callable(function):
            function()

    @classmethod
    def get_subtitle(cls, ui_element_name = None, function_name = None, **kwargs):
        function_name = cls.get_atom_parameter_value('function_name', function_name)
        if ui_element_name:
            return '{} {}'.format(ui_element_name, function_name)
        return function_name


class ShowDialogPopup(Action):
    atom_id = 503

    def __init__(self, dialog_key, dialog_values = None, **kwargs):
        super(ShowDialogPopup, self).__init__(**kwargs)
        self.dialog_key = dialog_key
        self.dialog_values = dialog_values

    def start(self, **kwargs):
        super(ShowDialogPopup, self).start(**kwargs)
        if not self.dialog_key:
            return
        self._start()

    @threadutils.threaded
    def _start(self):
        uicore.Message(self.dialog_key, self.dialog_values)

    @classmethod
    def get_subtitle(cls, dialog_key = None, **kwargs):
        return dialog_key
