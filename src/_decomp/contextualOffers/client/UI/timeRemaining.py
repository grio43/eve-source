#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\UI\timeRemaining.py
from carbonui import uiconst, fontconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import Label
import localization

class TimeRemaining(ContainerAutoSize):
    default_name = 'timeRemaining'
    default_align = uiconst.TOPRIGHT

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.ConstructLayout()

    def ConstructLayout(self):
        text_color = (1, 1, 1, 1)
        self.timerIcon = Sprite(name='timeIcon', parent=self, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/clock_icon.png', width=17, height=17)
        self.timerText = Label(name='timeRemainingText', parent=self, align=uiconst.CENTERLEFT, left=23, fontsize=20, bold=True, color=text_color)
        self.remainingText = Label(name='remainingLabel', parent=self, align=uiconst.CENTERLEFT, top=int(20 * fontconst.fontSizeFactor), left=23, fontsize=16, color=text_color)

    def SetRemainingText(self, text):
        self.remainingText.SetText(text)

    def UpdateTimeRemaining(self, time):
        if time > 0:
            self.timerText.SetText(text=localization.formatters.FormatTimeIntervalShortWritten(value=long(time), showFrom='day', showTo='second'))
        else:
            self.timerText.SetText(localization.GetByLabel('UI/ContextualOffers/Expired'))
