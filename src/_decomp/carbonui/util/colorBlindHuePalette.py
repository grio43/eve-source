#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\colorBlindHuePalette.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
import carbonui.const as uiconst
from carbonui.util import color
from localization import GetByLabel
NUM_SAMPLES = 32
SIZE = 8

class ColorBlindHuePalette(ContainerAutoSize):
    default_name = 'ColorBlindHuePalette'

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.ConstructLayout()

    def Reconstruct(self):
        self.Flush()
        self.ConstructLayout()

    def ConstructLayout(self):
        self.ConstructPalette(ignore=True, hint=GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindOriginalPalette'))
        self.ConstructPalette(ignore=False, hint=GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindResultingPalette'))

    def ConstructPalette(self, ignore, hint):
        cont = Container(parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=SIZE, padBottom=5, hint=hint)
        for i in xrange(NUM_SAMPLES):
            c = color.Color(1, 1, 1, 1.0).SetHSB(float(i) / NUM_SAMPLES, 1.0, 1.0).GetRGBA()
            Fill(parent=cont, align=uiconst.TOLEFT_PROP, width=1.0 / NUM_SAMPLES, color=c, padLeft=1, ignoreColorBlindMode=ignore)
