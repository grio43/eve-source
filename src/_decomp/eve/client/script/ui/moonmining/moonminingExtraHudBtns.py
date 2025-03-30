#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\moonminingExtraHudBtns.py
import evetypes
import gametime
import itertoolsext
import structures
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.common.lib.appConst import SEC, ixFlag
from dogma.const import attributeIsOnline
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.inflight.shipHud.leftSideButton import LeftSideButton
from eve.client.script.ui.inflight.shipModuleButton.extraBtnShipSlot import ExtraBtnShipSlot
from eve.client.script.ui.moonmining import GetColorAndStatusTextForExtraction, GetExtractionStage, GetTextColor, STAGE_FRACTURING, STAGE_IN_PROGRESS, STAGE_READY, STAGE_STOPPED
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eveservices.scheduling import GetSchedulingService
from inventorycommon.const import serviceSlotFlags, typeStandupMoonDrill
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
from moonmining.const import FRACTURE_TOTAL_DURATION
from carbonui.uicore import uicore
import mathext
GLOW_COLOR_IN_PROGRESS = (1.0, 0.13, 0.0, 0.73)
GLOW_COLOR_FRACTURE = (0.24, 0.67, 0.16, 0.75)

class MoonminingExtraHudBtns(Container):
    default_name = 'moonminingExtraHudBtns'
    __notifyevents__ = ['OnDogmaAttributeChanged', 'OnItemChange']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.extraBtns = []
        sm.RegisterNotify(self)

    def UpdateButtonsForHull(self):
        self.RemoveBtns()
        structureID = session.structureid
        if structureID:
            self.AddBtns(structureID)

    def AddBtns(self, structureID):
        self.fireLaserBtn = MoonDrillCont(structureID=structureID, parent=self, align=uiconst.CENTERRIGHT, left=-4, moonDrillTypeID=typeStandupMoonDrill)
        self.fireLaserBtn.Disable()
        self.fireLaserBtn.display = False
        self.accessSchedule = SchedulerHudBtn(structureID=structureID, parent=self, align=uiconst.CENTERLEFT, top=44, left=4)
        self.accessSchedule.Disable()
        self.accessSchedule.display = False
        self.extraBtns.append(self.fireLaserBtn)
        self.extraBtns.append(self.accessSchedule)
        uthread.new(self.UpdateBtns, structureID)

    def UpdateBtns(self, structureID):
        self.fireLaserBtn.display = False
        self.accessSchedule.display = False
        if self.AreBtnsAvailable(structureID):
            self.fireLaserBtn.Enable()
            self.fireLaserBtn.display = True
            self.accessSchedule.Enable()
            self.accessSchedule.display = True
        _, extraction = GetSchedulingService().GetExtractionAndEventIDFromStructureID()
        self.fireLaserBtn.SetExtraction(extraction)

    def RemoveBtns(self):
        for eachBtn in self.extraBtns:
            eachBtn.Close()

        self.extraBtns = []

    def AreBtnsAvailable(self, structureID):
        if session.structureid != structureID:
            return False
        if not sm.GetService('structureSettings').CharacterHasSetting(structureID, structures.SETTING_DEFENSE_CAN_CONTROL_STRUCTURE):
            return False
        clientDogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        itemsFittedToShip = clientDogmaLM.GetFittedItemsToShip()
        moonDrill = itertoolsext.first_or_default(itemsFittedToShip.values(), predicate=lambda x: x.typeID == typeStandupMoonDrill, default=None)
        if not moonDrill:
            return False
        return bool(moonDrill.IsOnline())

    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if attributeID != attributeIsOnline or session.structureid is None:
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        item = dogmaLocation.SafeGetDogmaItem(itemID)
        if item and item.typeID == typeStandupMoonDrill:
            self.UpdateButtonsForHull()

    def OnItemChange(self, item, change, location):
        if item.typeID != typeStandupMoonDrill:
            return
        if ixFlag in change and change[ixFlag] in serviceSlotFlags:
            self.UpdateButtonsForHull()


class MoonDrillCont(Container):
    __notifyevents__ = ['OnMoonExtractionUpdate', 'OnMiningLaserFiredLocal', 'OnMiningLaserFiredFailedLocal']
    default_width = 64
    default_height = 64
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        self.rampThread = None
        self.tooltipThread = None
        Container.ApplyAttributes(self, attributes)
        self.currentExtraction = attributes.extraction
        self.structureID = attributes.structureID
        self.moonDrillTypeID = attributes.moonDrillTypeID or 45009
        self.moonDrillBtn = ExtraBtnShipSlot(name='moonDrillBtn', parent=self, func=self.OnBtnClickedFunction)
        self.moonDrillBtn.LoadTooltipPanel = self.LoadTooltipPanel
        self.SetStage()
        sm.RegisterNotify(self)

    def SetStage(self):
        stageID = GetExtractionStage(self.currentExtraction)
        texturePath = None
        self.rampThread = None
        self.moonDrillBtn.SetRampValue(0.0)
        self.moonDrillBtn.DisableBtn()
        glowColor = None
        if stageID == STAGE_STOPPED:
            texturePath = 'res:/UI/Texture/classes/Moonmining/iconStopped.png'
            self.moonDrillBtn.EnableBtn()
        elif stageID == STAGE_IN_PROGRESS:
            glowColor = GLOW_COLOR_IN_PROGRESS
            texturePath = 'res:/UI/Texture/classes/Moonmining/iconTransit.png'
            self.StartUpdateThreadForInProgress()
        elif stageID == STAGE_FRACTURING:
            glowColor = GLOW_COLOR_FRACTURE
            texturePath = 'res:/UI/Texture/classes/Moonmining/iconFracture.png'
            self.StartUpdateThreadForLaserFired()
        elif stageID == STAGE_READY:
            self.moonDrillBtn.EnableBtn()
            texturePath = 'res:/UI/Texture/classes/Moonmining/iconReady.png'
        self.moonDrillBtn.SetButtonIcon(texturePath)
        if glowColor:
            self.moonDrillBtn.BlinkGlow(glowColor)
        else:
            self.moonDrillBtn.StopBlinkGlow()

    def OnBtnClickedFunction(self):
        stageID = GetExtractionStage(self.currentExtraction)
        schedulingSvc = GetSchedulingService()
        if stageID == STAGE_READY:
            schedulingSvc.FireLaser()
        elif stageID == STAGE_STOPPED:
            schedulingSvc.OpenSchedulingWndForStructure(self.structureID)

    def StartUpdateThreadForLaserFired(self):
        laserFiredTimestamp = GetSchedulingService().GetLaserFiredTimestamp()
        endTime = laserFiredTimestamp + FRACTURE_TOTAL_DURATION * SEC
        self.UpdateRampThread(laserFiredTimestamp, endTime)
        self.rampThread = AutoTimer(50, self.UpdateRampThread, laserFiredTimestamp, endTime)

    def StartUpdateThreadForInProgress(self):
        self.UpdateRampThread(self.currentExtraction.startMoveTime, self.currentExtraction.chunkAvailableTime)
        self.rampThread = AutoTimer(60000, self.UpdateRampThread, self.currentExtraction.startMoveTime, self.currentExtraction.chunkAvailableTime)

    def GetPercentageDone(self, startTime, endTime):
        totalTime = endTime - startTime
        diff = max(0, endTime - gametime.GetWallclockTime())
        percentage = 1.0 - mathext.clamp(diff / float(totalTime), 0, 1.0)
        return percentage

    def OnMoonExtractionUpdate(self, extraction):
        self.SetExtraction(extraction)

    def OnMiningLaserFiredFailedLocal(self):
        self.SetStage()

    def OnMiningLaserFiredLocal(self):
        self.SetStage()

    def SetExtraction(self, extraction):
        self.currentExtraction = extraction
        self.SetStage()

    def UpdateRampThread(self, startTime, endTime):
        if self.destroyed:
            self.rampThread = False
        percentage = self.GetPercentageDone(startTime, endTime)
        self.moonDrillBtn.SetRampValue(percentage)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.columns = 2
        tooltipPanel.margin = (4, 4, 4, 4)
        tooltipPanel.cellPadding = 0
        tooltipPanel.cellSpacing = 0
        self._LoadTooltipPanel_thread(tooltipPanel)
        self.tooltipThread = AutoTimer(500, self._LoadTooltipPanel_thread, tooltipPanel)

    def _LoadTooltipPanel_thread(self, tooltipPanel):
        currentMouseOver = uicore.uilib.mouseOver
        if self.destroyed or currentMouseOver != self and not currentMouseOver.IsUnder(self):
            self.tooltipThread = None
            return
        tooltipPanel.Flush()
        iconCont = self.GetIconCont()
        tooltipPanel.AddCell(iconCont, cellPadding=2)
        typeName = evetypes.GetName(self.moonDrillTypeID)
        tooltipPanel.AddLabelMedium(text=typeName, align=uiconst.CENTERLEFT, cellPadding=(4, 2, 4, 2), bold=True)
        text, _, color = GetColorAndStatusTextForExtraction(self.currentExtraction)
        textColor = GetTextColor(color)
        tooltipPanel.AddSpacer(height=0, width=0)
        labelObj = tooltipPanel.AddLabelMedium(text=text.upper(), align=uiconst.CENTERLEFT, cellPadding=(4, 2, 4, 2))
        labelObj.SetRGBA(*textColor)
        currentStage = GetExtractionStage(self.currentExtraction)
        if currentStage == STAGE_IN_PROGRESS:
            totalTime = self.currentExtraction.chunkAvailableTime - self.currentExtraction.startMoveTime
            diff = max(0, self.currentExtraction.chunkAvailableTime - gametime.GetWallclockTime())
            if diff > 0:
                tooltipPanel.AddSpacer(height=0, width=0)
                remainingText = GetByLabel('UI/Moonmining/RemainingTime', countdownText=FormatTimeIntervalShortWritten(diff, showFrom='day', showTo='minute'))
                labelObj = tooltipPanel.AddLabelMedium(text=remainingText, align=uiconst.CENTERLEFT, cellPadding=(4, 2, 4, 2))
                labelObj.SetRGBA(*textColor)

    def GetIconCont(self):
        iconSize = 26
        iconCont = Container(pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER)
        iconObj = Icon(parent=iconCont, pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.TOPLEFT, ignoreSize=True)
        iconObj.LoadIconByTypeID(self.moonDrillTypeID, size=iconSize, ignoreSize=True)
        techIcon = Icon(parent=iconCont, width=16, height=16, align=uiconst.TOPLEFT, idx=0, top=0)
        GetTechLevelIcon(techIcon, typeID=self.moonDrillTypeID)
        return iconCont

    def Close(self):
        self.rampThread = None
        self.tooltipThread = None
        Container.Close(self)


class SchedulerHudBtn(LeftSideButton):
    default_name = 'shedulerHudBtn'
    default_texturePath = 'res:/UI/Texture/classes/Moonmining/iconSchedulerSmall.png'
    cmdName = 'OpenCargoHoldOfActiveShip'
    cmdDescription_override = 'Tooltips/Hud/CargoHoldStructure_description'

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        self.structureID = attributes.structureID

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        GetSchedulingService().OpenSchedulingWndForStructure(self.structureID)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Moonmining/MoonMiningSchedulingHeader'))
