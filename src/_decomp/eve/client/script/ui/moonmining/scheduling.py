#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\scheduling.py
import carbonui.const as uiconst
import inventorycommon.const as invConst
import uthread
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.moonmining import COLOR_IN_PROGRESS, COLOR_READY, COLOR_STOPPED, GetExtractionStage, STAGE_IN_PROGRESS, STAGE_READY, GetTextColor, GetColorAndStatusTextForExtraction, STAGE_STOPPED
from eve.client.script.ui.moonmining.inProgressCont import InProgressCont
from eve.client.script.ui.moonmining.planningCont import PlanningCont
from eve.client.script.ui.moonmining.schedulingController import SchedulingController
from eve.common.lib.appConst import corpRoleStationManager
from eveservices.scheduling import GetSchedulingService
from localization import GetByLabel
import blue
from utillib import KeyVal
import locks

class SchedulingWindow(Window):
    __guid__ = 'SchedulingWindow'
    __notifyevents__ = ['OnSessionChanged',
     'OnMoonExtractionUpdate',
     'OnItemChange',
     'OnMiningLaserFiredLocal',
     'OnMiningLaserFiredFailedLocal']
    default_width = 600
    default_height = 525
    default_windowID = 'mooonminingScheduling'
    default_captionLabelPath = 'UI/Moonmining/MoonMiningSchedulingHeader'
    default_descriptionLabelPath = 'Tooltips/Neocom/MoonMiningScheduling_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/moonDrillScheduler.png'
    default_minSize = [default_width, default_height]

    def ApplyAttributes(self, attributes):
        self.uiUpdateThread = None
        self.gmBtnCont = None
        self.currentBtnStage = None
        self.mainAreaContent = None
        self.calendarEventPending = False
        Window.ApplyAttributes(self, attributes)
        self.schedulingSvc = sm.GetService('scheduling')
        self.countdownThread = None
        self.outputContsByTypeID = {}
        self.schedulingController = SchedulingController(self.schedulingSvc.GetFuelExpiryTime())
        self.structureID = attributes.structureID
        self.moonID = attributes.moonID
        self.extraction = attributes.extraction
        self.structureOwnerID = attributes.structureOwnerID
        self.eventID = attributes.eventID
        padding = 10
        self.topCont = Container(name='topCont', parent=self.sr.main, height=128, align=uiconst.TOTOP, padding=(padding,
         8,
         padding,
         0))
        self.bottomCont = Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOBOTTOM, height=48)
        self.mainAreaCont = Container(name='mainAreaCont', parent=self.sr.main, align=uiconst.TOALL, padLeft=padding, padRight=padding, padBottom=2)
        self.BuildTop()
        self.BuildBottom()
        self.RefreshUI(resourceComposition={})
        uthread.new(self.RefreshUI)
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            self.AddGMButtons()
        sm.RegisterNotify(self)

    def RefreshUI(self, resourceComposition = None):
        with locks.TempLock('RefreshUI'):
            if self.destroyed:
                return
            if resourceComposition is None:
                resourceComposition = self.schedulingSvc.GetMoonResourcesForStructure()
            c = self.MakeMainArea(resourceComposition)
            self.LoadTop()
            self.UpdateButtons()
            if self.uiUpdateThread:
                self.uiUpdateThread.KillTimer()
            self.UpdateUIForStatus_thread()
            self.uiUpdateThread = AutoTimer(3000, self.UpdateUIForStatus_thread)
            if not self.stacked:
                self.height = 330 + c.outputPanel.GetOutputHeight()
            self.ShowOrHideGMButtons()

    def ShowOrHideGMButtons(self):
        if not self.gmBtnCont:
            return
        if self.extraction:
            self.gmBtnCont.display = True
        else:
            self.gmBtnCont.display = False

    def OnMoonExtractionUpdate(self, extraction):
        if extraction is None:
            self.eventID = None
        elif self.eventID is None:
            self.calendarEventPending = True
            uthread.new(self._DelayedCalendarUpdate)
        self.extraction = extraction
        self.UpdateUiOnEvent()

    def _DelayedCalendarUpdate(self):
        try:
            blue.synchro.Sleep(1000)
            self.eventID, _ = self.schedulingSvc.GetExtractionAndEventIDFromStructureID()
            self.calendarEventPending = False
            self.UpdateButtons()
        finally:
            self.calendarEventPending = False

    def UpdateUiOnEvent(self):
        self.RefreshUI()
        self.UpdateButtons()
        if self.mainAreaContent:
            self.mainAreaContent.UpdateUI()

    def OnMiningLaserFiredLocal(self):
        self.UpdateUiOnEvent()

    def OnMiningLaserFiredFailedLocal(self):
        self.UpdateUiOnEvent()

    def MakeMainArea(self, resourceComposition):
        self.mainAreaCont.Flush()
        if self.extraction:
            c = InProgressCont(parent=self.mainAreaCont, extraction=self.extraction, moonMaterialInfo=resourceComposition)
        else:
            c = PlanningCont(parent=self.mainAreaCont, schedulingController=self.schedulingController, structureID=self.structureID, moonMaterialInfo=resourceComposition)
        self.mainAreaContent = c
        return c

    def BuildBottom(self):
        self.btnGrid = ContainerAutoSize(parent=self.bottomCont, state=uiconst.UI_PICKCHILDREN, align=uiconst.BOTTOMRIGHT, left=6, top=10, alignMode=uiconst.TORIGHT, height=32)
        self.stopDrillBtn = Button(parent=self.btnGrid, align=uiconst.TORIGHT, left=6, label=GetByLabel('UI/Moonmining/StopDrill'), func=self.StopDrill, color=COLOR_IN_PROGRESS[:3] + (0.5,), texturePath='res:/UI/Texture/classes/Moonmining/warning.png', iconSize=20)
        self.startBtn = Button(parent=self.btnGrid, align=uiconst.TORIGHT, left=6, label=GetByLabel('UI/Moonmining/StartExtraction'), func=self.StartExtraction, color=COLOR_STOPPED[:3] + (0.5,))
        self.fireBtn = Button(parent=self.btnGrid, align=uiconst.TORIGHT, left=6, label=GetByLabel('UI/Moonmining/FireLaser'), func=self.FireLaser, color=COLOR_READY[:3] + (0.5,))
        self.stopDrillBtn.width = self.fireBtn.width = max(self.stopDrillBtn.width, self.startBtn.width, self.fireBtn.width)
        self.btnGrid.height = max(self.stopDrillBtn.height, self.startBtn.height, self.fireBtn.height)
        self.stopDrillBtn.display = self.fireBtn.display = False
        self.addToCalendarCb = Checkbox(name='calendarCB', parent=self.bottomCont, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Moonmining/AddToCalendar'), checked=True, width=200, left=10)
        self.addToCalendarCb.display = False
        self.calendarEventStatusLabel = EveLabelMedium(name='calendarLabel', parent=self.bottomCont, align=uiconst.CENTERLEFT, left=10)

    def FireLaser(self, *args):
        eve.Message('CustomNotify', {'notify': GetByLabel('Notifications/NotificationNames/MoonminingLaserFired')})
        self.schedulingSvc.FireLaser()

    def StopDrill(self, *args):
        self.schedulingSvc.CancelExtraction()

    def StartExtraction(self, *args):
        endtime = self.schedulingController.GetCurrentTime()
        addToCalendar = self.addToCalendarCb.GetValue()
        started = GetSchedulingService().StartMoonminingEvent(self.structureID, self.structureOwnerID, endtime, addToCalendar)
        if started:
            self.startBtn.Disable()

    def BuildTop(self):
        self.moonIcon = Icon(parent=self.topCont, align=uiconst.TOPLEFT, pos=(0, 0, 128, 128))
        self.moonIcon.GetDragData = self.GetMoonDragData
        self.moonIcon.MakeDragObject()
        textCont = Container(name='textCont', parent=self.topCont, align=uiconst.TOALL, padLeft=140, height=64)
        self.structureNameLabel = Label(name='structureNameLabel', parent=textCont, align=uiconst.TOTOP, text='', state=uiconst.UI_NORMAL, fontsize=16)
        self.moonNameLabel = EveLabelMedium(name='moonNameLabel', parent=textCont, align=uiconst.TOTOP, text='', state=uiconst.UI_NORMAL)
        layoutGrid = LayoutGrid(name='layoutGrid', parent=textCont, columns=3, align=uiconst.TOTOP, top=12)
        self.drillStatusHederText = EveLabelMedium(name='headerStatusText', parent=layoutGrid, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Moonmining/DrillStatus'))
        self.drillStatusText = EveLabelMedium(name='headerStatusText', parent=layoutGrid, align=uiconst.CENTERLEFT, text='', padLeft=4)
        self.helpIcon = MoreInfoIcon(parent=layoutGrid, align=uiconst.CENTERRIGHT, hint='', padLeft=4)
        self.LoadTop()

    def GetMoonDragData(self):
        fakeNode = KeyVal()
        fakeNode.__guid__ = 'xtriui.ListSurroundingsBtn'
        fakeNode.itemID = self.moonID
        fakeNode.typeID = invConst.typeMoon
        fakeNode.label = cfg.evelocations.Get(self.moonID).name
        return [fakeNode]

    def LoadTop(self):
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(self.structureID)
        self.structureNameLabel.text = GetShowInfoLink(structureInfo.typeID, structureInfo.itemName, structureInfo.structureID)
        moonInfo = cfg.evelocations.Get(self.moonID)
        self.moonNameLabel.text = GetShowInfoLink(invConst.typeMoon, moonInfo.name, moonInfo.locationID)
        self.moonIcon.LoadIconByTypeID(const.typeMoon, self.moonID, size=128)
        headerText, headerHelp, headerColor = GetColorAndStatusTextForExtraction(self.extraction)
        self.drillStatusText.text = headerText.upper()
        textColor = GetTextColor(headerColor)
        self.drillStatusText.SetRGBA(*textColor)
        self.helpIcon.hint = headerHelp

    def OnSessionChanged(self, isRemote, sess, change):
        if not session.structureid or session.shipid != session.structureid:
            self.Close()

    def UpdateButtons(self):
        self.SetElementDisplayAndState([self.fireBtn,
         self.stopDrillBtn,
         self.startBtn,
         self.addToCalendarCb,
         self.calendarEventStatusLabel], False)
        elementsToShow = []
        self.currentBtnStage = GetExtractionStage(self.extraction)
        if self.currentBtnStage == STAGE_READY:
            elementsToShow.append(self.fireBtn)
        elif self.currentBtnStage == STAGE_STOPPED:
            elementsToShow.append(self.startBtn)
            elementsToShow.append(self.addToCalendarCb)
        self.SetElementDisplayAndState(elementsToShow, True)
        if self.currentBtnStage == STAGE_IN_PROGRESS:
            self.stopDrillBtn.display = True
            if not session.corprole & corpRoleStationManager or self.structureOwnerID != session.corpid:
                self.stopDrillBtn.Disable()
                self.stopDrillBtn.hint = GetByLabel('UI/Moonmining/StopDrillBtnHint')
            else:
                self.stopDrillBtn.Enable()
                self.stopDrillBtn.hint = ''
            if self.calendarEventPending:
                calendarText = ''
            elif self.eventID > 0:
                calendarText = GetByLabel('UI/Moonmining/CalendarEventSet')
            else:
                calendarText = GetByLabel('UI/Moonmining/CalendarEventNotSet')
            self.calendarEventStatusLabel.text = calendarText
            self.calendarEventStatusLabel.display = True

    def SetElementDisplayAndState(self, btnList, doShow):
        for each in btnList:
            each.display = doShow
            if doShow:
                each.Enable()
            else:
                each.Disable()

    def UpdateUIForStatus_thread(self):
        if self.destroyed:
            self.uiUpdateThread = None
        currentStage = GetExtractionStage(self.extraction)
        if currentStage != self.currentBtnStage:
            self.UpdateButtons()

    def Close(self, *args, **kwds):
        self.countdownThread = None
        Window.Close(self, *args, **kwds)

    def AddGMButtons(self):
        if not getattr(self, 'gmBtnCont', None) or self.gmBtnCont.destroyed:
            self.gmBtnCont = Container(name='gmBtnCont', parent=self.bottomCont, align=uiconst.TOBOTTOM_NOPUSH, height=30, top=10)
        midwayBtn = Button(parent=self.gmBtnCont, label='GM:Set Chunk Midway', hint='Set extraction to mid-way between the start and stop movement positions', align=uiconst.BOTTOMLEFT, func=lambda x: sm.GetService('slash').SlashCmd('/extraction advance mid'), top=20, left=100)
        stopBtn = Button(parent=self.gmBtnCont, label='GM:Stop Chunk', hint="Set extraction to the stop movement position. Chunk WILL NOT be available for fracture until it reaches the 'ready' phase", align=uiconst.BOTTOMLEFT, func=lambda x: sm.GetService('slash').SlashCmd('/extraction advance stop'), left=midwayBtn.left)
        readyBtn = Button(parent=self.gmBtnCont, left=midwayBtn.left + midwayBtn.width + 20, label='GM:Set Chunk Ready', hint='Set extraction to the stop movement position. Chunk WILL be available for fracture immediately.', align=uiconst.BOTTOMLEFT, func=lambda x: sm.GetService('slash').SlashCmd('/extraction advance ready'), top=20)
        decayBtn = Button(parent=self.gmBtnCont, left=readyBtn.left, label='GM:Set to Decay point', hint='Set extraction to the point at which the chunk is about to naturally decay.', align=uiconst.BOTTOMLEFT, func=lambda x: sm.GetService('slash').SlashCmd('/extraction advance decay'))

    def OnItemChange(self, item, change, location):
        oldLocationID = change.get(const.ixLocationID, None)
        if session.structureid not in (oldLocationID, item.locationID):
            return
        oldFlag = change.get(const.ixFlag, None)
        if const.flagStructureFuel not in (oldFlag, item.flagID):
            return
        self.UpdateFuelExpiry()

    def UpdateFuelExpiry(self):
        fuelExpiryTime = self.schedulingSvc.GetFuelExpiryTime()
        self.schedulingController.SetFuelExpiryTime(fuelExpiryTime)
