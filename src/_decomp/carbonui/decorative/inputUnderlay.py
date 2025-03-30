#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\decorative\inputUnderlay.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations

class InputUnderlay(Container):

    def ApplyAttributes(self, attributes):
        super(InputUnderlay, self).ApplyAttributes(attributes)
        Frame(bgParent=self, color=(1.0, 1.0, 1.0, 0.05))
        self._background = Fill(bgParent=self, padding=1, color=(0.0, 0.0, 0.0, 0.1))

    def OnWindowAboveSetActive(self):
        animations.FadeTo(self._background, startVal=self._background.opacity, endVal=0.5, duration=uiconst.TIME_ENTRY)

    def OnWindowAboveSetInactive(self):
        animations.FadeTo(self._background, startVal=self._background.opacity, endVal=0.1, duration=uiconst.TIME_EXIT)
