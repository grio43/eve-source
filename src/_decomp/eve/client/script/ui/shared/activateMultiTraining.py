#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\activateMultiTraining.py
import functools
import math
import blue
import localization
import uthread
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.control.button import Button
from carbonui.util.color import Color
from carbonui.control.window import Window
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold, EveLabelMedium, EveLabelMediumBold
from eve.common.lib import appConst as const
from eveexceptions import UserError

def ActivateMultiTraining(itemID = 0, tokens = None, charId = None, useHomeStation = False):
    wnd = ActivateMultiTrainingWindow.Open(itemID=0, tokens=tokens, charId=charId, useHomeStation=useHomeStation)
    if wnd and not wnd.destroyed:
        wnd.itemID = itemID
        wnd.tokens = tokens
        wnd.charId = charId
        wnd.useHomeStation = useHomeStation
    wnd.ModalPosition()


class ActivateMultiTrainingWindow(Window):
    __guid__ = 'form.ActivateMultiTrainingWindow'
    default_width = 420
    default_heigt = 100
    default_windowID = 'ActivateMultiTrainingWindow'
    default_clipChildren = True
    default_isLightBackgroundConfigurable = False
    GRAY_COLOR = Color.GRAY5
    GREEN_COLOR = (0.0, 1.0, 0.0, 0.8)
    LINE_COLOR = (1, 1, 1, 0.2)
    WHITE_COLOR = Color.WHITE
    CONFIRM_DELAY = 3000

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.itemID = attributes['itemID']
        self.tokens = attributes['tokens']
        self.useHomeStation = attributes['useHomeStation']
        self.expireDate1 = None
        self.expireDate2 = None
        self.numberOfDays = 30 * len(self.tokens) if self.tokens else 30
        self.reloading = False
        self.confirmed = False
        self.highlight = None
        self.charId = None
        self.Layout()
        self.Reload()
        uthread.new(self.UpdateTimersThread)

    def Layout(self):
        self.HideHeader()
        self.MakeUnResizeable()
        self.container = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, padding=(15, 15, 15, 0), callback=self.OnContainerResized)
        EveLabelLargeBold(parent=self.container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ActivateMultiTraining/ActivateHeading'))
        EveLabelMedium(parent=self.container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ActivateMultiTraining/ActivateDescription', numberOfDays=self.numberOfDays), color=self.GRAY_COLOR, padding=(0, 5, 0, 10))
        Line(parent=self.container, align=uiconst.TOTOP, color=self.LINE_COLOR)
        slot1 = ContainerAutoSize(parent=self.container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
        self.slot1Background = Fill(parent=slot1, color=self.GREEN_COLOR, opacity=0.0)
        self.slot1Title = EveLabelMediumBold(parent=slot1, align=uiconst.TOTOP, text='', padding=(60, 12, 140, 0), color=self.WHITE_COLOR)
        self.slot1Expiry = EveLabelMediumBold(parent=slot1, align=uiconst.TOTOP, text='', padding=(60, 0, 140, 10), color=self.GRAY_COLOR)
        self.slot1Button = Button(parent=slot1, label='', align=uiconst.CENTERRIGHT, fontsize=13, fixedwidth=120, fixedheight=30, pos=(10, 0, 0, 0))
        self.slot1Button.confirmHilite = GradientSprite(bgParent=self.slot1Button, rotation=-math.pi / 2, rgbData=[(0, self.GREEN_COLOR[:3])], alphaData=[(0, 0.5), (0.3, 0.2), (0.6, 0.14)], opacity=0.0)
        self.slot1Icon = Sprite(parent=slot1, texturePath='res:/UI/Texture/Icons/add_training_queue.png', align=uiconst.CENTERLEFT, pos=(15, 0, 32, 32))
        Line(parent=self.container, align=uiconst.TOTOP, color=self.LINE_COLOR)
        slot2 = ContainerAutoSize(parent=self.container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
        self.slot2Background = Fill(parent=slot2, color=self.GREEN_COLOR, opacity=0.0)
        self.slot2Title = EveLabelMediumBold(parent=slot2, align=uiconst.TOTOP, text='', padding=(60, 12, 140, 0), color=self.WHITE_COLOR)
        self.slot2Expiry = EveLabelMediumBold(parent=slot2, align=uiconst.TOTOP, text='', padding=(60, 0, 140, 10), color=self.GRAY_COLOR)
        self.slot2Button = Button(parent=slot2, label='', align=uiconst.CENTERRIGHT, fontsize=13, fixedwidth=120, fixedheight=30, pos=(10, 0, 0, 0))
        self.slot2Button.confirmHilite = GradientSprite(bgParent=self.slot2Button, rotation=-math.pi / 2, rgbData=[(0, self.GREEN_COLOR[:3])], alphaData=[(0, 0.5), (0.3, 0.2), (0.6, 0.14)], opacity=0.0)
        self.slot2Icon = Sprite(parent=slot2, texturePath='res:/UI/Texture/Icons/add_training_queue.png', align=uiconst.CENTERLEFT, pos=(15, 0, 32, 32))
        Line(parent=self.container, align=uiconst.TOTOP, color=self.LINE_COLOR)
        self.closeButton = Button(parent=self.container, label=localization.GetByLabel('UI/Generic/Cancel'), func=self.Close, align=uiconst.TOTOP, fontsize=13, padding=(120, 10, 120, 30))

    def Reload(self, delay = 0, force = False):
        try:
            self.reloading = True
            blue.pyos.synchro.SleepWallclock(delay)
            if self.destroyed:
                return
            queues = sm.RemoteSvc('userSvc').GetUpdatedMultiCharacterTraining(force)
            if len(queues) < 1:
                self.expireDate1 = None
                self.slot1Title.text = localization.GetByLabel('UI/ActivateMultiTraining/AdditionalQueueNotActive')
                self.slot1Title.color = self.GRAY_COLOR
                self.slot1Icon.opacity = 0.3
                self.slot1Button.SetLabel(localization.GetByLabel('UI/ActivateMultiTraining/Activate'))
                self.slot1Button.SetHint(localization.GetByLabel('UI/ActivateMultiTraining/ActivateHint', expiryDate=blue.os.GetWallclockTime() + self.numberOfDays * const.DAY))
                self.slot1Button.func = functools.partial(self.OnConfirmButton, self.slot1Button, self.OnAddQueue, 2, None)
            if len(queues) < 2:
                self.expireDate2 = None
                self.slot2Title.text = localization.GetByLabel('UI/ActivateMultiTraining/AdditionalQueueNotActive')
                self.slot2Title.color = self.GRAY_COLOR
                self.slot2Icon.opacity = 0.3
                self.slot2Button.SetLabel(localization.GetByLabel('UI/ActivateMultiTraining/Activate'))
                self.slot2Button.SetHint(localization.GetByLabel('UI/ActivateMultiTraining/ActivateHint', expiryDate=blue.os.GetWallclockTime() + self.numberOfDays * const.DAY))
                self.slot2Button.func = functools.partial(self.OnConfirmButton, self.slot2Button, self.OnAddQueue, 3, None)
            for index, (trainingID, trainingExpiry) in enumerate(sorted(queues)):
                if index == 0:
                    self.expireDate1 = trainingExpiry
                    self.slot1Title.text = localization.GetByLabel('UI/ActivateMultiTraining/AdditionalQueueActive')
                    self.slot1Title.color = self.GREEN_COLOR
                    self.slot1Icon.opacity = 1.0
                    self.slot1Button.SetLabel(localization.GetByLabel('UI/ActivateMultiTraining/Extend'))
                    self.slot1Button.SetHint(localization.GetByLabel('UI/ActivateMultiTraining/ExtendHint', expiryDate=trainingExpiry + self.numberOfDays * const.DAY))
                    self.slot1Button.func = functools.partial(self.OnConfirmButton, self.slot1Button, self.OnAddQueue, 1, trainingID)
                elif index == 1:
                    self.expireDate2 = trainingExpiry
                    self.slot2Title.text = localization.GetByLabel('UI/ActivateMultiTraining/AdditionalQueueActive')
                    self.slot2Title.color = self.GREEN_COLOR
                    self.slot2Icon.opacity = 1.0
                    self.slot2Button.SetLabel(localization.GetByLabel('UI/ActivateMultiTraining/Extend'))
                    self.slot2Button.SetHint(localization.GetByLabel('UI/ActivateMultiTraining/ExtendHint', expiryDate=trainingExpiry + self.numberOfDays * const.DAY))
                    self.slot2Button.func = functools.partial(self.OnConfirmButton, self.slot2Button, self.OnAddQueue, 2, trainingID)

            uicore.animations.FadeTo(self.slot1Button.confirmHilite, self.slot1Button.confirmHilite.opacity, 0.0, duration=0.3)
            uicore.animations.FadeTo(self.slot2Button.confirmHilite, self.slot2Button.confirmHilite.opacity, 0.0, duration=0.3)
            self.EnableButtons()
            if len(queues) == 0:
                self.slot2Button.Disable()
            if self.confirmed:
                self.slot1Button.state = uiconst.UI_HIDDEN
                self.slot2Button.state = uiconst.UI_HIDDEN
                self.closeButton.SetLabel(localization.GetByLabel('UI/Generic/OK'))
            else:
                self.slot1Button.state = uiconst.UI_NORMAL
                self.slot2Button.state = uiconst.UI_NORMAL
                self.closeButton.SetLabel(localization.GetByLabel('UI/Generic/Cancel'))
            if self.highlight == 1:
                uicore.animations.FadeTo(self.slot1Background, self.slot1Background.opacity, 0.1, duration=0.3)
                self.closeButton.Blink(blinks=1)
                self.highlight = None
            elif self.highlight == 2:
                uicore.animations.FadeTo(self.slot2Background, self.slot2Background.opacity, 0.1, duration=0.3)
                self.closeButton.Blink(blinks=1)
                self.highlight = None
            self.UpdateTimers()
        finally:
            self.reloading = False

    def UpdateTimersThread(self):
        while not self.destroyed:
            blue.pyos.synchro.SleepWallclock(1000)
            self.UpdateTimers()

    def OnContainerResized(self):
        self.height = self.container.height

    def OnConfirmButton(self, button, *args):
        if not self.reloading:
            self.DisableButtons()
            button.Enable()
            button.func = functools.partial(*args[:-1])
            button.SetLabel(localization.GetByLabel('UI/ActivateMultiTraining/Confirm'))
            uicore.animations.FadeTo(button.confirmHilite, button.confirmHilite.opacity, 1.0, duration=0.3)
            self.Reload(self.CONFIRM_DELAY)

    def OnAddQueue(self, slot, trainingID, button):
        if not self.confirmed:
            self.confirmed = True
            self.highlight = slot
            self.Reload()
            try:
                if self.tokens:
                    sm.RemoteSvc('userSvc').ActivateSoulboundMultiTraining(self.charId, self.tokens, trainingID=trainingID, useHomeStation=self.useHomeStation)
                else:
                    sm.RemoteSvc('userSvc').ActivateMultiTraining(self.itemID, trainingID=trainingID)
                self.Reload(force=True)
            except UserError:
                self.Close()
                raise

    def UpdateTimers(self):
        if self.expireDate1:
            timeRemaining = localization.formatters.FormatTimeIntervalShortWritten(self.expireDate1 - blue.os.GetWallclockTime(), showFrom='day', showTo='second')
            self.slot1Expiry.text = localization.GetByLabel('UI/ActivateMultiTraining/Ends', timeRemaining=timeRemaining)
        else:
            self.slot1Expiry.text = ''
        if self.expireDate2:
            timeRemaining = localization.formatters.FormatTimeIntervalShortWritten(self.expireDate2 - blue.os.GetWallclockTime(), showFrom='day', showTo='second')
            self.slot2Expiry.text = localization.GetByLabel('UI/ActivateMultiTraining/Ends', timeRemaining=timeRemaining)
        else:
            self.slot2Expiry.text = ''

    def DisableButtons(self):
        self.slot1Button.Disable()
        self.slot2Button.Disable()

    def EnableButtons(self):
        self.slot1Button.Enable()
        self.slot2Button.Enable()
