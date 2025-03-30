#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovDashboard\cynoJammerIcon.py
import gametime
import uthread2
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import LineThemeColored
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
from carbonui.uicore import uicore
JAMMER_STATUS_PENDING = -1
JAMMER_STATUS_OFF = 0
JAMMER_STATUS_ON = 1
NOT_ACTIVE_ALPHA = 0.25

class CynoJammerIcon(Container):
    default_align = uiconst.CENTER
    default_iconSize = 32
    default_height = 40
    default_width = 40
    default_state = uiconst.UI_NORMAL
    default_useBackground = True
    texturePath = 'res:/UI/Texture/classes/Sov/effectCyno.png'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onlineSimTime = None
        self.updateThread = None
        self.tooltipThread = None
        if attributes.get('useBackground', True):
            backgroundShape = Sprite(parent=self, texturePath='res:/ui/Texture/classes/Sov/structureIconBackground.png', color=(0, 0, 0, 0.3), align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=-1)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.jammerSprite = Sprite(name='cynoJammer', parent=self, texturePath=self.texturePath, align=uiconst.CENTER, pos=(0,
         0,
         self.iconSize,
         self.iconSize), opacity=0.25, state=uiconst.UI_DISABLED)
        uthread2.start_tasklet(self._UpdateFromServer)

    def _UpdateFromServer(self):
        self.UpdateIconState(sm.RemoteSvc('beyonce').GetCynoJammerState())

    def UpdateIconState(self, onlineSimTime):
        if self.updateThread is not None:
            self.updateThread.kill()
            self.updateThread = None
        self.onlineSimTime = onlineSimTime
        self._UpdateIconState()
        if self.onlineSimTime is not None:
            delay = self.GetUpdateDelayInSec()
            if delay > 0:
                self.updateThread = uthread2.call_after_simtime_delay(self._UpdateIconState, delay)

    def GetUpdateDelayInSec(self):
        delay = gametime.GetSecondsUntilSimTime(self.onlineSimTime)
        if delay > 0:
            return delay + 0.5

    def _UpdateIconState(self):
        status = self.GetJamStatus()
        if status == JAMMER_STATUS_PENDING:
            uicore.animations.FadeTo(self.jammerSprite, NOT_ACTIVE_ALPHA, 1.0, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        else:
            uicore.animations.StopAllAnimations(self.jammerSprite)
            if status == JAMMER_STATUS_ON:
                uicore.animations.FadeTo(self.jammerSprite, self.jammerSprite.opacity, 1.0, duration=1.0, curveType=uiconst.ANIM_OVERSHOT4)
            else:
                uicore.animations.FadeTo(self.jammerSprite, self.jammerSprite.opacity, NOT_ACTIVE_ALPHA, duration=1.0)
        self.jammingStatus = status

    def GetJamStatus(self):
        if self.onlineSimTime is None:
            return JAMMER_STATUS_OFF
        inFuture = IsTimeInFuture(self.onlineSimTime)
        if self.onlineSimTime == 0 or not inFuture:
            status = JAMMER_STATUS_ON
        else:
            status = JAMMER_STATUS_PENDING
        return status

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_2

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.tooltipThread is not None:
            self.tooltipThread.kill()
            self.tooltipThread = None
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 2
        tooltipPanel.margin = 2
        tooltipPanel.cellPadding = 1
        self._LoadTooltipPanel(tooltipPanel)

    def _LoadTooltipPanel(self, tooltipPanel):
        tooltipPanel.Flush()
        if not self or self.destroyed or tooltipPanel.destroyed:
            return
        status = self.GetJamStatus()
        if status == JAMMER_STATUS_PENDING:
            return self.LoadTooltipPanelJamPending(tooltipPanel)
        elif status == JAMMER_STATUS_ON:
            return self.LoadTooltipPanelJammed(tooltipPanel)
        else:
            return self.LoadTooltipPanelNotJammed(tooltipPanel)

    def LoadTooltipPanelJamPending(self, tooltipPanel):
        icon = Sprite(width=48, height=48, state=uiconst.UI_DISABLED, texturePath=self.texturePath, opacity=NOT_ACTIVE_ALPHA)
        tooltipPanel.AddCell(icon)
        headerText = GetByLabel('UI/Neocom/JamPendingForSolarSystem')
        tooltipPanel.AddLabelLarge(text=headerText, width=150, bold=True, align=uiconst.CENTERLEFT)
        l = LineThemeColored(width=200, height=1, align=uiconst.CENTER, opacity=0.3)
        tooltipPanel.AddCell(l, colSpan=2, cellPadding=(1, 1, 1, 3))
        timeLabel = CountdownCynoLabel(align=uiconst.CENTER, onlineSimTime=self.onlineSimTime, width=190)
        tooltipPanel.AddCell(cellObject=timeLabel, colSpan=2)
        delay = self.GetUpdateDelayInSec()
        if delay > 0:
            self.tooltipThread = uthread2.call_after_simtime_delay(self._LoadTooltipPanel, delay, tooltipPanel)

    def LoadTooltipPanelJammed(self, tooltipPanel):
        icon = Sprite(width=48, height=48, state=uiconst.UI_DISABLED, texturePath=self.texturePath, opacity=NOT_ACTIVE_ALPHA)
        tooltipPanel.AddCell(icon)
        headerText = GetByLabel('UI/Neocom/SolarSystemIsJammed')
        tooltipPanel.AddLabelLarge(text=headerText, width=150, bold=True, align=uiconst.CENTERLEFT)
        self.AddDesc(tooltipPanel, 'UI/Neocom/SystemEffectCynoHint')

    def LoadTooltipPanelNotJammed(self, tooltipPanel, *args):
        icon = Sprite(width=48, height=48, state=uiconst.UI_DISABLED, texturePath=self.texturePath, opacity=NOT_ACTIVE_ALPHA)
        tooltipPanel.AddCell(icon)
        headerText = GetByLabel('UI/Neocom/SolarSystemIsNotJammed')
        tooltipPanel.AddLabelLarge(text=headerText, width=150, bold=True, align=uiconst.CENTERLEFT)
        self.AddDesc(tooltipPanel, 'UI/Neocom/NoSystemEffectCynoHint')

    def AddDesc(self, tooltipPanel, labelPath):
        l = LineThemeColored(width=200, height=1, align=uiconst.CENTER, opacity=0.3)
        tooltipPanel.AddCell(l, colSpan=2, cellPadding=(1, 1, 1, 3))
        text = '<center>%s</center>' % GetByLabel(labelPath)
        descLabel = EveLabelMedium(align=uiconst.CENTER, width=190, text=text)
        tooltipPanel.AddCell(cellObject=descLabel, colSpan=2)

    def Close(self):
        if self.tooltipThread is not None:
            self.tooltipThread.kill()
            self.tooltipThread = None
        if self.updateThread is not None:
            self.updateThread.kill()
            self.updateThread = None
        Container.Close(self)


class CountdownCynoLabel(EveLabelMedium):
    default_name = 'countdownCynoLabel'
    default_state = uiconst.UI_DISABLED
    DELAY_SEC = 0.5

    def ApplyAttributes(self, attributes):
        EveLabelMedium.ApplyAttributes(self, attributes)
        self.onlineSimTime = attributes.onlineSimTime
        uthread2.start_tasklet(self.UpdateTime_thread)

    def UpdateTime_thread(self):
        if self.destroyed:
            return
        if not self.parent or not self.parent.display or not self.display:
            return
        keepUdating = self.UpdateTime()
        if keepUdating:
            uthread2.sleep(self.DELAY_SEC)
            uthread2.start_tasklet(self.UpdateTime_thread)

    def UpdateTime(self):
        timeDiff = gametime.GetTimeDiff(gametime.GetSimTime(), self.onlineSimTime)
        if timeDiff > 0:
            text = GetByLabel('UI/Neocom/CynoJammerActivatingHint', timeLeft=FormatTimeIntervalShortWritten(timeDiff, showFrom='minute', showTo='second'))
        else:
            text = GetByLabel('UI/Neocom/JammerActive')
        self.text = '<center>%s</center>' % text
        return bool(timeDiff > 0)


def IsTimeInFuture(onlineSimTime):
    if onlineSimTime is None:
        return False
    timeDiff = gametime.GetTimeDiff(gametime.GetSimTime(), onlineSimTime)
    return bool(timeDiff > 0)
