#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\warehouseRaidUI\scoreboard.py
import carbonui
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.gauge import Gauge
from eveui import Sprite

class ScoreRow(Container):
    default_height = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.label = attributes.get('label')
        self.iconTexturePath = attributes.get('iconTexturePath')
        self.denominator = attributes.get('denominator', 1)
        self.progressGauge = None
        self.valueText = None
        numerator = attributes.get('numerator', 0)
        self.ConstructLayout(numerator)

    def ConstructLayout(self, numerator):
        Sprite(parent=Transform(parent=self, align=uiconst.TOLEFT, width=16, height=32), align=uiconst.CENTER, texturePath=self.iconTexturePath, width=16, height=16)
        gaugeCont = Container(parent=self, align=uiconst.TOALL, padLeft=8)
        self.progressGauge = Gauge(parent=gaugeCont, label=self.label, width=213, gaugeHeight=3)
        self.valueText = carbonui.TextDetail(parent=gaugeCont, align=uiconst.TOPRIGHT, text='')
        self.SetValue(numerator)

    def SetValue(self, numerator, callback = None):
        self.numerator = numerator
        self.progressGauge.SetValueTimed(float(numerator) / float(self.denominator), duration=0.6, callback=callback)
        self.valueText.SetText(u'{}/{}'.format(numerator, self.denominator))
