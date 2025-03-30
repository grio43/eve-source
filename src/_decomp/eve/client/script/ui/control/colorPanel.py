#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\colorPanel.py
import eveicon
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
import carbonui.const as uiconst
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from localization import GetByLabel

class ColorPanel(LayoutGrid):
    default_colorPos = (0, 0, 16, 16)
    default_columns = 5

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)
        self.cellPadding = 0
        self.cellSpacing = 4
        self.margin = 0
        self.addClear = attributes.get('addClear', True)
        self.colorList = attributes['colorList']
        self.callback = attributes.callback
        currentColor = attributes.currentColor
        self.colorPos = attributes.colorPos or self.default_colorPos
        for color in self.colorList:
            c = Container(name='colorFill', pos=self.colorPos, align=uiconst.NOALIGN, state=uiconst.UI_NORMAL, bgColor=color)
            frameColor = Color(*color).SetBrightness(1.0).SetOpacity(0.15).GetRGBA()
            Frame(parent=c, color=frameColor, padding=-1)
            if color == currentColor:
                Frame(parent=c, name='selectedColorFrame', color=eveColor.PLATINUM_GREY, padding=-2)
            c.OnClick = lambda c = color, *args: self.OnColorSelected(color=c)
            self.AddCell(cellObject=c, colSpan=1, cellPadding=1)

        if self.addClear:
            self.AddCell(cellObject=self.GetClearButton(c), colSpan=1)

    def GetClearButton(self, c):
        return ButtonIcon(texturePath=eveicon.close.resolve(16), align=uiconst.NOALIGN, hint=GetByLabel('UI/SystemMenu/ResetSettings/Clear'), func=lambda *args: self.OnColorSelected(None), pos=self.colorPos)

    def OnColorSelected(self, color):
        self.callback(color)
