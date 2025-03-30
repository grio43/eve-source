#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\badge.py
import carbonui.const as uiconst
from carbon.common.script.util.format import FmtAmt, FmtAmtCapped
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from carbonui.fontconst import STYLE_SMALLTEXT, EVE_MEDIUM_FONTSIZE
BADGE_COLOR_UNSEEN = (0.97, 0.09, 0.13)

class Badge(Container):
    MIN_WIDTH = 16
    MIN_HEIGHT = 16
    MIN_LABEL_PADDING_H = 4

    def ApplyAttributes(self, attributes):
        super(Badge, self).ApplyAttributes(attributes)
        self._value = attributes.value
        self._color = BADGE_COLOR_UNSEEN
        self._maxValue = attributes.get('maxValue', None)
        self._Layout()
        self._Update()

    def SetValue(self, value):
        self._value = value
        self._Update()

    def SetCounterValue(self, value, *args):
        self.SetValue(value)

    def GetValue(self):
        return self._value

    def SetColor(self, color):
        self._color = color
        self.frame.SetRGBA(*color)

    def _Layout(self):
        self.label = Label(parent=self, align=uiconst.CENTER, fontsize=EVE_MEDIUM_FONTSIZE, fontStyle=STYLE_SMALLTEXT, color=Color.WHITE, bold=True)
        self.badgeContainer = Container(name='badgeContainer', parent=self, align=uiconst.CENTER)
        self.frame = Frame(name='badgeFrame', bgParent=self.badgeContainer, texturePath='res:/UI/Texture/Shared/counterFrame.png', cornerSize=8, offset=-1, color=self._color)

    def _Update(self):
        self._UpdateVisible()
        if self.display:
            self._UpdateLabel()
            self._UpdateSize()

    def _UpdateLabel(self):
        if self._maxValue and self._value > self._maxValue:
            text = FmtAmtCapped(self._maxValue, fmt='sn')
        else:
            text = FmtAmt(self._value, fmt='sn')
        self.label.SetText(text)

    def _UpdateVisible(self):
        if self._value > 0:
            self.Show()
        else:
            self.Hide()

    def _UpdateSize(self):
        self.width = max(self.MIN_WIDTH, self.label.textwidth + self.MIN_LABEL_PADDING_H * 2)
        self.height = max(self.MIN_HEIGHT, self.label.height)
        self.badgeContainer.width = self.width
        self.badgeContainer.height = self.MIN_HEIGHT
