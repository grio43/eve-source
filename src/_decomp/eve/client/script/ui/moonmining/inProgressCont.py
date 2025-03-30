#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\inProgressCont.py
import gametime
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.common.lib.appConst import SEC
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.moonmining import DAY_NAME_TEXT, COLOR_IN_PROGRESS, COLOR_READY, GetExtractionStage, STAGE_READY, STAGE_IN_PROGRESS, STAGE_FRACTURING, COLOR_FRACTURE
import blue
import carbonui.const as uiconst
from eve.client.script.ui.moonmining.outputCont import SchedulingOutputPanel
from eve.client.script.ui.moonmining.progressBar import ProgressBar
from eveservices.scheduling import GetSchedulingService
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
from moonmining.const import FRACTURE_TOTAL_DURATION
import mathext

class InProgressCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.extraction = attributes.extraction
        self.moonMaterialInfo = attributes.moonMaterialInfo
        self.remainingUpdateThread = None
        self.centerCont = Container(name='centerCont', parent=self, height=90, align=uiconst.TOTOP)
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOALL)
        self.BuildBottom()
        self.BuildCenter()

    def GetColorAndStrings(self, currentStage):
        if currentStage == STAGE_READY:
            return (COLOR_READY, GetByLabel('UI/Moonmining/LaserReadyToFire').upper())
        elif currentStage == STAGE_FRACTURING:
            return (COLOR_FRACTURE, GetByLabel('UI/Moonmining/ExtractionFracturingStatus').upper())
        else:
            year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(self.extraction.chunkAvailableTime)
            dayName = DAY_NAME_TEXT[wd]
            readyText = GetByLabel('UI/Moonmining/ExtractionScheduled', weekday=dayName[:3], timestamp=FmtDate(self.extraction.chunkAvailableTime, fmt='ss'))
            return (COLOR_IN_PROGRESS, readyText)

    def BuildCenter(self):
        EveLabelMedium(parent=self.centerCont, text=GetByLabel('UI/Moonmining/Schedule'), align=uiconst.TOTOP)
        LineThemeColored(parent=self.centerCont, align=uiconst.TOTOP)
        fontSize = 14
        self.aboveCont = ContainerAutoSize(name='aboveCont', parent=self.centerCont, height=50, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=12)
        self.traversalHelpIcon = MoreInfoIcon(parent=self.aboveCont, align=uiconst.CENTERRIGHT, hint='', padLeft=4)
        self.traversalHelpIcon.LoadTooltipPanel = self.LoadTraversalInfoTooltipPanel
        self.remainingLabel = Label(parent=self.aboveCont, text='', align=uiconst.TOPRIGHT, fontsize=fontSize, left=20)
        self.scheduledAtLabel = Label(parent=self.aboveCont, text='', align=uiconst.TOTOP, fontsize=fontSize)
        mainCenter = Container(name='mainCenter', parent=self.centerCont, align=uiconst.TOALL, padTop=8)
        remainingText, percentage = self.GetRemainingTextAndPercentageDone(GetExtractionStage(self.extraction))
        self.progressBar = ProgressBar(parent=mainCenter, color=COLOR_IN_PROGRESS, percentage=percentage, barHeight=24)
        self.UpdateRemainingTime()
        self.remainingUpdateThread = AutoTimer(400, self.UpdateRemainingTime_thread)

    def BuildBottom(self):
        text = GetByLabel('UI/Moonmining/ProjectedOutput')
        self.outputPanel = SchedulingOutputPanel(parent=self.bottomCont, moonMaterialInfo=self.moonMaterialInfo, top=8, outputHeaderText=text)
        numSec = float(self.extraction.chunkAvailableTime - self.extraction.startMoveTime) / SEC
        self.outputPanel.SetEstimation(numSec, self.extraction.yieldMultiplier)

    def UpdateRemainingTime_thread(self):
        if self.destroyed:
            self.remainingUpdateThread = None
            return
        self.UpdateRemainingTime()

    def UpdateRemainingTime(self):
        currentStage = GetExtractionStage(self.extraction)
        color, text = self.GetColorAndStrings(currentStage)
        self.progressBar.ColorElement(color)
        turnOnArrows = currentStage == STAGE_IN_PROGRESS
        isLastStage = currentStage == STAGE_FRACTURING
        if currentStage == STAGE_IN_PROGRESS:
            self.traversalHelpIcon.display = True
            self.remainingLabel.left = 20
        else:
            self.traversalHelpIcon.display = False
            self.remainingLabel.left = 0
        self.progressBar.ChangeAnimationState(turnOnArrows, isLastStage)
        self.progressBar.ChangeCenterMarkerDisplay(isLastStage)
        self.scheduledAtLabel.text = text
        remainingText, percentage = self.GetRemainingTextAndPercentageDone(currentStage)
        self.progressBar.UpdateProgress(percentage)
        self.remainingLabel.text = remainingText

    def GetRemainingTextAndPercentageDone(self, currentStage):
        percentage = 1.0
        if currentStage == STAGE_READY:
            diff = max(0, self.extraction.naturalDecayTime - gametime.GetWallclockTime())
            remainingText = GetByLabel('UI/Moonmining/AutomaticFracture', countdownText=FormatTimeIntervalShortWritten(diff, showFrom='day', showTo='minute'))
        elif currentStage == STAGE_IN_PROGRESS:
            totalTime = self.extraction.chunkAvailableTime - self.extraction.startMoveTime
            diff = max(0, self.extraction.chunkAvailableTime - gametime.GetWallclockTime())
            percentage = 1.0 - mathext.clamp(diff / float(totalTime), 0, 1.0)
            remainingText = GetByLabel('UI/Moonmining/RemainingTime', countdownText=FormatTimeIntervalShortWritten(diff, showFrom='day', showTo='minute'))
        elif currentStage == STAGE_FRACTURING:
            laserFiredTimestamp = GetSchedulingService().GetLaserFiredTimestamp() or 0
            diff = long(max(0, laserFiredTimestamp + FRACTURE_TOTAL_DURATION * SEC - gametime.GetWallclockTime()))
            remainingText = GetByLabel('UI/Moonmining/RemainingTime', countdownText=FormatTimeIntervalShortWritten(diff, showFrom='minute', showTo='second'))
        return (remainingText, percentage)

    def UpdateUI(self):
        self.UpdateRemainingTime()

    def LoadTraversalInfoTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        fractureDelay = long(self.extraction.naturalDecayTime - self.extraction.chunkAvailableTime)
        text = GetByLabel('UI/Moonmining/AutomaticFractureTooltip', fractureDelay=fractureDelay)
        tooltipPanel.AddLabelMedium(text=text, wrapWidth=200)

    def Close(self):
        self.remainingUpdateThread = None
        Container.Close(self)
