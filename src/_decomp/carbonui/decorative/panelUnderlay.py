#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\decorative\panelUnderlay.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import GetWindowAbove

class PanelUnderlay(Container):
    OPACITY_IDLE = 0.025
    OPACITY_ACTIVE = 0.05
    _active = False
    _background = None

    def __init__(self, **kwargs):
        super(PanelUnderlay, self).__init__(**kwargs)
        self._update_active()
        self._background = Fill(bgParent=self, align=uiconst.TOALL, color=(1.0, 1.0, 1.0), opacity=self._get_opacity())

    def SetParent(self, parent, idx = None):
        super(PanelUnderlay, self).SetParent(parent, idx)
        self._update_active()

    def _update_active(self):
        was_active = self._active
        window = GetWindowAbove(self)
        if window:
            self._active = window.active
        else:
            self._active = False
        if was_active != self._active:
            self._update_opacity()

    def _get_opacity(self):
        if self._active:
            return self.OPACITY_ACTIVE
        return self.OPACITY_IDLE

    def _update_opacity(self):
        if self._background:
            animations.FadeTo(self._background, startVal=self._background.opacity, endVal=self._get_opacity(), duration=uiconst.TIME_ENTRY)

    def OnWindowAboveSetActive(self):
        self._update_active()

    def OnWindowAboveSetInactive(self):
        self._update_active()
