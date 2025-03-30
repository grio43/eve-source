#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dropdownColorPicker.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.colorPanel import ColorPanel
from localization import GetByLabel

class DropdownColorPicker(Container):
    __guid__ = 'dropdownColorPicker'
    default_height = 20
    default_width = 27
    default_name = 'colorPicker'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.CENTERRIGHT
    default_colorPos = (0, 0, 16, 16)
    default_numColumns = 5
    COLOR_LIST = [(1.0, 0.7, 0.0),
     (1.0, 0.35, 0.0),
     (0.75, 0.0, 0.0),
     (0.1, 0.6, 0.1),
     (0.0, 0.63, 0.57),
     (0.2, 0.5, 1.0),
     (0.0, 0.15, 0.6),
     (0.0, 0.0, 0.0),
     (0.7, 0.7, 0.7)]

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.numColumns = attributes.get('numColumns', self.default_numColumns)
        self.currentColor = attributes.currentColor
        self.callback = attributes.callback
        self.colorPos = attributes.colorPos or self.default_colorPos
        self.arrowSprite = Sprite(parent=self, pos=(-2, 0, 16, 16), name='arrow', align=uiconst.CENTERRIGHT, texturePath='res:/ui/texture/icons/38_16_229.png', color=(1, 1, 1, 0.5), state=uiconst.UI_DISABLED)
        self.colorCont = Container(parent=self, name='colorCont', pos=(2, 0, 12, 12), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        Frame(parent=self.colorCont, name='colorFrame', color=(1, 1, 1, 0.2))
        self.colorFill = Fill(parent=self.colorCont, color=(0, 0, 0, 0))
        self.SetCurrentFill(self.currentColor)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def GetTooltipDelay(self):
        return 50

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.LoadStandardSpacing()
        colorPanel = ColorPanel(callback=lambda color: self.SetColorFromPanel(color=color, tooltipPanel=tooltipPanel), currentColor=self.currentColor, colorList=self.GetColors(), columns=self.numColumns)
        tooltipPanel.AddLabelSmall(text=GetByLabel('UI/Mail/Select Color'))
        tooltipPanel.AddCell(cellObject=colorPanel)

    def SetColorFromPanel(self, color, tooltipPanel):
        self.SetCurrentFill(color)
        self.callback(color, self)
        tooltipPanel.Close()

    def GetColors(self):
        return self.COLOR_LIST

    def SetCurrentFill(self, color):
        if color:
            color = tuple(color)
            if not isinstance(color, (tuple, list)):
                color = None
        self.currentColor = color
        fillColor = color
        self.colorFill.display = True
        if color is None:
            fillColor = (0, 0, 0, 0)
            self.colorFill.display = True
        elif len(fillColor) == 3:
            fillColor = color + (1,)
        self.colorFill.SetRGBA(*fillColor)
