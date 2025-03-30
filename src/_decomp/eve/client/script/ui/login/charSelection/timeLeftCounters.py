#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charSelection\timeLeftCounters.py
import carbonui.const as uiconst
import localization
import blue
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import IsUnder
from carbonui.primitives.container import Container
import eve.client.script.ui.login.charSelection.characterSelectionUtils as csUtil
import eve.client.script.ui.login.charSelection.characterSelectionColors as csColors
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button

class CountDownCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.subscriptionTimers = attributes.timers
        self.trainingEndTimes = self.subscriptionTimers.trainingEndTimes
        Fill(bgParent=self, color=csColors.SUBSCRIPTION_BORDER_FILL)
        if self.trainingEndTimes:
            trainingSlotNumber = 2
            iconPath = 'res:/UI/Texture/classes/CharacterSelection/skillbook_timer.png'
            for endTime in self.trainingEndTimes:
                hintMessage = 'UI/CharacterSelection/QueueExpiryHint%d' % trainingSlotNumber
                timer = CountDownTimer(parent=self, endTime=endTime.trainingEnds, iconPath=iconPath, callback=self.GoToAccountMgmt, hintMessage=hintMessage)
                trainingSlotNumber += 1

    def GoToAccountMgmt(self, *args):
        uicore.cmd.GetCommandAndExecute('OpenAccountManagement', origin='characterSelection')


class CountDownTimer(Container):
    default_align = uiconst.TOLEFT
    default_state = uiconst.UI_NORMAL
    default_width = 72
    default_height = 64
    default_padLeft = 4
    default_padTop = 4
    default_padBottom = 4
    default_padRight = 4

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        endTime = attributes.endTime
        iconPath = attributes.iconPath
        addButton = attributes.get('addButton', False)
        self.callback = attributes.get('callback', None)
        hintMessage = attributes.get('hintMessage', None)
        if hintMessage:
            self.hint = localization.GetByLabel(hintMessage, endTime=endTime)
        self.highlight = Fill(bgParent=self, color=(0.8, 0.8, 0.8, 0.2))
        self.highlight.display = False
        icon = Sprite(parent=self, pos=(0, 0, 32, 32), align=uiconst.CENTERLEFT, texturePath=iconPath, state=uiconst.UI_DISABLED)
        now = blue.os.GetWallclockTime()
        timeLeft = max(0L, endTime - now)
        timeLeftText = localization.formatters.FormatTimeIntervalWritten(long(timeLeft), showFrom='day', showTo='day')
        self.label = eveLabel.EveLabelLarge(parent=self, pos=(8, 0, 0, 0), align=uiconst.CENTERRIGHT, text=timeLeftText, state=uiconst.UI_DISABLED)
        if timeLeft < csUtil.WARNING_TIME:
            self.label.SetRGBA(1, 0, 0, 1)
        self.width = icon.width + self.label.textwidth + self.label.left + 4
        if self.callback:
            self.OnClick = self.callback
        if addButton:
            btnText = attributes.get('btnText', '')
            self.AddButton(btnText=btnText)

    def AddButton(self, btnText = ''):
        buyBtn = Button(name='buyBtn', label=btnText, parent=self, align=uiconst.CENTERRIGHT, func=self.callback, pos=(4, 0, 0, 0))
        btnMouseExit = buyBtn.OnMouseExit
        buyBtn.OnMouseExit = (self.OnButtonMouseExit, btnMouseExit)
        self.label.left += buyBtn.width + 8
        self.width += buyBtn.width

    def OnMouseEnter(self, *args):
        self.highlight.display = True

    def OnMouseExit(self, *args):
        if not IsUnder(uicore.uilib.mouseOver, self):
            self.highlight.display = False

    def OnButtonMouseExit(self, btnMouseExitFunction):
        if uicore.uilib.mouseOver != self:
            self.OnMouseExit()
        btnMouseExitFunction()

    def OnClick(self, *args):
        if self.callback:
            self.callback()
