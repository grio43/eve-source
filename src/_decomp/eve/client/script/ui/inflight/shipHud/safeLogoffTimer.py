#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\safeLogoffTimer.py
import blue
import localization
import uthread
from carbonui import uiconst
from carbonui.control.radioButton import RadioButton
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveCaptionLarge
from carbonui.decorative.menuUnderlay import MenuUnderlay

class SafeLogoffTimer(Container):
    __guid__ = 'uicls.SafeLogoffTimer'
    default_align = uiconst.CENTERTOP
    default_state = uiconst.UI_NORMAL
    default_width = 300
    default_height = 130
    default_top = 300
    default_bgColor = (0.05, 0.05, 0.05, 0.75)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.SetHint(localization.GetByLabel('UI/Inflight/SafeLogoffTimerHint'))
        Frame(parent=self, color=(1.0, 1.0, 1.0, 0.5))
        self.logoffTime = attributes.logoffTime
        topCont = Container(parent=self, align=uiconst.TOTOP, height=30)
        timerCont = Container(parent=self, align=uiconst.TOTOP, height=70)
        bottomCont = Container(parent=self, align=uiconst.TOALL)
        self.caption = eveLabel.Label(parent=topCont, fontsize=24, bold=True, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/Inflight/SafeLogoffTimerCaption'), top=4)
        self.timer = eveLabel.Label(parent=timerCont, align=uiconst.CENTER, fontsize=60, color=Color.YELLOW, bold=True)
        self.button = Button(parent=bottomCont, label=localization.GetByLabel('UI/Inflight/SafeLogoffAbortLogoffLabel'), align=uiconst.CENTER, func=self.AbortSafeLogoff)
        self.quitting = True
        self.UpdateLogoffTime()
        uthread.new(self.UpdateLogoffTime_Thread)

    def UpdateLogoffTime(self):
        timeLeft = self.logoffTime - blue.os.GetSimTime()
        timeLeft += const.SEC
        self.timer.text = '%.1f' % max(0.1, timeLeft / float(const.SEC))

    def UpdateLogoffTime_Thread(self):
        self.countingDown = True
        while self.countingDown:
            self.UpdateLogoffTime()
            blue.pyos.synchro.SleepSim(50)

    def AbortLogoff(self, *args):
        self.countingDown = False
        uthread.new(self.AbortLogoff_Thread)

    def AbortLogoff_Thread(self):
        blue.pyos.synchro.SleepSim(1000)
        uicore.animations.FadeOut(self, duration=1.0, sleep=True)
        self.Close()

    def AbortSafeLogoff(self, *args):
        shipAccess = sm.GetService('gameui').GetShipAccess()
        shipAccess.AbortSafeLogoff()
        self.AbortLogoff()

    def SetTimerCompleted(self):
        self.timer.SetText('0.0')
        self.timer.SetTextColor(Color.GREEN)
        self.countingDown = False

    def OnClose(self, *args):
        self.countingDown = False


class SafeLogoffTimer2(Container):
    __guid__ = 'uicls.SafeLogoffTimer2'
    default_align = uiconst.CENTERTOP
    default_state = uiconst.UI_NORMAL
    default_width = 300
    default_height = 225
    default_top = 250
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.SetHint(localization.GetByLabel('UI/Inflight/SafeLogoffTimerHint'))
        self.logoffTime = attributes.logoffTime
        self.buttonCont = Container(name='buttonCont', parent=self, align=uiconst.TOBOTTOM, height=32, padding=(0, 16, 0, 16))
        self.mainGrid = LayoutGrid(name='mainGrid', parent=self, align=uiconst.CENTERTOP, columns=1, cellSpacing=(16, 16), top=16)
        self.caption = EveCaptionMedium(parent=self.mainGrid, align=uiconst.CENTERTOP, text='<center>%s</center>' % localization.GetByLabel('UI/Inflight/SafeLogoffTimerCaption'), width=250)
        self.timer = EveCaptionLarge(parent=self.mainGrid, align=uiconst.CENTER, color=eveColor.WARNING_ORANGE)
        self.button = Button(parent=self.buttonCont, label=localization.GetByLabel('UI/Commands/Abort'), align=uiconst.CENTER, func=self.AbortSafeLogoff)
        self.cleanedHouse = False
        self.quitting = False
        row = self.mainGrid.AddRow()
        cbCont = ContainerAutoSize(name='cbCont', parent=row, align=uiconst.CENTERTOP)
        self.logoffCb = RadioButton(parent=cbCont, name='logoffCb', align=uiconst.TOPLEFT, wrapLabel=False, checked=True, text=localization.GetByLabel('UI/Inflight/SafeLogoffLogOutCb'), callback=self.OnCheckboxChange, groupname='logoffCb')
        self.quitCb = RadioButton(parent=cbCont, name='quitCb', align=uiconst.TOPLEFT, wrapLabel=False, top=32, checked=False, text=localization.GetByLabel('UI/Inflight/SafeLogoffQuitGameCb'), callback=self.OnCheckboxChange, groupname='logoffCb')
        self.UpdateLogoffTime()
        uthread.new(self.UpdateLogoffTime_Thread)
        self.mainGrid.RefreshGridLayout()
        self.RefreshHeight()
        MenuUnderlay(bgParent=self)

    def OnCheckboxChange(self, quitGameCheckbox):
        isQuitting = self.quitCb.GetValue()
        self.quitting = isQuitting
        if isQuitting:
            captionPath = 'UI/Inflight/SafeExitTimerCaption'
            hintPath = 'UI/Inflight/SafeExitTimerHint'
        else:
            captionPath = 'UI/Inflight/SafeLogoffTimerCaption'
            hintPath = 'UI/Inflight/SafeLogoffTimerHint'
        self.caption.text = '<center>%s</center>' % localization.GetByLabel(captionPath)
        self.SetHint(localization.GetByLabel(hintPath))

    def UpdateLogoffTime(self):
        timeLeft = self.logoffTime - blue.os.GetSimTime()
        timeLeft += const.SEC
        self.timer.text = '%.1f' % max(0.1, timeLeft / float(const.SEC))
        self.RefreshHeight()
        if self.cleanedHouse is False and self.quitting and timeLeft < 3 * const.SEC:
            self.cleanedHouse = True
            sm.ChainEvent('ProcessShutdown')

    def RefreshHeight(self):
        contentHeight = self.buttonCont.height + self.buttonCont.top + self.mainGrid.height + 6
        if contentHeight > self.height:
            self.height = contentHeight

    def UpdateLogoffTime_Thread(self):
        self.countingDown = True
        while self.countingDown:
            self.UpdateLogoffTime()
            blue.pyos.synchro.SleepSim(50)

    def AbortLogoff(self, *args):
        self.countingDown = False
        uthread.new(self.AbortLogoff_Thread)

    def AbortLogoff_Thread(self):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=0.85, duration=0.1)
        blue.pyos.synchro.SleepSim(1000)
        uicore.animations.FadeOut(self, duration=0.5, callback=self.Close)

    def AbortSafeLogoff(self, *args):
        shipAccess = sm.GetService('gameui').GetShipAccess()
        shipAccess.AbortSafeLogoff()
        self.AbortLogoff()

    def SetTimerCompleted(self):
        self.timer.SetText('0.0')
        self.timer.SetTextColor(Color.GREEN)
        self.countingDown = False

    def OnClose(self, *args):
        self.countingDown = False
