#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\segment\underlay.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui import eveThemeColor
OPACITY_IDLE = 0.05
OPACITY_ACTIVE = 0.2

class WindowSegmentUnderlay(Container):

    def ApplyAttributes(self, attributes):
        super(WindowSegmentUnderlay, self).ApplyAttributes(attributes)
        wnd = GetWindowAbove(self)
        self._background = Fill(bgParent=self, color=eveThemeColor.THEME_TINT, opacity=OPACITY_ACTIVE if wnd and wnd.active else OPACITY_IDLE)

    def OnWindowAboveSetActive(self):
        animations.FadeTo(self._background, startVal=self._background.opacity, endVal=OPACITY_ACTIVE, duration=0.3)

    def OnWindowAboveSetInactive(self):
        animations.FadeTo(self._background, startVal=self._background.opacity, endVal=OPACITY_IDLE, duration=0.3)
