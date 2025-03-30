#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\side_sheet.py
import carbonui.const as uiconst
from carbonui.uicore import uicore
import eveui
import threadutils
from raffles.client import sound, texture

class SideSheet(eveui.Container):
    default_name = 'SideSheet'

    def __init__(self, title, icon, content_width, content_height, **kwargs):
        super(SideSheet, self).__init__(**kwargs)
        self._title = title
        self._icon = icon
        self._content_width = content_width
        self._content_height = content_height
        self.content_container = None
        self._global_click = None
        self._transitioning = False
        self._layout()
        self.opened_container.opacity = 0
        self.content_container.opacity = 0
        self.opened_container.Hide()

    def Enable(self, *args):
        self.state = eveui.State.pick_children

    def OnGlobalMouseDown(self, object, *args, **kwargs):
        if self._transitioning or object.IsUnder(self) or object.IsUnder(uicore.layer.menu) or object.IsUnder(uicore.layer.modal):
            return True
        self._close()

    def _open(self, *args, **kwargs):
        if self._transitioning:
            return
        self._transitioning = True
        self._global_click = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)
        self.opened_container.Show()
        self.opened_container.Enable()
        eveui.play_sound(sound.filters_expand)
        eveui.fade_in(self.opened_container, duration=0.2)
        eveui.animate(self.opened_container, 'padRight', start_value=200, end_value=0, duration=0.1, sleep=True)
        eveui.animate(self.opened_container, 'padBottom', end_value=0, duration=0.1)
        eveui.fade_in(self.content_container, duration=0.1, time_offset=0.1, sleep=True)
        self._transitioning = False
        self.on_open()

    def on_open(self):
        pass

    @threadutils.threaded
    def _close(self, *args, **kwargs):
        if self._transitioning:
            return
        self._transitioning = True
        uicore.event.UnregisterForTriuiEvents(self._global_click)
        focus = uicore.registry.GetFocus()
        if focus is not None and focus.IsUnder(self.opened_container):
            uicore.registry.SetFocus(self._open_button)
        self.opened_container.Disable()
        eveui.play_sound(sound.filters_collapse)
        eveui.fade_out(self.content_container, duration=0.1)
        eveui.animate(self.opened_container, 'padBottom', end_value=470, duration=0.1, sleep=True)
        eveui.fade_out(self.opened_container, duration=0.1)
        eveui.animate(self.opened_container, 'padRight', end_value=200, duration=0.1, sleep=True)
        self.opened_container.Hide()
        self._transitioning = False

    def _layout(self):
        self._construct_opened()
        self._construct_closed()
        self.content_container = eveui.Container(parent=self.opened_container, padding=16)

    def _construct_closed(self):
        self._open_button = eveui.Button(parent=self, align=eveui.Align.top_left, height=30, width=40, func=self._open, hint=self._title)
        self.filter_icon = eveui.Sprite(parent=self._open_button, align=eveui.Align.center, height=20, width=20, texturePath=self._icon)

    def _construct_opened(self):
        self.opened_container = container = eveui.Container(parent=self, state=eveui.State.normal, align=eveui.Align.top_left, width=self._content_width, height=self._content_height, idx=0)
        eveui.Frame(bgParent=container, texturePath=texture.panel_1_corner, cornerSize=9, color=(0, 0, 0, 0.9))
        top = eveui.Container(parent=container, state=eveui.State.normal, align=eveui.Align.to_top, height=28, bgColor=(0.1, 0.1, 0.1, 1))
        top.OnClick = self._close
        eveui.Sprite(parent=top, align=eveui.Align.center_left, height=20, width=20, left=10, texturePath=texture.filter_icon)
        eveui.Line(parent=top, align=eveui.Align.to_left, opacity=0.75, weight=2)
        eveui.EveHeaderMedium(parent=top, align=eveui.Align.center, text=self._title)
