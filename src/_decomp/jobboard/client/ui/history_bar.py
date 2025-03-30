#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\history_bar.py
import carbonui
import eveicon
import eveui
import threadutils

class HistoryBar(eveui.ContainerAutoSize):
    default_padding = (0, 4, 0, 4)
    _label_left = 48
    _label_opacity = carbonui.TextColor.SECONDARY.opacity
    _icon_opacity = carbonui.TextColor.SECONDARY.opacity

    def __init__(self, controller, **kwargs):
        super(HistoryBar, self).__init__(**kwargs)
        self._controller = controller
        self._layout()
        self._controller.on_page_change.connect(self._on_page_change)

    def _layout(self):
        self._back_button = eveui.ButtonIcon(parent=self, align=eveui.Align.center_left, texture_path=eveicon.navigate_back, size=16, on_click=self._controller.go_back, enabled=self._controller.is_back_available, opacity_enabled=self._icon_opacity, opacity_disabled=carbonui.TextColor.DISABLED.opacity)
        self._forward_button = eveui.ButtonIcon(parent=self, align=eveui.Align.center_left, left=24, texture_path=eveicon.navigate_forward, size=16, on_click=self._controller.go_forward, enabled=self._controller.is_forward_available, opacity_enabled=self._icon_opacity, opacity_disabled=carbonui.TextColor.DISABLED.opacity)
        self._page_title_label = carbonui.TextDetail(parent=self, align=eveui.Align.center_left, left=self._label_left, text=self._controller.history_label, opacity=self._label_opacity)

    def _on_page_change(self, *args, **kwargs):
        self._back_button.enabled = self._controller.is_back_available
        self._forward_button.enabled = self._controller.is_forward_available
        self._update_page_title()

    @threadutils.threaded
    def _update_page_title(self):
        eveui.animate(self._page_title_label, 'left', end_value=self._page_title_label.left + 10, duration=0.2)
        eveui.fade_out(self._page_title_label, duration=0.2, sleep=True)
        self._page_title_label.SetText(self._controller.history_label)
        eveui.animate(self._page_title_label, 'left', start_value=self._label_left - 10, end_value=self._label_left, duration=0.2)
        eveui.fade_in(self._page_title_label, end_value=self._label_opacity, duration=0.2)
