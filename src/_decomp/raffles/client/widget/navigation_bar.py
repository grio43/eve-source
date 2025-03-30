#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\navigation_bar.py
import eveui
import threadutils
from raffles.client import texture
from raffles.client.localization import Text

class NavigationBar(eveui.ContainerAutoSize):
    default_height = 16
    _label_left = 56
    _label_opacity = 0.5

    def __init__(self, navigation_controller, **kwargs):
        super(NavigationBar, self).__init__(**kwargs)
        self._navigation_controller = navigation_controller
        self._layout()
        self._navigation_controller.bind(is_back_available=self._back_button.setter('enabled'), is_forward_available=self._forward_button.setter('enabled'), current_page_title=self._update_page_title)

    def _layout(self):
        self._back_button = eveui.ButtonIcon(parent=self, align=eveui.Align.center_left, texture_path=texture.history_back, size=16, on_click=self._navigation_controller.go_back, enabled=self._navigation_controller.is_back_available, opacity_enabled=0.6, opacity_disabled=0.2, hint=Text.history_back())
        self._forward_button = eveui.ButtonIcon(parent=self, align=eveui.Align.center_left, left=24, texture_path=texture.history_forward, size=16, on_click=self._navigation_controller.go_forward, enabled=self._navigation_controller.is_forward_available, opacity_enabled=0.6, opacity_disabled=0.2, hint=Text.history_forward())
        self._page_title_label = eveui.EveLabelMedium(parent=self, align=eveui.Align.center_left, left=self._label_left, text=self._navigation_controller.current_page_title, opacity=self._label_opacity)

    @threadutils.threaded
    def _update_page_title(self, navigation_controller, title):
        eveui.animate(self._page_title_label, 'left', end_value=self._page_title_label.left + 10, duration=0.25)
        eveui.fade_out(self._page_title_label, duration=0.25, sleep=True)
        self._page_title_label.SetText(title)
        eveui.animate(self._page_title_label, 'left', start_value=self._label_left - 10, end_value=self._label_left, duration=0.25)
        eveui.fade_in(self._page_title_label, end_value=self._label_opacity, duration=0.25)
