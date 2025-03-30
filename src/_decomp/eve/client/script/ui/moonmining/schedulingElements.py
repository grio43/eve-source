#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\schedulingElements.py
from carbonui.fontconst import STYLE_HEADER
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelLargeUpper, Label
import carbonui.const as uiconst

class StatusCont(Container):
    default_align = uiconst.CENTER
    default_height = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        color = attributes.color
        text = attributes.text or ''
        self.frame = Frame(bgParent=self)
        self.fill = Fill(bgParent=self)
        self.label = Label(name='statusLabel', parent=self, align=uiconst.CENTER, fontsize=14, uppercase=True, fontstyle=STYLE_HEADER)
        self.SetLabelText(text)
        self.SetWidth(self.GetMaxWidth())
        self.SetColors(color)

    def SetColors(self, color):
        self.frame.SetRGBA(*(color[:3] + (0.3,)))
        self.fill.SetRGBA(*(color[:3] + (0.1,)))
        textColor = GetTextColor(color)
        self.label.SetRGBA(*textColor)

    def GetMaxWidth(self):
        return self.label.textwidth + 100

    def SetWidth(self, width):
        self.width = width

    def GetLabelText(self):
        return self.label.text

    def SetLabelText(self, text):
        self.label.text = text


class HeaderStatus(Container):
    default_width = 200
    default_height = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        color = attributes.color
        text = attributes.text
        self.label = EveLabelLargeUpper(name='headerStatusLabel', parent=self, align=uiconst.CENTER, text=text, bold=True)
        self.edges = Frame(parent=self, texturePath='res:/UI/Texture/classes/Moonmining/headerFrame1.png', cornerSize=7)
        Frame(parent=self, texturePath='res:/UI/Texture/classes/Moonmining/headerFrame2.png', cornerSize=7, color=(0.75, 0.75, 0.75, 0.1))
        self.fill = Fill(bgParent=self, padding=1)
        self.SetColors(color)

    def SetColors(self, color):
        self.edges.SetRGBA(*(color[:3] + (0.5,)))
        self.fill.SetRGBA(*(color[:3] + (0.05,)))
        textColor = GetTextColor(color)
        self.label.SetRGBA(*textColor)

    def SetLabelText(self, text):
        self.label.text = text


def GetTextColor(color, maximumSaturation = 0.3):
    c = Color(*color)
    currentSaturation = c.GetSaturation()
    if currentSaturation < maximumSaturation:
        return color
    return c.SetSaturation(maximumSaturation).GetRGBA()
