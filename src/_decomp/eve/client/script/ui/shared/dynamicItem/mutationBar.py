#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dynamicItem\mutationBar.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.util import color
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.dynamicItem.const import COLOR_NEGATIVE, COLOR_POSITIVE
import math
COLOR_BAR_BACKGROUND = color.Color.GRAY2
COLOR_PIP = color.Color.WHITE

class MutationBar(ContainerAutoSize):
    default_height = 24
    default_barWidth = 50

    def ApplyAttributes(self, attributes):
        super(MutationBar, self).ApplyAttributes(attributes)
        self.attribute = attributes.attribute
        self.barWidth = attributes.get('barWidth', self.default_barWidth)
        self.Layout()

    def Layout(self):
        EveLabelMedium(parent=self, align=uiconst.TOLEFT, text=self.attribute.displayMutationLow)
        barCont = Container(parent=self, align=uiconst.TOLEFT, left=8, width=self.barWidth)
        EveLabelMedium(parent=self, align=uiconst.TOLEFT, left=8, text=self.attribute.displayMutationHigh)
        Fill(parent=barCont, align=uiconst.TOTOP_NOPUSH, top=6, height=4, color=COLOR_BAR_BACKGROUND)
        a = self.attribute
        mutationRangeWidth = a.mutationMax - a.mutationMin
        value = getattr(a, 'baseValue', a.value)
        if a.highIsGood:
            left = max((min(value, a.sourceValue) - a.mutationMin) / mutationRangeWidth, 0.0)
        else:
            left = max((a.mutationMax - max(value, a.sourceValue)) / mutationRangeWidth, 0.0)
        width = abs((value - max(a.sourceValue, a.mutationMin)) / mutationRangeWidth)
        if a.isMutationPositive:
            changeColor = COLOR_POSITIVE
            rotation = 0.0
        else:
            changeColor = COLOR_NEGATIVE
            rotation = math.pi
        Sprite(parent=barCont, align=uiconst.TOPLEFT, top=6, height=4, left=left * self.barWidth, width=width * self.barWidth, texturePath='res:/UI/Texture/Classes/DynamicItem/arrows.png', tileX=True, rotation=rotation, color=changeColor, idx=0)
        left = max(abs(value - a.mutationLow) / mutationRangeWidth, 0.0)
        Fill(parent=barCont, align=uiconst.TOPLEFT, top=6, height=4, left=math.floor(left * self.barWidth), width=1, color=COLOR_PIP, idx=0)
