#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\status_bar.py
from carbonui import uiconst
from carbonui.util.color import Color
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.info.infoUtil import GetColoredText, PrepareInfoTextForAttributeHint

class StatusBar(LabelTextSides):
    __guid__ = 'listentry.StatusBar'
    default_gradientBrightnessFactor = 1.5
    default_color = Color.GRAY

    def Startup(self, *args):
        LabelTextSides.Startup(self, args)
        self.sr.gauge = Gauge(parent=self, gaugeHeight=28, align=uiconst.TOTOP, top=1, padding=(1, 0, 1, 0), state=uiconst.UI_DISABLED)

    def Load(self, node):
        LabelTextSides.Load(self, node)
        modifiedAttribute = node.modifiedAttribute
        if modifiedAttribute:
            coloredText = GetColoredText(modifiedAttribute, text=self.sr.text.text)
            self.sr.text.text = coloredText
            itemID = node.itemID
            PrepareInfoTextForAttributeHint(self.sr.text, modifiedAttribute, itemID)
        self.sr.gauge.gradientBrightnessFactor = node.Get('gradientBrightnessFactor', self.default_gradientBrightnessFactor)
        color = node.Get('color', self.default_color)
        self.sr.gauge.SetColor(color)
        self.sr.gauge.SetBackgroundColor(color)
        self.sr.gauge.SetValueInstantly(node.Get('value', 0.0))
