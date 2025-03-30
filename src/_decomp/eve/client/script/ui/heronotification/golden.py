#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\heronotification\golden.py
from carbonui import uiconst
from carbonui.primitives.base import ReverseScaleDpi, ScaleDpiF
from carbonui.primitives.containerAutoSize import ContainerAutoSize

class GoldenPositionContainerAutoSize(ContainerAutoSize):

    def SetAlign(self, align):
        super(GoldenPositionContainerAutoSize, self).SetAlign(align)
        self.isPushAligned = False
        self.isAffectedByPushAlignment = False
        self._alignFunc = GoldenPositionContainerAutoSize.UpdateGoldenPositionAlignment

    def UpdateGoldenPositionAlignment(self, budget_only, *budget):
        if budget_only:
            return budget
        left, top, width, height = self.pos
        pad_left, pad_top, pad_right, pad_bottom = self.padding
        parent_height = ReverseScaleDpi(self.parent.displayHeight)
        half_height = int(round(height / 2.0))
        proportion = 1.0 - 1.0 / uiconst.GOLDEN_RATIO
        top += max(0, parent_height * proportion - half_height)
        displayX = (self.parent.displayWidth - ScaleDpiF(width)) / 2 + ScaleDpiF(left + pad_left)
        displayY = ScaleDpiF(top + pad_top)
        displayWidth = ScaleDpiF(width - pad_left - pad_right)
        displayHeight = ScaleDpiF(height - pad_top - pad_bottom)
        self.displayRect = (displayX,
         displayY,
         displayWidth,
         displayHeight)
        return budget
